#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Oleg Lomaka'
SITENAME = 'ALEK.WS'
SITEURL = ''
SITEURL = 'http://www.alek.ws'

TIMEZONE = 'Europe/Kiev'

DEFAULT_LANG = 'ru'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = "feeds/atom.xml"
FEED_ALL_RSS = "feeds/rss.xml"
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
# LINKS =  (('Pelican', 'http://getpelican.com/'),
#           ('Python.org', 'http://python.org/'),
#           ('Jinja2', 'http://jinja.pocoo.org/'),
#           ('You can modify those links in your config file', '#'),)
LINKS = ()

# LINKS = ()

# Social widget
SOCIAL = (
    ('<span class="icomoon-twitter" ></span> Twitter', 'https://twitter.com/olomix'),
    ('<span class="icomoon-github" ></span> Github', 'https://github.com/olomix'),
)
# SOCIAL = ()

# DEFAULT_PAGINATION = False
DEFAULT_PAGINATION = 20

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False

THEME = 'alek.ws.theme'
ARTICLE_URL = '{category}/{date:%Y}/{date:%b}/{date:%d}/{slug}.html'
ARTICLE_SAVE_AS = ARTICLE_URL

FOOTER_TEXT = "© 2014 Oleg Lomaka"

# CSS_PYGMENTS = 'pygments-zenburn.css'
