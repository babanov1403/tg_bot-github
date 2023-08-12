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


class Interface_action:
    def send_notes(self, cb_additional, is_editing = False): #notes_count ---> cb_additional
        try:                                                   #в цикле счетчик, играет с cb_additional, и break
            table = boto3.resource("dynamodb").Table(DB_NEW)
            scanned_items = table.query( #dictionary
                KeyConditionExpression=Key('chat_id').eq(self.chat_id), 
                    )
            scanned_items["Items"] = scanned_items["Items"][:-1]#здесь срез когда prefernces появятся
            if len(scanned_items["Items"]) >= 1:
                outp = ""
                last_note_index = 0
                message_id_list = []
                for item in reversed(scanned_items["Items"]):
                    msg_postfix = ""
                    last_note_index += 1 #first message is the most fresh
                    if last_note_index <= 5*cb_additional and last_note_index >= 5*(cb_additional-1)+1:
                        if int(item['active']) == 1:
                            msg_postfix = f" (remind at {self.convert_from_unix(int(eval(item['message'])['remind_time']))})"
                        elif "ttl" in item.keys():
                            msg_postfix = " (passed)"
                        message_id_list.append(int(item['sortkey']))
                        message_payload = eval(item['message'])
                        timestamp = datetime.datetime.fromtimestamp(message_payload["date"])
                        timestamp_now = datetime.datetime.fromtimestamp(self.time)
                        if timestamp.strftime('%Y') == timestamp_now.strftime('%Y'):
                            time_outp = timestamp.strftime('%B %d')
                        else:
                            time_outp = timestamp.strftime('%B %d %Y')
                        #outp += str(len(scanned_items['Items']) - item['message_id'] + 1) + ") " + item["text"] + "\n"
                        outp += str(last_note_index) + ") " + message_payload['text'] +f"{msg_postfix}, " + time_outp + "\n\n"#["message"]['message']))))))))))))))))))
                    elif last_note_index > 5*cb_additional:
                        last_note_index-=1#останавливается на номере последнего выведенного сообщения => не кратен 5 => их всего будет last_note_index%5
                        break
                    else:
                        pass
                outp += "To edit - select a number:"
                markup = types.InlineKeyboardMarkup(row_width = 5)
                btn_list = []
                notes_count = last_note_index%5 if last_note_index%5 != 0 else 5 
                
                for i, msg_id in zip(range(notes_count), message_id_list):
                    btn = types.InlineKeyboardButton(text = f'{last_note_index-(notes_count-i)+1}', callback_data = f'{msg_id} --- {cb_additional}')
                    btn_list.append(btn)
                
                if notes_count >= 5:
                    markup.add(btn_list[0], btn_list[1], btn_list[2], btn_list[3], btn_list[4])
                elif notes_count == 4:
                    markup.add(btn_list[0], btn_list[1], btn_list[2], btn_list[3])
                elif notes_count == 3:
                    markup.add(btn_list[0], btn_list[1], btn_list[2])
                elif notes_count == 2:
                    markup.add(btn_list[0], btn_list[1])
                elif notes_count == 1:
                    markup.add(btn_list[0])
                btn_forward = types.InlineKeyboardButton('Next>>', callback_data = f'forward --- {cb_additional}')
                btn_previous = types.InlineKeyboardButton('<<Previous', callback_data = f'previous --- {cb_additional}')
                if len(scanned_items["Items"]) <= 5:
                    pass
                elif last_note_index == len(scanned_items["Items"]):
                    markup.add(btn_previous)
                elif last_note_index == 5:
                    markup.add(btn_forward)
                else:
                    markup.add(btn_previous, btn_forward)
                if is_editing:
                    bot.edit_message_text(text = outp, chat_id = self.chat_id, message_id = self.message_id, reply_markup = markup)
                else:
                    bot.send_message(self.chat_id, outp, reply_markup = markup)
                return{
                    'statusCode' : 200
                }
            else:
                bot.send_message(self.chat_id, "Type something to add a note or a reminder")
        except Exception as e:
            bot.send_message(CHAT_ID1, str(e) + " error10000")
            bot.send_message(CHAT_ID2, str(e) + " error10000")
            print(e)
            return{
                    'statusCode' : 200
                }

    def parser(self): #returns arr e.g. "new text 18:30" -> ["18", "30", "new text"]
        #я бы с огромным удовольствием вшил бы это в bananov_pdt, но когда я полез в код библиотеки я понял что не могу прочитать названия переменных
        arr = self.text.strip().split(" ")
        helper = []
        for burger in arr:
            if ':' in burger and (len(burger) == 4 or len(burger) == 5):
                helper = burger.split(":")
                try:
                    h = helper[0]
                    m = helper[1]
                    if int(h)<=24 and int(h) >=0 and int(m)<=59 and int(m)>=0:
                        #self.text = self.text.replace(f"{h}:{m}", "")
                        return [int(h), int(m), self.text.strip()]
                    else:
                        return False
                except Exception as e:
                    bot.send_message(CHAT_ID1, "error11 " + str(e))
                    return {
                        'statusCode' : 200
                    }
        return None
    def when_remind_parser(self):
        """
        пара слов о том как работает pdt
        когда она принимает текст типа "15 минут" - она просто делает offset с настоящего времени(блять неужели с твоей tz?) на 15*60 секунд, далее я перевожу
        timestamp в человеческий вид и бла бла бла
        если она принимает чтото типа "15:00" - то она возвращает timestamp:
        1) дата такая же, когда было написано сообщение(если например сейчас 20:00, а напоминание поставлено на 15:00 - вернется сегодняшняя дата 15:00)
        2) если ты заводишь время например 15:00, она возвращает время 15:00 + timezone_delta(для мск +3) => напоминание поставится на 18:00
        """
        
        # n_time = datetime.datetime.now(tz = tz).strftime("%d-%m-%Y-%H-%M")#utc(+tz)-utc_now(+tz) = delta utc(+0)
        # time_arr = n_time.split('-') # 0 - d | 1 - m | 2 - y | 3 - h | 4 - m
        # H_now = int(time_arr[3])
        # M_now = int(time_arr[4])
        # S = H*3600+M*60
        # S_now = H_now*3600 + M_now*60
        # unix_delta = (S-S_now)%(24*3600)
        # d = datetime.datetime.utcnow()
        # epoch = datetime.datetime(1970,1,1)
        # outp = int((d - epoch).total_seconds()) + unix_delta
        # dt = datetime.datetime.now(tz = tz)
        # dt = dt.utcoffset().total_seconds()
        # #блять подумать
        # when_time = when_time - dt#(-tz)
        # d = datetime.datetime.utcnow() 
        # epoch = datetime.datetime(1970,1,1)
        # now_time = int((d - epoch).total_seconds())
        
        # unix_delta = (when_time - now_time)%(3600*24)
        # outp_time = now_time + unix_delta
        # #bot.send_message(CHAT_ID1, s)
        """
        18:00 по твоему времени
        через 15 минут - +15*60 sec к utc0 => 15:15(utc) -> 18:15(+3)
        в 18:15 - время 18:15 в utc => 21:15(+3)
        """
        
        calendar = pdt.Calendar(pdt.Constants(localeID = 'ru_RU'))
        parser_val = self.parser()
        
        time_struct, useless_int = calendar.parse(self.text)
        bot.send_message(CHAT_ID1, str(time_struct))
        #when_time = int(time_l.mktime(time_struct)) - self.tz*60
        when_time = int(time_l.mktime(time_struct))
        if parser_val:
            #1)вычесть tz, 2)проверить больше меньше чем now_time => ничего не делать/прибавить день
            when_time -= self.tz*3600
            d = datetime.datetime.utcnow()
            epoch = datetime.datetime(1970,1,1)
            outp = int((d - epoch).total_seconds())
            if(when_time <= outp):
                when_time += 60*60*24
        else:
            when_time -= self.tz*3600
        return when_time
    
    def convert_from_unix(self, unix_time: int):#must be in utc #really
        ts = int(unix_time)
        return str(datetime.datetime.fromtimestamp(ts, timezone(offset=datetime.timedelta(hours = self.tz))).strftime('%B %d %H:%M'))
        
    def welcome_message(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_settings = types.KeyboardButton(f"{emoji5}Settings")
        btn_note_list = types.KeyboardButton(f"{emoji1}List")
        btn_feedback = types.KeyboardButton(f"{emoji6}Feedback")
        markup.add(btn_note_list, btn_settings)
        markup.add(btn_feedback)
        #bot.send_message(self.chat_id, text="Type your note or reminder, e. g. 'pick up laundry 18:30' or 'ran out of salt'", reply_markup=markup)
        bot.send_message(self.chat_id, text="Так ну сначала давай ты долбаеб выберешь свой язык и таймзону => для этого нажми настройки?", reply_markup = markup)
        return{
            'statusCode':200
        }
    
    def item_putter(self):
        try:
            is_reminder = self.when_remind_parser()
            if not is_reminder:
                # adding item to db
                table = boto3.resource("dynamodb").Table(DB_NEW)
                # #catching index of an item
                # scanned_items = table.query(
                # KeyConditionExpression=Key('chat_id').eq(chat_id)
                #     )
                db_dict = {}
                db_dict["text"] = self.text.strip()
                db_dict["date"] = self.time
                #putting an item in db
                response = table.put_item(
                    Item = {"chat_id": self.chat_id, 
                            "sortkey": f"{self.message_id}",
                            "active" : 0,
                            "message": str(db_dict)
                          }
                )
                bot.send_message(self.chat_id, emoji1)
                bot.send_message(self.chat_id, f"Note \n'{self.text.strip()}'\n has been added! To view all notes /list")
                return {
                'statusCode' : 200
                }
            else:
                self.text = self.text.lower().strip()#это нормально или нет?
                remind_time = is_reminder#check the when_remind_parser
                db_dict = {}
                db_dict["text"] = self.text
                db_dict["remind_time"] = int(remind_time)  ######PREFIRE
                db_dict["date"] = int(self.time)
                
                table = boto3.resource("dynamodb").Table(DB_NEW)
                table.put_item(
                    Item = {"active": 1,
                            "sortkey": str(self.message_id),
                            "chat_id": self.chat_id,
                            "message": str(db_dict),
                            "sortkey2": str(int(remind_time))
                          }
                )
                time_remind = self.convert_from_unix(remind_time)
                bot.send_message(self.chat_id, emoji2)
                bot.send_message(self.chat_id, f"Reminder: \n'{self.text}'\n at {time_remind} has been added!  To view all reminders /list")
                return {
                    'statusCode' : 200
                }
        except Exception as e:
            bot.send_message(CHAT_ID1, f"{str(e)} error4")
            return {
                'statusCode' : 200
            }
    def note_menu(self): #ch_id, msg_id, cb_datа
        try:
            table = boto3.resource("dynamodb").Table(DB_NEW)
            response = table.get_item(Key={'chat_id': int(self.chat_id), 'sortkey': str(self.cb_data)})
            #bot.send_message(CHAT_ID1, str(response))
            
            item = response["Item"]
            
            btn_delete = types.InlineKeyboardButton(f'Удалить{emoji3}', callback_data = f'delete --- {self.cb_data}')
            btn_edit = types.InlineKeyboardButton(f'Редактировать{emoji1}', callback_data = f'edit --- {self.cb_data}')
            btn_back = types.InlineKeyboardButton(f'Вернуться{emoji4}', callback_data = f'list_back --- {self.cb_data}')
            markup = types.InlineKeyboardMarkup()
            markup.add(btn_edit, btn_delete) 
            markup.add(btn_back)
            text = eval(item['message'])["text"]
            bot.edit_message_text(text = text, chat_id = self.chat_id, message_id = self.message_id, reply_markup = markup)
            return {
                'statusCode' : 200
            }
        except Exception as e:
            bot.send_message(CHAT_ID1, f'{str(e)} error12')
            return {
                'statusCode' : 200
            }
    def settings_menu(self):
        try:
            table = boto3.resource("dynamodb").Table(DB_NEW)
            response = table.query(
                KeyConditionExpression=Key('chat_id').eq(self.chat_id)
            )
            user_pref_dict = eval(response['Items'][-1]['message'])
            tz_user = datetime.timezone(datetime.timedelta(hours = int(user_pref_dict['tz'])))
            n_time = datetime.datetime.now(tz = tz_user).strftime("%Y, %H:%M")
            markup = types.InlineKeyboardMarkup()
            btn_set_lang = types.InlineKeyboardButton(f'Set language{emoji8}', callback_data = f'language_set')
            btn_set_tz = types.InlineKeyboardButton(f'Set timezone{emoji7}', callback_data = f'timezone_set')
            markup.add(btn_set_lang, btn_set_tz)
            bot.edit_message_text(message_id = self.message_id, chat_id =self.chat_id, reply_markup = markup, text = f"Your current settings:\n- language: {user_pref_dict['language']}\n- time zone: Europe/Moscow ({user_pref_dict['tz']})\n- local time: {n_time}")
            return{
                'statusCode' : 200
            }
        except Exception as e:
            bot.send_message(CHAT_ID1, f'{str(e)} error_ilya')
            return{
                'statusCode' : 200
            }