import json
import os
import datetime
import time as time_l
from datetime import time,timezone
import boto3
from boto3.dynamodb.conditions import Key, Attr
from telebot import TeleBot, types
import bananov_pdt as pdt
from classMessage import Message
from classCallback import Callback
from classEdit_message import Edited_Message

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
#tz = datetime.timezone(datetime.timedelta(hours = 3))
bot = TeleBot(TOKEN)
#hello from my pc
#hello from my pc one more time


def lambda_handler(event, context):
    payload = json.loads(event['body'])
    if "callback_query" in payload.keys():
        try:
            message = Callback(payload)
            if message.cb_data == "forward":
                message.send_notes(int(message.cb_additional)+1, True)
            elif message.cb_data == "previous":
                message.send_notes(int(message.cb_additional)-1, True)
            elif message.cb_data == "delete":
                table = boto3.resource("dynamodb").Table(DB_NEW)
                response = table.delete_item(Key={'chat_id': int(message.chat_id), 'sortkey': str(message.cb_additional)})
                bot.send_message(message.chat_id, "Сообщение успешно удалено!")
                message.send_notes(1)
            elif message.cb_data == "edit":
                bot.send_message(message.chat_id, reply_to_message_id = message.cb_additional, text = "Edit the original message⤴️:")
            elif message.cb_data == "list_back":
                message.send_notes(1, True)
            elif message.cb_data == "delta":
                table = boto3.resource("dynamodb").Table(DB_NEW)
                # get item
                response = table.get_item(Key={'chat_id': int(message.chat_id), 'sortkey': str(message.cb_msg_id)})
                item = response['Item']
            
                # update
                d = datetime.datetime.utcnow()
                epoch = datetime.datetime(1970,1,1)
                from_what_time_i_should_send_fucking_message = int((d - epoch).total_seconds())
                item['active'] = 1
                db_dict = eval(item['message'])
                db_dict["remind_time"] = int(from_what_time_i_should_send_fucking_message) + int(message.cb_additional)#здесь было дб -> сообщение, стало сейчас -> сообщение
                item['sortkey2'] = str(db_dict["remind_time"])
                item['ttl'] = int(item['sortkey2'])+24*3600
                item['message'] = str(db_dict)
            
                # put (idempotent))) impotent
                table.put_item(Item=item)
                markup = types.InlineKeyboardMarkup()
                #сюда вставить
                time_string = message.calc_time_output()
                message.text = message.text.replace("Remind in:", "")
                message.text += f"Reminder will be in {time_string}"
                bot.edit_message_text(text = message.text, chat_id = message.chat_id, message_id = message.message_id, reply_markup = markup) # написать через сколько обратно сконвертировав в минуты\дни итд
            elif message.cb_data == "language_set":
                bot.send_message(message.chat_id, "Coming soon")
            elif message.cb_data == "settings_back":
                message.settings_menu()
            elif message.cb_data == "timezone_set":
                if(len(message.cb_additional) == 0):#если запрос пустой(без cb типа 84 или 85 строки в данном коде)
                    markup = types.InlineKeyboardMarkup()
                    btn_tz_0 = types.InlineKeyboardButton(f'Moscow/SaintP(+3)', callback_data = f'timezone_set --- +3')
                    btn_tz_1 = types.InlineKeyboardButton(f'Iceland(+0)', callback_data = f'timezone_set --- +0')
                    btn_tz_2 = types.InlineKeyboardButton(f'Khanty-Mansiysk(+5)', callback_data = f'timezone_set --- +5')
                    btn_back1 = types.InlineKeyboardButton(f'Back{emoji4}', callback_data = f'settings_back')
                    markup.add(btn_tz_0)
                    markup.add(btn_tz_1)
                    markup.add(btn_tz_2)
                    markup.add(btn_back1)
                    bot.edit_message_text(text = "Choose your timezone:", chat_id = message.chat_id, message_id = message.message_id, reply_markup = markup)
                else:
                    #обращение в базу, берем элемент:
                    table = boto3.resource("dynamodb").Table(DB_NEW)
                    response = table.get_item(Key = {'chat_id' : int(message.chat_id), 'sortkey' : "user_pref"})
                    item = response["Item"]
                    db_dict = eval(item['message'])
                    db_dict['tz'] = int(message.cb_additional)
                    item['message'] = str(db_dict)
                    table.put_item(Item=item)
                    #bot.send_message(message.chat_id, text = str(item))
            else:
                message.note_menu()
                
            return {
                'statusCode' : 200
            }
        except Exception as e:
            print(str(e) + " error")
            bot.send_message(CHAT_ID1, str(e) + " error1")
            return {
                'statusCode' : 200
            }
    elif "edited_message" in payload.keys():
        try:
            message = Edited_Message(payload)
            table = boto3.resource("dynamodb").Table(DB_NEW)
            # get item
            response = table.get_item(Key={'chat_id': int(message.chat_id), 'sortkey': str(message.message_id)})
            item = response['Item']
            # update
            db_dict = eval(item['message'])
            db_dict["text"] = message.text
            item['message'] = str(db_dict)
            # put (idempotent))) impotent
            table.put_item(Item=item)
            bot.send_message(message.chat_id, "Edited succesfully. See all /list")
            
            
            return{
                'statusCode' : 200
            }
        except Exception as e:
            bot.send_message(CHAT_ID1, str(e) + " error3")
            return{
                'statusCode' : 200
            }
    elif 'message' in payload.keys():
        try:
            message = Message(payload)
            
            if not message.is_text:
                bot.send_sticker(message.chat_id, funny_sticker)
                bot.send_message(message.chat_id,"чел ты")
                return {
                'statusCode' : 200
                }  
            else:
                
                if len(message.text)>128:
                    bot.send_message(message.chat_id, "Your message is too long, try shorter text")
                else:
                    if message.text.lower().strip().find("/start") != -1:
                        message.start_com()
                    elif message.text.strip().find("/sanyacount") != -1:
                        message.sanyacount_com()
                    elif message.text.strip().find(f"{emoji1}List")!=-1 or message.text.lower().strip().find("/list")!=-1:
                        message.list_com()
                    elif message.text.strip().find(f"{emoji6}Feedback") != -1:
                        message.feedback_com()
                    elif message.text.strip().find(f"{emoji5}Settings") != -1:
                        message.settings_com()
                    else:
                        message.note_or_reminder_com()
                    return {
                        'statusCode' : 200
                    }
        except Exception as e:
            bot.send_message(CHAT_ID1, str(e) + " error111")
            return {
                'statusCode' : 200
            }
    else:
        return{
            'statusCode' : 200
        }

        
    
    
    