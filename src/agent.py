# -*- coding: utf-8 -*-
#
# This file is part of Zoe Assistant
# Licensed under MIT license - see LICENSE file
#

from telebot import types
from zoe import *
from threading import Thread

import telebot
import json


# zoe-agent-tila/config.json for running in venv
# code/config.json for running with docker
bot = telebot.TeleBot(json.loads(open("./config.json").read())['token'], parse_mode='Markdown')


class TilaAgent(Agent):

    def __init__(self, name):
        super().__init__(name)
        global bot
        bot.zoe_broker = self.agent._listener
        th = Thread(target=bot.polling)
        th.start()

    @Intent("tila.read")
    def send_to_chat(self, intent):
        """ Expected intent
            {
                "intent": "tila.read",
                "chat": "chat id"
                "messsage": "message to send to the telegram chat"
            }
        """
        global bot
        bot.send_message(intent['chat'], intent['message'])

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        markup = types.ReplyKeyboardMarkup()
        led_but = types.InlineKeyboardButton('/led')
        temp_but = types.InlineKeyboardButton('/temperature')
        markup.row(led_but, temp_but)
        bot.reply_to(message, f"Hellou {message.from_user.first_name}", reply_markup=markup)

    @bot.message_handler(commands=['led'])
    def led_options(message):
        """ Show commands related to the leds
        """
        markup = types.ReplyKeyboardMarkup()
        led_status = types.InlineKeyboardButton('/get_led_status')
        led_on = types.InlineKeyboardButton('/turn_led_on')
        led_off = types.InlineKeyboardButton('/turn_led_off')
        markup.row(led_status)
        markup.row(led_on, led_off)
        bot.reply_to(message, "Turn on / off?", reply_markup=markup)

    @bot.message_handler(commands=['turn_led_on'])
    def turn_on_led(message):
        """ Send to the pico-agent to turn on the led
        """
        bot.reply_to(message, "Led on")
        bot.zoe_broker.send(json.dumps(
            {"intent": "pico.led", "led": True, "chat": message.chat.id}
        ))

    @bot.message_handler(commands=['turn_led_off'])
    def turn_off_led(message):
        """ Send to the pico-agent to turn off the led
        """
        bot.reply_to(message, "Led off")
        bot.zoe_broker.send(json.dumps(
            {"intent": "pico.led", "led": False, "chat": message.chat.id}
        ))

    @bot.message_handler(commands=['get_led_status'])
    def get_led_status(message):
        """ Request to the pico-agent the status of the led
        """
        bot.reply_to(message, "Requesting led status")
        bot.zoe_broker.send(json.dumps(
            {"intent": "pico.get_led", "chat": message.chat.id}
        ))

    @bot.message_handler(commands=['temperature'])
    def get_temp(message):
        """ Request to the pico-agent the current temperature
        """
        bot.reply_to(message, "Requesting temperature")
        bot.zoe_broker.send(json.dumps(
            {"intent": "pico.get_temp", "chat": message.chat.id}
        ))

if __name__ == "__main__":
    tila = TilaAgent("Tila")
    tila()
