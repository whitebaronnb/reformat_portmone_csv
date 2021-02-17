#!/bin/sh
scutil --nc start "PGH" --secret $IPSec
sleep 2
venv/bin/python main.py
scutil --nc stop "PGH"