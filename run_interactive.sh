#!/usr/bin/env bash
python3 run_bpy.py $1
when-changed $1 -c "clear; python3 run_bpy.py $1"
