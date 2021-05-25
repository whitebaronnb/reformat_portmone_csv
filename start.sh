#!/bin/sh
scutil --nc start "PGH Utels" --secret $IPSec
sleep 5
venv/bin/python3 main.py
scutil --nc stop "PGH Utels"