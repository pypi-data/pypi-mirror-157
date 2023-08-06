# -*- coding: utf-8 -*-
import importlib
from setuptools import setup

DESCRIPTION = "chatbot"
VERSION = importlib.import_module('chatbot').__version__

setup(
    name='chatbotlib',
    version=VERSION,
    description=DESCRIPTION,
    author="Fizone",
    author_email="edeport126@gmail.com",
    license='Apache License 2.0',
    url="https://github.com/Orisdaddy/likeshell",
    keywords=['chat', 'bot', 'chatbot', 'dingding', 'dingtalk'],
    packages=['chatbot'],
    include_package_data=True,
    platforms="any",
    python_requires=">=3.6",
    install_requires=['requests', 'aiohttp'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)
