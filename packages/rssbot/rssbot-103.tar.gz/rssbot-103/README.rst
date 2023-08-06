NAME
====

**RSSBOT** - rss feed fetcher for irc channels.

SYNOPSIS
========

``rssctl <cmd> [options] [key=value] [key==value]``

INSTALL
=======

| ``pip3 install rssbot``


DESCRIPTION
===========

**RSSBOT** is a IRC bot that fetches rss feeds and displays them into irc 
channels. It runs as a background daemon for 24/7 a day presence in a IRC
channel. 

**RSSBOT** is a messenger that only messages, no commands or DCC capabilities.


CONFIGURATION
==============

systemd
-------

| cp /usr/local/share/rssbot/rssbot.service /etc/systemd/system
| systemctl enable rssbot --now

| * default channel/server is #rssbot on localhost

rss
---

| ``rssctl rss <url>``

irc
---

| ``rssctl cfg server=<server> channel=<channel> nick=<nick>``

sasl
----

| ``rssctl pwd <nickservnick> <nickservpass>``
| ``rssctl cfg password=<outputfrompwd>``


COPYRIGHT
=========

**RSSBOT** is placed in the Public Domain, no Copyright, no LICENSE.

AUTHOR
======

Bart Thate 
