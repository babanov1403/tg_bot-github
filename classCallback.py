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

class Callback(Interface_action):
    def __init__(self, payload):
        self.time =  payload['callback_query']['message']['date']
        cb_data_str = payload["callback_query"]["data"].split(" --- ")#"previous --- cb_additional(page_number)" or delete --- {msg_number}'
        self.cb_data = cb_data_str[0]#callback
        self.cb_additional = "" if len(cb_data_str) == 1 else cb_data_str[1]#or page_number
        self.chat_id = payload["callback_query"]["from"]["id"]
        self.message_id = payload["callback_query"]["message"]["message_id"]
        self.text = payload["callback_query"]["message"]["text"]
        table = boto3.resource("dynamodb").Table(DB_NEW)
        response = table.get_item(Key = {'chat_id' : int(self.chat_id), 'sortkey' : "user_pref"})
        if "Item" in response:
            item = response["Item"]
            db_dict = eval(item['message'])
            self.tz = int(db_dict['tz'])
        else:
            self.tz = 0
        if self.cb_data == "delta":
            self.cb_msg_id = cb_data_str[2]
    def calc_time_output(self):
        time_output = str(datetime.timedelta(seconds = int(cb_additional)))
        time_output = time_output.split(":")
        if int(self.cb_additional) >= 24*3600:
            time_output_days = time_output[0].split(", ")
            time_output[0] = time_output_days[1]
            time_output.append(str(time_output_days[0]))
        else:
            time_output.append('0')   # 0 - hours 1 - min 2 - sec 3 - days
        for i in range(1, len(time_output)-1):
            if time_output[i][0] == '0':
                time_output[i] = str(time_output[i]).replace("0", "", 1) 
        #building string of time to sending message
        time_string = ""
        if int(time_output[3]):
            time_string += f"{time_output[3]} days, "
        if int(time_output[0]):
            time_string += f"{time_output[0]} hours, "
        if int(time_output[1]):
            time_string += f"{time_output[1]} minutes, "
        if int(time_output[2]):
            time_string += f"{time_output[2]} seconds, "
        time_string = time_string[:-2]
        return time_string
    