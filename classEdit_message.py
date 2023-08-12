from classInterface import Interface_action
###
import json
import os
import datetime
import time as time_l
from datetime import time,timezone
###
import boto3
from boto3.dynamodb.conditions import Key, Attr
from telebot import TeleBot, types
import bananov_pdt as pdt

funny_sticker = "CAACAgIAAxkBAAIHQ2MGk1hIJT6L0pkPI4s05Rbr4wjUAAK0AAM-7VswsCSiLczQ7DspBA"
TIMEZONES_DICT = {"Калининград":"2", "Москва":"3", "Самара":"4", "Екатеринбург":"5", "Омск":"6", "Новосибирск":"7", "Иркутск":"8", "Чита":"9", "Владивосток":"10","Магадан":"11","Петропавловск-Камчатский":"12"}
emoji1 = "📝"
emoji2 = "💡"
emoji3 = "❌"
emoji4 = "↩️"
emoji5 = "⚙️"
emoji6 = "🧑🏻‍💻"

TOKEN = os.environ["TOKEN"]
CHAT_ID1 = os.environ["CHAT_ID"]
CHAT_ID2 = os.environ["SANYA"]
DB_NOTE = "db_note"
DB_REMINDER = "db_reminder"
DB_USER = "db_user"
DB_NEW = "planner_table"
tz = datetime.timezone(datetime.timedelta(hours = 3))
bot = TeleBot(TOKEN)

class Edited_Message(Interface_action):
    def __init__(self, payload):
        self.text = payload["edited_message"]["text"]
        self.chat_id = payload["edited_message"]["chat"]["id"]
        self.message_id = payload["edited_message"]["message_id"]