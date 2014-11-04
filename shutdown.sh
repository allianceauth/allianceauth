#!/usr/bin/env bash

ps ww | grep 'manage.py' | grep -v grep | awk '{print $1}' | xargs kill
