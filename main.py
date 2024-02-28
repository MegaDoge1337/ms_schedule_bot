from config import BOT_TOKEN
from terminaltables import AsciiTable
from telebot.types import Message
import telebot
import requests
import json

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message: Message):
  pass

@bot.message_handler(commands=['schedule'])
def schedule(message: Message):
  splitted_message = message.text.split(' ')
  if len(splitted_message) <= 2:
    bot.reply_to(message, 'Неверный формат команды: используйте <code>/schedule номер-группы дата</code>', parse_mode='HTML')
    return None

  group_number = splitted_message[1]
  date = splitted_message[2]

  def get_group_id(group_number: str):
    groups_list = json.loads(requests.get('https://api.xn--80aai1dk.xn--p1ai/api/groups?subdivision_cod=1').text)
    for group in groups_list:
      if group['title'].strip() == group_number:
        return group['id']
    return None
  
  group_id = get_group_id(group_number)
  if group_id is None:
    bot.reply_to(message, f'Группа <code>{group_number}</code> не найдена', parse_mode='HTML')
    return None
  
  splitted_date = date.split('.')
  if len(splitted_date) <= 2:
    bot.reply_to(message, 'Неверный формат даты: используйте формат <code>день.месяц.год</code>', parse_mode='HTML')
    return None
  
  formatted_date = f'{splitted_date[2]}-{splitted_date[1]}-{splitted_date[0]}'
  url = f'https://api.xn--80aai1dk.xn--p1ai/api/schedule?range=4&subdivision_cod=1&group_name={group_id}&date_from={formatted_date}&date_to={formatted_date}'
  data = json.loads(requests.get(url).text)

  if len(data) <= 0:
    bot.reply_to(message, f'На дату <code>{date}</code> для группы <code>{group_number}</code> не назначено ни одной пары', parse_mode='HTML')
    return None

  table_data = [
    ['Номер пары', 'Дисиплина', 'Преподаватель', 'Тип заняти', 'Аудитория']
  ]

  for row in data:
    table_data_row = []
    table_data_row.append(row['pair'])
    table_data_row.append(row['subject'].strip())
    table_data_row.append(row['signature'].strip())
    table_data_row.append(row['study_type'].strip())
    table_data_row.append(row['classroom'].strip())
    table_data.append(table_data_row)
  
  table = AsciiTable(table_data)
  bot.reply_to(message, f'Расписание на дату <code>{date}</code> для группы <code>{group_number}</code>\n<pre>{table.table}</pre>', parse_mode='HTML')

bot.polling(none_stop=True, interval=0)