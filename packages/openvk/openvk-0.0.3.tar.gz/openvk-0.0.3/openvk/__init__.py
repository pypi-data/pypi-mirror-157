"""
:author: Parliskaya
:license: Apache License, Version 2.0, see LICENSE file

:copyright: (c) 2022 Parliskaya
"""

from .openvkapi import *
from .account import account
from .friends import friends
from .groups import groups
from .messages import messages
from .utils import utils
from .users import users
from .news_feed import news_feed
from .wall import wall

openvkapi = openvkapi()
account = account()
friends = friends()
groups = groups()
messages = messages()
utils = utils()
users = users()
news_feed = news_feed()
wall = wall()


__author__ = 'Parliskaya'
__version__ = '0.0.3'
__email__ = 'alonaparlis@gmail.com'