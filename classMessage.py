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
import bananov_pdt as pdt #origin name - parsedatetime?

funny_sticker = "CAACAgIAAxkBAAIHQ2MGk1hIJT6L0pkPI4s05Rbr4wjUAAK0AAM-7VswsCSiLczQ7DspBA"
TIMEZONES_DICT = {"Калининград":"2", "Москва":"3", "Самара":"4", "Екатеринбург":"5", "Омск":"6", "Новосибирск":"7", "Иркутск":"8", "Чита":"9", "Владивосток":"10","Магадан":"11","Петропавловск-Камчатский":"12"}
emoji1 = "📝"
emoji2 = "💡"
emoji3 = "❌"
emoji4 = "↩️"
emoji5 = "⚙️"
emoji6 = "🧑🏻‍💻"
emoji7 = "✈️"
emoji8 = "🇬🇧"

TOKEN = os.environ["TOKEN"]
CHAT_ID1 = os.environ["CHAT_ID"]
CHAT_ID2 = os.environ["SANYA"]
DB_NOTE = "db_note"
DB_REMINDER = "db_reminder"
DB_USER = "db_user"
DB_NEW = "planner_table"
#tz = datetime.timezone(datetime.timedelta(hours = 3))
bot = TeleBot(TOKEN)

class Message(Interface_action):
    def __init__(self, payload):
        self.chat_id = payload['message']['chat']['id']
        self.message_id = payload['message']['message_id']
        self.time = payload['message']['date']
        if 'text' in payload['message']:
            self.text = payload['message']['text']
            self.is_text = True
        else:
            self.is_text = False
        table = boto3.resource("dynamodb").Table(DB_NEW)
        response = table.get_item(Key = {'chat_id' : int(self.chat_id), 'sortkey' : "user_pref"})
        if "Item" in response:
            item = response["Item"]
            db_dict = eval(item['message'])
            self.tz = int(db_dict['tz'])
        else:
            self.tz = 0
    def start_com(self):
        table = boto3.resource("dynamodb").Table(DB_NEW)
        db_dict = {}
        db_dict['tz'] = "+3"
        db_dict['language'] = "English"
        
        response = table.put_item(
        Item = {"chat_id": self.chat_id, 
                "sortkey": "user_pref",
                "active" : 2,
                "message": str(db_dict),
                "sortkey2" : "pppppp"
              }
        )
        self.welcome_message()
        #bot.send_message(self.chat_id, str(db_dict))
    def sanyacount_com(self):#/sanyacount
        table = boto3.resource("dynamodb").Table(DB_NEW)
        response = table.query(
            IndexName='active-index',
            KeyConditionExpression=Key('active').eq(2),
        )
        bot.send_message(self.chat_id, f"Now we have {len(response['Items'])} unique users!")
        return{
            'statusCode' : 200
        }
    def list_com(self):
        self.send_notes(1)
    def feedback_com(self):
        bot.send_message(self.chat_id, 
        """
        For a feedback reach out: @babanbrand\n========================== @Vintego
        """)
        return{
            'statusCode' : 200
        }
    def settings_com(self, is_back = False):
        table = boto3.resource("dynamodb").Table(DB_NEW)
        response = table.query(
            KeyConditionExpression=Key('chat_id').eq(self.chat_id)
        )
        
        user_pref_dict = eval(response['Items'][-1]['message'])
        #ПЕРЕДЕЛАТЬ
        #################################
        ##################################################################
        ##################################################################
        ##################################################################
        ##################################################################
        #################################
        if user_pref_dict['tz'] == 0:
            country = "Iceland"
        elif user_pref_dict['tz'] == 3:
            country = "SaintP"
        elif user_pref_dict['tz'] == 5:
            country = "Khanty- mansiysk"
        #################################
        ##################################################################
        ##################################################################
        ##################################################################
        ##################################################################
        #################################
        tz_user = datetime.timezone(datetime.timedelta(hours = int(user_pref_dict['tz'])))
        n_time = datetime.datetime.now(tz = tz_user).strftime("%Y, %H:%M")
        markup = types.InlineKeyboardMarkup()
        btn_set_lang = types.InlineKeyboardButton(f'Set language{emoji8}', callback_data = f'language_set')
        btn_set_tz = types.InlineKeyboardButton(f'Set timezone{emoji7}', callback_data = f'timezone_set')
        markup.add(btn_set_lang, btn_set_tz)
        if is_back:
            bot.edit_message_text(message_id = self.message_id, chat_id = self.chat_id, reply_markup = markup, text = f"Your current settings:\n- language: {user_pref_dict['language']}\n- time zone: {country} ({user_pref_dict['tz']})\n- local time: {n_time}")
        else:
            bot.send_message(self.chat_id, reply_markup = markup, text = f"Your current settings:\n- language: {user_pref_dict['language']}\n- time zone: {country} ({user_pref_dict['tz']})\n- local time: {n_time}")
        
        
    def note_or_reminder_com(self):
        self.text = self.text.strip()
        #проверка на количество заметок
        table = boto3.resource("dynamodb").Table(DB_NEW)
        response = table.query(
            KeyConditionExpression=Key('chat_id').eq(self.chat_id)
        )
        if (len(response["Items"]) >= 20) and (str(self.chat_id) != str(CHAT_ID1)):
            bot.send_message(self.chat_id, "Alexander please write something cute and nice here я блять не умею общаться нахуй, чтото про то что у пользователя долбаеба дохуя сообщений")
        else:
            self.item_putter()
     