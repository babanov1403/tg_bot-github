import os
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