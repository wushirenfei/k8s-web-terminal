# -*- coding=utf-8 -*-
# Copyright 2018 Alex Ma

"""
:author Alex Ma (machao@qutoutiao.net)
:date 2018/10/18 

"""
import logging


log = logging.getLogger('web_terminal')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('/tmp/web_terminal.log')
fh.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
log.addHandler(ch)
