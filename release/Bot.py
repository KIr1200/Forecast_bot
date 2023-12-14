import json
import re
import telebot
from telebot import types
from back_end import *
from forecast_script import *
import os
import time

Dict_data = {}
Dict_params = {}

bot = telebot.TeleBot('your_bot_token')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(message.from_user.id, "Здравствуйте, напишите тикер акции, которую хотите спрогнозировать (пример = AAPL)", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_ticker(message):
    global Dict_data
    List_data = ['', '', '', ''] #ticker, horizon, model
    #bot.send_photo(message.from_user.id, 'dgEI7PDozTI.jpg')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ticker = message.text
    if(check_ticker(ticker) == 'Wrong ticker'):
        bot.send_message(message.from_user.id, f"Некорректный тикер {ticker}, введите новый", reply_markup=markup)
        return

    List_data[0] = ticker
    Dict_data.update({message.from_user.id : List_data})
    bot.send_message(message.from_user.id, 'Укажите горизонт предсказания в днях (пример 7)', reply_markup=markup)
    bot.register_next_step_handler(message, get_horizon)


def get_horizon(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global Dict_data

    if not Dict_data.get(message.from_user.id):
        bot.send_message(message.from_user.id, 'Возникла неполадка перевыберите ваш тикер', reply_markup=markup)
        bot.register_next_step_handler(message, get_ticker)
        return

    horizon = Dict_data.get(message.from_user.id)[1]

    if(message.text == 'Да' and horizon != ''):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Sarimax', callback_data=3))
        markup.add(telebot.types.InlineKeyboardButton(text='SSSmuzi', callback_data=4))
        markup.add(telebot.types.InlineKeyboardButton(text='Catboost', callback_data=5))
        bot.send_message(message.from_user.id, 'Выберите модель', reply_markup=markup)
        return
    elif(message.text == 'Нет' and horizon != ''):
        Dict_data[message.from_user.id][1] = ''
        bot.send_message(message.from_user.id, 'Перевыберите число', reply_markup=markup)
        bot.register_next_step_handler(message, get_horizon)
        return

    horizon = check_horizon(message.text)
    if(horizon == -1):
        bot.send_message(message.from_user.id, 'Пожалуйста напишите положительное число', reply_markup=markup)
    if(horizon == -3):
        bot.send_message(message.from_user.id, 'Пожалуйста напишите число', reply_markup=markup)
    if(horizon == -2):
        btn1 = types.KeyboardButton('Да')
        btn2 = types.KeyboardButton('Нет')
        markup.add(btn1, btn2)
        bot.send_message(message.from_user.id, 'Число слишком большое. Вы уверены?', reply_markup=markup)
        Dict_data[message.from_user.id][1] = int(message.text)
        bot.register_next_step_handler(message, get_horizon)
        return

    Dict_data[message.from_user.id][1] = horizon

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Sarimax', callback_data=3))
    markup.add(telebot.types.InlineKeyboardButton(text='EXPONENTIAL_SMOOTHING', callback_data=4))
    markup.add(telebot.types.InlineKeyboardButton(text='Catboost', callback_data=5))
    bot.send_message(message.from_user.id, 'Выберите модель', reply_markup=markup)


def get_dop_params(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global Dict_data
    params = message.text
    #TODO убрать дублирование
    if params.lower() == 'run':
        dict_params = parse_params_sarimax(params)
        filename = f"{message.from_user.id}_kwargs_model.json"
        with open(filename, "w", encoding="utf-8") as file:
          json.dump(dict_params, file)
        bot.send_message(message.from_user.id, 'Взял в работу ваши данные, мне надо немного подумать')
        run_forecast([message.from_user.id] + Dict_data[message.from_user.id])
        print_png_and_data(message.from_user.id, bot)
        return

    if Dict_data[message.from_user.id][2] == 'SARIMA':
        dict_params = parse_params_sarimax(params)
        filename = f"{message.from_user.id}_kwargs_model.json"
        with open(filename, "w", encoding="utf-8") as file:
          json.dump(dict_params, file)
        bot.send_message(message.from_user.id, 'Взял в работу ваши данные, мне надо немного подумать')
        run_forecast([message.from_user.id] + Dict_data[message.from_user.id])
        print_png_and_data(message.from_user.id, bot)
        return
        
    if Dict_data[message.from_user.id][2] == 'EXPONENTIAL_SMOOTHING':
        filename = f"{message.from_user.id}_kwargs_model.json"
        with open(filename, "w", encoding="utf-8") as file:
          json.dump(dict_params, file)



@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global Dict_data
    global Dict_params
    if not Dict_data.get(call.message.chat.id):
        bot.answer_callback_query(callback_query_id=call.id, text='Возникла неполадка, выберите данные занового')
        return
    if   call.data == '3':
        Dict_data[call.message.chat.id][2] = 'SARIMA'
    elif call.data == '4':
        Dict_data[call.message.chat.id][2] = 'EXPONENTIAL_SMOOTHING'
    elif call.data == '5':
        Dict_data[call.message.chat.id][2] = 'CATBOOST'


    elif call.data == '11' or call.data == '12':
        if call.data == '12':
            list_params_smooth = ['add', '']
        else:
            list_params_smooth = ['mul', '']
        Dict_params.update({call.message.chat.id : list_params_smooth })
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Да', callback_data=13))
        markup.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data=14))
        bot.send_message(call.message.chat.id, f"Ваш тренд затухающий?", reply_markup=markup)
        return
    elif call.data == '13' or call.data == '14':
        if not Dict_params[call.message.chat.id]:
              bot.send_message(call.message.chat.id, f"Произошла утечка данных, перевыберите ваши параметры")
        if call.data == '13':
            Dict_params[call.message.chat.id][1] = True
        else:
            Dict_params[call.message.chat.id][1] = False
        filename = f"{call.message.chat.id}_kwargs_model.json"
        with open(filename, "w", encoding="utf-8") as file:
          json.dump({'trend': Dict_params[call.message.chat.id][0], 'damped_trend' : Dict_params[call.message.chat.id][1], 'initialization_method': 'estimated'}, file)
        bot.send_message(call.message.chat.id, 'Взял в работу ваши данные, мне надо немного подумать')
        run_forecast([call.message.chat.id] + Dict_data[call.message.chat.id])
        print_png_and_data(call.message.chat.id, bot)


    bot.send_message(call.message.chat.id, f"Ваши данные :{Dict_data[call.message.chat.id][0]} {Dict_data[call.message.chat.id][1]} {Dict_data[call.message.chat.id][2]}")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    if call.data ==   '3':
        bot.send_message(call.message.chat.id, f"Выберите дополнительные параметры для модели SARIMA (p d q), впишите их в одну строку через пробел -- например p=1 q=2 d=3, \
                         неуказанным параметрам будет присвоено дефолтное значение, все единицы! Отправьте run если хотите оставить всё по дефолту")
        bot.register_next_step_handler(call.message, get_dop_params)

    elif call.data == '4':
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='Аддитивный', callback_data=11))
        markup.add(telebot.types.InlineKeyboardButton(text='Мультипликативный', callback_data=12))
        bot.send_message(call.message.chat.id, f"Выберите параметры для модели EXPONENTIAL_SMOOTHING\nВыберите trend", reply_markup=markup)

    elif (call.data == '5'):
        bot.send_message(call.message.chat.id, 'Взял в работу ваши данные, мне надо немного подумать')
        run_forecast([call.message.chat.id] + Dict_data[call.message.chat.id])
        print_png_and_data(call.message.chat.id, bot)


bot.polling(none_stop=True, timeout=123) #обязательная для работы бота часть