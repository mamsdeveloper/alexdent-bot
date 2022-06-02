#!/bin/bash
ps -ef | grep "/home/k/kurer843/aleks-dent-telebot/alex_dent_bot.py" | awk '{print $2}' | xargs sudo kill
cd /home/k/kurer843/aleks-dent-telebot
nohup python3 alex_dent_bot.py &