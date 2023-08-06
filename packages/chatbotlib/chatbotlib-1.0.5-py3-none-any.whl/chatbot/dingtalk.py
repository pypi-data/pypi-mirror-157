import time
import hmac
import hashlib
import base64
import aiohttp

import requests
from requests.adapters import HTTPAdapter
from urllib.parse import quote_plus, urlencode


def request(url, method='GET', retry_times=5, *args, **kwargs):
    with requests.Session() as s:
        if retry_times:
            s.mount('https://', HTTPAdapter(pool_connections=1, max_retries=retry_times))
        response = s.request(
            url=url, method=method,
            *args, **kwargs
        )
    return response


class DingTalkBot:
    url = 'https://oapi.dingtalk.com/robot/send'

    def __init__(self, token, secret=None, auto_throttle=True):
        self.access_token = token
        self.secret = secret
        self.interval_set = {}
        # 是否自动处理钉钉限流问题
        self.auto_throttle = auto_throttle
        self.report_record = []
        self.wait_seconds = 61

    @staticmethod
    def get_signature(ts, s):
        secret_enc = s.encode('utf-8')
        string_to_sign = '{}\n{}'.format(ts, s)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        return quote_plus(base64.b64encode(hmac_code).decode('utf-8'))

    def not_allow_report(self, tag, interval):
        if tag and interval:
            ts = int(time.time())
            last_report_ts = self.interval_set.get(tag)
            if last_report_ts is None:
                self.interval_set[tag] = ts
                return
            if ts - last_report_ts < interval:
                return True
            else:
                self.interval_set[tag] = ts

    def wait(self):
        ts = time.time()
        if len(self.report_record) >= 20 and ts - self.report_record[0] < 60:
            sleep_time = self.wait_seconds - (ts - self.report_record[0])
            time.sleep(sleep_time)
            ts = time.time()
        self.report_record.append(ts)
        if len(self.report_record) > 20:
            self.report_record = self.report_record[1:]

    async def async_send(self, data, tag=None, interval=None):
        if self.not_allow_report(tag, interval) is True:
            return

        if self.auto_throttle is True:
            self.wait()

        timestamp = str(round(time.time() * 1000))
        params = {
            'access_token': self.access_token,
            'timestamp': timestamp,
        }
        if self.secret:
            sign = self.get_signature(timestamp, self.secret)
            params['sign'] = sign

        if self.access_token.startswith('https://'):
            u = self.access_token
            params.pop('access_token')
            sep = '&'
        else:
            sep = '?'
            u = self.url
        url = f'{u}{sep}{urlencode(params)}'
        async with aiohttp.ClientSession() as s:
            timeout = aiohttp.ClientTimeout(sock_read=20, sock_connect=10)
            async with s.request(
                    'POST',
                    url,
                    json=data,
                    timeout=timeout
            ) as response:
                if await self.async_check_response(response):
                    return await response.text()

    def send(self, data, tag=None, interval=None):
        if self.not_allow_report(tag, interval) is True:
            return

        if self.auto_throttle is True:
            self.wait()

        timestamp = str(round(time.time() * 1000))
        params = {
            'access_token': self.access_token,
            'timestamp': timestamp,
        }
        if self.secret:
            sign = self.get_signature(timestamp, self.secret)
            params['sign'] = sign

        if self.access_token.startswith('https://'):
            u = self.access_token
            params.pop('access_token')
            sep = '&'
        else:
            sep = '?'
            u = self.url
        url = f'{u}{sep}{urlencode(params)}'
        resp = request(method='POST', url=url, json=data, timeout=(10, 20))
        if self.check_response(resp):
            return resp.text

    async def async_send_text(self, text, phone=None, tag=None, interval=None):
        text_meta = {
            "text": {"content": text},
            "msgtype": "text"
        }

        if phone:
            at_all = False
            phones = None
            if phone == 'all':
                at_all = True
            else:
                phones = phone.split(',')

            at = {'isAtAll': at_all}
            if phones:
                at['atMobiles'] = phones
            text_meta['at'] = at

        return await self.async_send(text_meta, tag, interval)

    def send_text(self, text, phone=None, tag=None, interval=None):
        text_meta = {
            "text": {"content": text},
            "msgtype": "text"
        }

        if phone:
            at_all = False
            phones = None
            if phone == 'all':
                at_all = True
            else:
                phones = phone.split(',')

            at = {'isAtAll': at_all}
            if phones:
                at['atMobiles'] = phones
            text_meta['at'] = at

        return self.send(text_meta, tag, interval)

    async def async_send_link(self, title, desc, message_url, pic_url=None, tag=None, interval=None):
        link_meta = {
            "msgtype": "link",
            "link": {
                "text": desc,
                "title": title,
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }
        return await self.async_send(link_meta, tag, interval)

    def send_link(self, title, desc, message_url, pic_url=None, tag=None, interval=None):
        link_meta = {
            "msgtype": "link",
            "link": {
                "text": desc,
                "title": title,
                "picUrl": pic_url,
                "messageUrl": message_url
            }
        }
        return self.send(link_meta, tag, interval)

    @staticmethod
    async def async_check_response(resp):
        text = await resp.text()
        if not 200 <= resp.status < 300:
            RuntimeError(f'发送失败 {text}')

        try:
            res = await resp.json()
        except ValueError:
            raise RuntimeError(f'返回值异常 {text}')

        if str(res.get('errcode')) == '0':
            return True

        raise RuntimeError(f'发送失败 {text}')

    @staticmethod
    def check_response(resp):
        text = resp.text
        if not 200 <= resp.status_code < 300:
            raise RuntimeError(f'发送失败 {text}')

        try:
            res = resp.json()
        except ValueError:
            raise RuntimeError(f'返回值异常 {text}')

        if str(res.get('errcode')) == '0':
            return True

        raise RuntimeError(f'发送失败 {text}')
