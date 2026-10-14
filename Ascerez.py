import asyncio
import os
import time
import datetime
import logging
import re
import random
import io
from aiohttp import web
from telegram import Update, ChatPermissions
from telegram.constants import ChatType
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import RetryAfter, TimedOut, NetworkError, Conflict as TelegramConflict
from telegram.request import HTTPXRequest

# ========== CONFIGURATION ==========
OWNER_ID = 8572048945

BOT_TOKENS = [
"8600041613:AAGLQoUdtBoFNTqC9HXwMeSxxAzNamWhYgg",
"7639678823:AAGNJnIMvLg69RmdyyrYmzm7veg4Sl7V2Ow",
"8814978940:AAEWMAnC3ZGJHKVD-4HdnJVtX9JAhzijg7o",
"8719538849:AAE-hgkpK17lgOhGrh0_vgtheHEq7P3K03w",
"8928867947:AAEgwZ0YM-OWD_K2GamQbqdlyirvl7joZQQ",
"8836859336:AAE-ZVJttLrKEqaWgnasX_LSOSS8eEphrnQ",
"8672735723:AAHIh2opGisKoauT5Wv2OwefBBNoM0JGlPw",
"8931267007:AAHpQCQBpNhNNR70F3jJ6PIySiN5w1kZGT0",
"8787763692:AAF0Z2Zy9AmczQWKe7N_6kkC4JIrLxoC4sU",
"8698285629:AAGhnSRPbgyeaZqzU8xwrccsTA_kL7a2868",
    
]
SUDO_IDS = [] 

# ========== ABUSES  ==========
TIME_EMOJIS = ["🕗", "🕘", "🕙", "🕚", "🕛", "🕜", "🕝", "⏰", "🕠", "⏱", "🕡", "🕢", "⏳", "⌛", "🕣", "🕤", "🕥", "🕦", "🕧", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗"]

CUSTOM_HEARTS = ["♥️", "❣️", "❤️‍🔥", "💖", "🐕", "💓", "💕", "💝", "💘", "💞", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "❤️", "💔", "❤️‍🩹", "💌", "🩷", "🩵", "🩶"]

MID_ABUSES = [
    "(🥵) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂",
    "(😂) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🎀) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🐕) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(💥) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(☁️) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🪐) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🦢) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🔥) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🚬) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(😂) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🖤) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🫦) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
    "(🎀) {text} ႽᑭEᖇᗰ Kᕼᗩ Tᕼᗩᑎᗪᗩ ᕼOᒍᗩ 𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖????𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂??𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖😂𓀓𓂺 ࣪ ˖❄️𓀓𓂺 ࣪ ˖",
]

LOVE_ABUSES = [
    "{text} LODE 𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵 𒐫𒈙𒐫🩵𒈙𒐫𒈙🩵𒐫𒈙𒐫🩵{heart_loop}"
]

HUGE_ABUSES = [
     "{text} 𝗖ʜᴜᴅᴀɪ 𝗞𝗛𝗔 𝗥ꫝɴᴅɪᴋᴇ😂 𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫{time_loop}",
]

HUGE_ABUSES2 = [
    "{text} 𝙈𝘼𝘿𝘼𝙍𝘾𝙃⭕𝘿𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫{heart_loop}"
]

FLOWER_ABUSES = [
    "{text} कमजोर रण्डी 🐕🪷","{text} कमजोर रण्डी 🌸🪷","{text} कमजोर रण्डी 💮🪷","{text} कमजोर रण्डी 🏵️🪷","{text} कमजोर रण्डी 🌹🪷","{text} कमजोर रण्डी 🌺🪷","{text} कमजोर रण्डी 🌼🪷","{text} कमजोर रण्डी 🌷🪷","{text} कमजोर रण्डी 🌻🪷","{text} कमजोर रण्डी 🍁🪷","{text} कमजोर रण्डी 🌾🪷","{text} कमजोर रण्डी 🪷🪷"
]

rZ_ABUSES = [
    "(🤮) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🥵) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🕷️) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🦅) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🕊️) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🦋) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🚀) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(✈️) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🎀) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(✨) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🥁) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🪢) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(💸) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🧿) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🗿) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🔮) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(🔱) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(😡) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃?? 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 ",
    "(😝) {text} ᑕᕼᑌᑭ ᑭIᒪᒪᗴ (🤢+🌈) 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 <🤣-🪐𓂃🐕 𓂃 🌙-🥵>𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 𓂃🐕 𓂃 "
]

# ========== GLOBALS ==========
ALL_BOT_IDS = set()
ALL_BOTS = {}
BOT_START_TIMES = {}
SYSTEM_START_TIME = time.time()
KNOWN_CHATS = set()
GLOBAL_STATS = {"messages_sent":0, "name_changes":0, "replies_sent":0, "fwd_spam_sent":0}

# ========== UTILITY ==========
def extract_retry_after(error_str):
    match = re.search(r'retry after (\d+)', error_str.lower())
    return int(match.group(1)) if match else None

# ========== BOT INSTANCE ==========
class BotInstance:
    def __init__(self, bot_number, owner_id):
        self.bot_number = bot_number
        self.owner_id = owner_id
        self.sudo_users = set(SUDO_IDS)
        self.chat_delays = {}
        self.chat_threads = {}
        self.locks = {}
        self.proxies_list = []
        self.proxy = None
        self._load_proxies()

        # Active tasks per chat
        self.active_nc_tasks = {}      # key: (mode, chat_id) -> list of tasks
        self.active_spam_tasks = {}
        self.active_reply_tasks = {}
        self.active_reply_targets = {}
        self.pending_replies = {}
        self.active_rr_tasks = {}
        self.active_rr_targets = {}
        self.pending_rr_replies = {}
        self.active_rrspam_tasks = {}
        self.active_rrspam_targets = {}
        self.active_fwdspam_tasks = {}
        self.fwdspam_sources = {}
        self.active_multigc_tasks = {}
        
        self.saved_pictures = []       
        self.active_pic_tasks = {}     
        self.active_picspam_tasks = {} 
        
        self.customnc_running = False
        self.customnc_text = ""
        self.customnc_task = None
        self.customnc_chat_id = None
        self.customspam_running = False
        self.customspam_text = ""
        self.customspam_task = None
        self.customspam_chat_id = None

    def _load_proxies(self):
        if os.path.exists("proxies.txt"):
            with open("proxies.txt", "r") as f:
                self.proxies_list = [line.strip() for line in f if line.strip()]
            if self.proxies_list:
                self.proxy = random.choice(self.proxies_list)

    def is_owner(self, user_id):
        return user_id == self.owner_id or user_id in self.sudo_users

    async def check_owner(self, update):
        user_id = update.effective_user.id
        if not self.is_owner(user_id):
            try:
                await update.message.reply_text("Unauthorized.")
            except Exception:
                pass
            return False
        if update.effective_chat:
            KNOWN_CHATS.add(update.effective_chat.id)
        return True

    def get_lock(self, chat_id):
        if chat_id not in self.locks:
            self.locks[chat_id] = asyncio.Lock()
        return self.locks[chat_id]

    # ---------- HELP ----------
    async def start(self, update, context):
        if not await self.check_owner(update):
            return

        help_text = """
                       sumit ᴠ6 🎀
⟨ ❄️ ⟩᥊-7 𝘴ꪊꪑ𝓲𝓽 ⟨ ❄️ ⟩

╭⧼ ⚡ NC ᴍᴏᴅᴇs (ɢʀᴏᴜᴘ ɴᴀᴍᴇ ʟᴏᴏᴘ) ⧽
│ ◈ +nc1 <text>     ⤷ 🟢 ᴍɪᴅ ᴀʙᴜsᴇ
│ ◈ +nc2 <text>     ⤷ 🟢 ʟᴏᴠᴇ ᴀʙᴜsᴇ
│ ◈ +nc3 <text>     ⤷ 🟢 ʜᴜɢᴇ ᴀʙᴜsᴇ
│ ◈ +bignc <text>   ⤷ 🟢 ʜᴜɢᴇ ᴀʙᴜsᴇ2
│ ◈ +smlnc <text>   ⤷ 🟢 ғʟᴏᴡᴇʀ ᴀʙᴜsᴇ
│ ◈ +rznc <text>    ⤷ 🟢 ɴᴏ ʟɪᴍɪᴛ (1.8s 1ʙʏ1)
│ ◈ +customnc <text>⤷ 🟢 ᴄᴜsᴛᴏᴍ ᴛᴇxᴛ ᴡɪᴛʜ ʜᴇᴀʀᴛ ʟᴏᴏᴘ
│ ◈ -customnc       ⤷ 🔴 sᴛᴏᴘ ᴄᴜsᴛᴏᴍ ɴᴄ
│ ◈ -nc1/-nc2 ᴇᴛᴄ  ⤷ 🔴 ᴅɪsᴀʙʟᴇ ᴛʜᴀᴛ ɴᴄ ʟᴏᴏᴘ
╰──────────────╯

╭⧼ 📸 Pɪᴄᴛᴜʀᴇ ᴄᴏᴍᴍᴀɴᴅs ⧽
│ ◈ +save          ⤷ 🟢 sᴀᴠᴇ ᴘʜᴏᴛᴏ (ʀᴇᴘʟʏ)
│ ◈ -save          ⤷ 🔴 ᴄʟᴇᴀʀ ᴀʟʟ sᴀᴠᴇᴅ
│ ◈ +pic           ⤷ 🟢 ᴘғᴘ ʟᴏᴏᴘ (ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ)
│ ◈ -pic           ⤷ 🔴 sᴛᴏᴘ ᴘғᴘ ʟᴏᴏᴘ
│ ◈ +picspam       ⤷ 🟢 sᴘᴀᴍ sᴀᴠᴇᴅ ᴘɪᴄs
│ ◈ -picspam       ⤷ 🔴 sᴛᴏᴘ ᴘɪᴄ sᴘᴀᴍ
╰──────────────╯

╭⧼ 💬 Sᴘᴀᴍ / Rᴇᴘʟʏ / Rʀ / Mᴜʟᴛɪɢᴄ / Fᴡᴅ ⧽
│ ◈ .spam <target>     ⤷ 🟢 sᴘᴀᴍ ᴛᴀʀɢᴇᴛ
│ ◈ .stopspam          ⤷ 🔴 sᴛᴏᴘ sᴘᴀᴍ
│ ◈ .reply <target>    ⤷ 🟢 ʀᴇᴘʟʏ ᴛᴏ ᴇᴠᴇʀʏ ᴍᴇssᴀɢᴇ
│ ◈ .stopreply         ⤷ 🔴 sᴛᴏᴘ ʀᴇᴘʟʏ ʟᴏᴏᴘ
│ ◈ .rr (ʀᴇᴘʟʏ ᴛᴏ ᴍsɢ)⤷ 🟢 ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴜsᴇʀ
│ ◈ .stoprr            ⤷ 🔴 sᴛᴏᴘ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ
│ ◈ .rrspam (ʀᴇᴘʟʏ)   ⤷ 🟢 sᴘᴀᴍ ʀᴇᴘʟɪᴇs ᴛᴏ ᴛʜᴀᴛ ᴍsɢ
│ ◈ .stoprrspam        ⤷ 🔴 sᴛᴏᴘ ʀʀsᴘᴀᴍ
│ ◈ .multigc <target>  ⤷ 🟢 ɴᴄ+sᴘᴀᴍ+ᴘғᴘ ɪɴ ᴛʜɪs ᴄʜᴀᴛ
│ ◈ .stopmultigc       ⤷ 🔴 sᴛᴏᴘ ᴍᴜʟᴛɪɢᴄ
│ ◈ .fwdspam (ʀᴇᴘʟʏ/ʟɪɴᴋ) ⤷ 🟢 ғᴏʀᴡᴀʀᴅ sᴘᴀᴍ
│ ◈ .stopfwdspam       ⤷ 🔴 sᴛᴏᴘ ғᴏʀᴡᴀʀᴅ sᴘᴀᴍ
╰──────────────╯

╭⧼ 👑 Aᴅᴍɪɴ / Uᴛɪʟɪᴛʏ ⧽
│ ◈ .upadmin       ⤷ 🟢 ᴘʀᴏᴍᴏᴛᴇ ᴀʟʟ ʙᴏᴛs ᴛᴏ ᴀᴅᴍɪɴ
│ ◈ .leaveall      ⤷ 🟢 ʟᴇᴀᴠᴇ ᴛʜɪs ɢʀᴏᴜᴘ
│ ◈ .lock          ⤷ 🟢 ʟᴏᴄᴋ ᴄʜᴀᴛ (ɴᴏ ᴍᴇssᴀɢᴇs)
│ ◈ .unlock        ⤷ 🟢 ᴜɴʟᴏᴄᴋ ᴄʜᴀᴛ
│ ◈ .broadcast <msg> ⤷ 🟢 sᴇɴᴅ ᴛᴏ ᴀʟʟ ᴋɴᴏᴡɴ ᴄʜᴀᴛs
│ ◈ .delay <sec>   ⤷ 🟢 sᴇᴛ ʟᴏᴏᴘ ᴅᴇʟᴀʏ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ
│ ◈ .threads <num> ⤷ 🟢 sᴇᴛ ᴛʜʀᴇᴀᴅ ᴄᴏᴜɴᴛ (1‑50)
│ ◈ .sudo @user    ⤷ 🟢 ɢʀᴀɴᴛ sᴜᴅᴏ (ᴏᴡɴᴇʀ ᴏɴʟʏ)
│ ◈ .refresh       ⤷ 🟢 ᴄʜᴇᴄᴋ ʙᴏᴛ ᴀᴄᴛɪᴠᴇ
│ ◈ .join / .joinall ⤷ 🟢 (sɪᴍᴘʟɪғɪᴇᴅ)
│ ◈ .stopall       ⤷ 🔴 sᴛᴏᴘ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ʟᴏᴏᴘs ɪɴ ᴛʜɪs ᴄʜᴀᴛ
│ ◈ .stats         ⤷ 🟢 sʜᴏᴡ ɢʟᴏʙᴀʟ sᴛᴀᴛs
│ ◈ .ping          ⤷ 🟢 ʟᴀᴛᴇɴᴄʏ ᴛᴇsᴛ
│ ◈ .uptime        ⤷ 🟢 ʙᴏᴛ ᴜᴘᴛɪᴍᴇ
│ ◈ /delay <sec>   ⤷ 🟢 ᴀʟɪᴀs ғᴏʀ .ᴅᴇʟᴀʏ
│ ◈ /leave         ⤷ 🟢 ᴀʟɪᴀs ғᴏʀ .ʟᴇᴀᴠᴇᴀʟʟ
╰──────────────╯
"""
        await update.message.reply_text(help_text)

    # ---------- NC LOOPS (from v4fix) ----------
    async def _nc_loop(self, chat_id, mode, base_text, context):
        if mode == 'nc1': lines = MID_ABUSES
        elif mode == 'nc2': lines = LOVE_ABUSES
        elif mode == 'nc3': lines = HUGE_ABUSES
        elif mode == 'bignc': lines = HUGE_ABUSES2
        elif mode == 'smlnc': lines = FLOWER_ABUSES
        elif mode == 'rznc': lines = rZ_ABUSES
        else: return

        time_idx = 0
        while True:
            delay = self.chat_delays.get(chat_id, 0)
            try:
                line = random.choice(lines)
                if mode == 'nc3':
                    current_time = TIME_EMOJIS[time_idx % len(TIME_EMOJIS)]
                    time_idx += 1
                    line = line.replace("{time_loop}", current_time)
                if mode == 'bignc':
                    heart = random.choice(CUSTOM_HEARTS)
                    line = line.replace("{heart_loop}", heart)
                title = line.replace("{text}", base_text)[:120]
                await context.bot.set_chat_title(chat_id=chat_id, title=title)
                GLOBAL_STATS["name_changes"] += 1
                if delay > 0:
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
            except Exception:
                await asyncio.sleep(2)

    async def nc_command(self, update, context, mode):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only works in groups!")
            return
        if not context.args:
            await update.message.reply_text(f"Usage: /{mode} <text>")
            return
        base_text = " ".join(context.args)
        chat_id = chat.id

        key = (mode, chat_id)
        if key in self.active_nc_tasks:
            for task in self.active_nc_tasks[key]:
                task.cancel()
            del self.active_nc_tasks[key]

        threads = self.chat_threads.get(chat_id, 1)
        tasks = []
        for i in range(threads):
            task = asyncio.create_task(self._nc_loop(chat_id, mode, base_text, context))
            tasks.append(task)
        self.active_nc_tasks[key] = tasks
        await update.message.reply_text(f"✅ {mode.upper()} started for {base_text} with {threads} threads.")

    async def stop_nc_command(self, update, context, mode):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        key = (mode, chat_id)
        if key in self.active_nc_tasks:
            for task in self.active_nc_tasks[key]:
                task.cancel()
            del self.active_nc_tasks[key]
            await update.message.reply_text(f"🛑 {mode.upper()} stopped.")
        else:
            await update.message.reply_text(f"No active {mode.upper()} loop.")

    # ---------- CUSTOM NC (heart loop) ----------
    async def _custom_nc_loop(self, chat_id, base_text, context):
        while self.customnc_running and self.customnc_chat_id == chat_id:
            try:
                heart = random.choice(CUSTOM_HEARTS)
                
                if re.search(r'[♥️❣️❤️‍🔥💖🐕💓💕💝💘💞🧡💛💚💙💜🖤🤍🤎❤️💔❤️‍🩹💌🩷🩵🩶]+$', base_text):
                    new_title = re.sub(r'[♥️❣️❤️‍🔥💖🐕💓💕💝💘💞🧡💛💚💙💜🖤🤍🤎❤️💔❤️‍🩹💌🩷🩵🩶]+$', heart, base_text)
                else:
                    new_title = base_text + heart
                new_title = new_title[:120]
                await context.bot.set_chat_title(chat_id=chat_id, title=new_title)
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def customnc_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not context.args:
            await update.message.reply_text("Usage: /customnc <text>")
            return
        base_text = " ".join(context.args)
        chat_id = chat.id

        if self.customnc_running:
            self.customnc_running = False
            if self.customnc_task:
                self.customnc_task.cancel()
                await asyncio.sleep(0.5)

        self.customnc_running = True
        self.customnc_text = base_text
        self.customnc_chat_id = chat_id
        self.customnc_task = asyncio.create_task(self._custom_nc_loop(chat_id, base_text, context))
        await update.message.reply_text(f"✅ Custom NC started: {base_text[:50]}...")

    async def stop_customnc_command(self, update, context):
        if not await self.check_owner(update): return
        self.customnc_running = False
        if self.customnc_task:
            self.customnc_task.cancel()
            self.customnc_task = None
        self.customnc_chat_id = None
        await update.message.reply_text("🛑 Custom NC stopped.")

    # ---------- CUSTOM SPAM ----------
    async def _custom_spam_loop(self, chat_id, spam_text, context):
        while self.customspam_running and self.customspam_chat_id == chat_id:
            try:
                await context.bot.send_message(chat_id=chat_id, text=spam_text)
                GLOBAL_STATS["messages_sent"] += 1
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def customspam_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not context.args:
            await update.message.reply_text("Usage: /customspam <text>")
            return
        spam_text = " ".join(context.args)
        chat_id = chat.id

        if self.customspam_running:
            self.customspam_running = False
            if self.customspam_task:
                self.customspam_task.cancel()
                await asyncio.sleep(0.5)

        self.customspam_running = True
        self.customspam_text = spam_text
        self.customspam_chat_id = chat_id
        self.customspam_task = asyncio.create_task(self._custom_spam_loop(chat_id, spam_text, context))
        await update.message.reply_text(f"✅ Custom Spam started: {spam_text[:50]}...")

    async def stop_customspam_command(self, update, context):
        if not await self.check_owner(update): return
        self.customspam_running = False
        if self.customspam_task:
            self.customspam_task.cancel()
            self.customspam_task = None
        self.customspam_chat_id = None
        await update.message.reply_text("🛑 Custom Spam stopped.")

    # ---------- PICTURE COMMANDS ----------
    async def save_command(self, update, context):
        if not await self.check_owner(update): return
        if update.message.reply_to_message and update.message.reply_to_message.photo:
            try:
                photo = update.message.reply_to_message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                img = await file.download_as_bytearray()
                self.saved_pictures.append(bytes(img))
                await update.message.reply_text(f"✅ Picture saved! Total: {len(self.saved_pictures)}")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
        else:
            await update.message.reply_text("Reply to a photo with +save.")

    async def clear_save_command(self, update, context):
        if not await self.check_owner(update): return
        self.saved_pictures.clear()
        await update.message.reply_text("🗑️ All saved pictures cleared.")

    async def pic_loop(self, chat_id, context):
        while True:
            if not self.saved_pictures:
                await asyncio.sleep(2)
                continue
            delay = self.chat_delays.get(chat_id, 0)
            try:
                pic_bytes = random.choice(self.saved_pictures)
                await context.bot.set_chat_photo(chat_id=chat_id, photo=io.BytesIO(pic_bytes))
                if delay > 0:
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(2)

    async def pic_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not self.saved_pictures:
            await update.message.reply_text("No pictures saved. Use +save first.")
            return
        chat_id = chat.id
        if chat_id in self.active_pic_tasks:
            self.active_pic_tasks[chat_id].cancel()
        task = asyncio.create_task(self.pic_loop(chat_id, context))
        self.active_pic_tasks[chat_id] = task
        await update.message.reply_text("🖼️ PFP loop started.")

    async def stop_pic_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_pic_tasks:
            self.active_pic_tasks[chat_id].cancel()
            del self.active_pic_tasks[chat_id]
            await update.message.reply_text("🛑 PFP loop stopped.")
        else:
            await update.message.reply_text("No PFP loop active.")

    async def picspam_loop(self, chat_id, context):
        while True:
            if not self.saved_pictures:
                await asyncio.sleep(2)
                continue
            delay = self.chat_delays.get(chat_id, 0)
            try:
                pic_bytes = random.choice(self.saved_pictures)
                await context.bot.send_photo(chat_id=chat_id, photo=io.BytesIO(pic_bytes))
                GLOBAL_STATS["messages_sent"] += 1
                if delay > 0:
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def picspam_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not self.saved_pictures:
            await update.message.reply_text("No pictures saved.")
            return
        chat_id = chat.id
        if chat_id in self.active_picspam_tasks:
            self.active_picspam_tasks[chat_id].cancel()
        task = asyncio.create_task(self.picspam_loop(chat_id, context))
        self.active_picspam_tasks[chat_id] = task
        await update.message.reply_text("🖼️ Picture spam started.")

    async def stop_picspam_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_picspam_tasks:
            self.active_picspam_tasks[chat_id].cancel()
            del self.active_picspam_tasks[chat_id]
            await update.message.reply_text("🛑 Picture spam stopped.")
        else:
            await update.message.reply_text("No picture spam active.")

    # ---------- SPAM/REPLY/RR  ----------
    async def spam_loop(self, chat_id, target, context, worker_id):
        templates = [SPAM_MESSAGE_TEMPLATE, SPAM_MESSAGE_2, SPAM_MESSAGE_3]
        idx = 0
        while True:
            delay = self.chat_delays.get(chat_id, 0)
            try:
                msg = templates[idx % len(templates)].format(target=target)
                await context.bot.send_message(chat_id=chat_id, text=msg)
                GLOBAL_STATS["messages_sent"] += 1
                idx += 1
                if delay > 0:
                    await asyncio.sleep(delay)
            except asyncio.CancelledError:
                break
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except Exception:
                await asyncio.sleep(1)

    async def spam_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not context.args:
            await update.message.reply_text("Usage: .spam <target>")
            return
        target = " ".join(context.args)
        chat_id = chat.id
        if chat_id in self.active_spam_tasks:
            for t in self.active_spam_tasks[chat_id]:
                t.cancel()
        threads = self.chat_threads.get(chat_id, 1)
        tasks = []
        for i in range(threads):
            tasks.append(asyncio.create_task(self.spam_loop(chat_id, target, context, i+1)))
        self.active_spam_tasks[chat_id] = tasks
        await update.message.reply_text(f"💣 Spam started for {target} with {threads} threads.")

    async def stop_spam_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_spam_tasks:
            for t in self.active_spam_tasks[chat_id]:
                t.cancel()
            del self.active_spam_tasks[chat_id]
            await update.message.reply_text("🛑 Spam stopped.")
        else:
            await update.message.reply_text("No active spam.")

    # ---------- REPLY ----------
    async def reply_loop(self, chat_id, target, context):
        while True:
            delay = self.chat_delays.get(chat_id, 0)
            if chat_id in self.pending_replies and self.pending_replies[chat_id]:
                async with self.get_lock(chat_id):
                    msgs = self.pending_replies[chat_id].copy()
                    self.pending_replies[chat_id] = []
                for msg_id in msgs:
                    try:
                        msg = random.choice(REPLY_MESSAGES).format(target=target)
                        await context.bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                        GLOBAL_STATS["replies_sent"] += 1
                        if delay > 0:
                            await asyncio.sleep(delay)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.5)

    async def reply_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not context.args:
            await update.message.reply_text("Usage: .reply <target>")
            return
        target = " ".join(context.args)
        chat_id = chat.id
        if chat_id in self.active_reply_tasks:
            self.active_reply_tasks[chat_id].cancel()
        self.active_reply_targets[chat_id] = target
        self.pending_replies[chat_id] = []
        task = asyncio.create_task(self.reply_loop(chat_id, target, context))
        self.active_reply_tasks[chat_id] = task
        await update.message.reply_text(f"💬 Reply loop started for {target}.")

    async def stop_reply_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_reply_tasks:
            self.active_reply_tasks[chat_id].cancel()
            del self.active_reply_tasks[chat_id]
            self.active_reply_targets.pop(chat_id, None)
            self.pending_replies.pop(chat_id, None)
            await update.message.reply_text("🛑 Reply loop stopped.")
        else:
            await update.message.reply_text("No active reply loop.")

    # ---------- RR ----------
    async def rr_loop(self, chat_id, target_user_id, context):
        while True:
            if chat_id in self.pending_rr_replies and self.pending_rr_replies[chat_id]:
                async with self.get_lock(chat_id):
                    msgs = self.pending_rr_replies[chat_id].copy()
                    self.pending_rr_replies[chat_id] = []
                for msg_id in msgs:
                    try:
                        msg = random.choice(RR_MESSAGES)
                        await context.bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                        if self.chat_delays.get(chat_id, 0) > 0:
                            await asyncio.sleep(self.chat_delays[chat_id])
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.5)

    async def rr_command(self, update, context):
        if not await self.check_owner(update): return
        if not update.message.reply_to_message:
            await update.message.reply_text("Reply to a message with .rr")
            return
        chat_id = update.effective_chat.id
        target_user = update.message.reply_to_message.from_user
        if not target_user:
            await update.message.reply_text("Could not identify user.")
            return
        target_id = target_user.id
        if chat_id in self.active_rr_tasks:
            self.active_rr_tasks[chat_id].cancel()
        self.active_rr_targets[chat_id] = target_id
        self.pending_rr_replies[chat_id] = []
        task = asyncio.create_task(self.rr_loop(chat_id, target_id, context))
        self.active_rr_tasks[chat_id] = task
        try:
            msg = random.choice(RR_MESSAGES)
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=update.message.reply_to_message.message_id)
        except: pass
        await update.message.reply_text("🔁 RR started.")

    async def stop_rr_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_rr_tasks:
            self.active_rr_tasks[chat_id].cancel()
            del self.active_rr_tasks[chat_id]
            self.active_rr_targets.pop(chat_id, None)
            self.pending_rr_replies.pop(chat_id, None)
            await update.message.reply_text("🛑 RR stopped.")
        else:
            await update.message.reply_text("No active RR.")

    # ---------- RRSPAM ----------
    async def rrspam_loop(self, chat_id, msg_id, context):
        while True:
            delay = self.chat_delays.get(chat_id, 0)
            try:
                msg = random.choice(RR_MESSAGES)
                await context.bot.send_message(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
                GLOBAL_STATS["messages_sent"] += 1
                if delay > 0:
                    await asyncio.sleep(delay)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def rrspam_command(self, update, context):
        if not await self.check_owner(update): return
        if not update.message.reply_to_message:
            await update.message.reply_text("Reply to a message with .rrspam")
            return
        chat_id = update.effective_chat.id
        msg_id = update.message.reply_to_message.message_id
        if chat_id in self.active_rrspam_tasks:
            self.active_rrspam_tasks[chat_id].cancel()
        task = asyncio.create_task(self.rrspam_loop(chat_id, msg_id, context))
        self.active_rrspam_tasks[chat_id] = task
        self.active_rrspam_targets[chat_id] = (update.message.reply_to_message.from_user.id, msg_id)
        await update.message.reply_text("💥 RRSPAM started.")

    async def stop_rrspam_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_rrspam_tasks:
            self.active_rrspam_tasks[chat_id].cancel()
            del self.active_rrspam_tasks[chat_id]
            self.active_rrspam_targets.pop(chat_id, None)
            await update.message.reply_text("🛑 RRSPAM stopped.")
        else:
            await update.message.reply_text("No active RRSPAM.")

    # ---------- MULTIGC ----------
    async def multigc_nc_loop(self, chat_id, target, context):
        lines = MULTIGC_NC_MESSAGES
        idx = 0
        while True:
            try:
                title = lines[idx % len(lines)].format(target=target)
                await context.bot.set_chat_title(chat_id=chat_id, title=title)
                idx += 1
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def multigc_spam_loop(self, chat_id, target, context):
        lines = MULTIGC_SPAM_MESSAGES
        idx = 0
        while True:
            try:
                msg = lines[idx % len(lines)].format(target=target)
                await context.bot.send_message(chat_id=chat_id, text=msg)
                idx += 1
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def multigc_gc_loop(self, chat_id, context):
        while True:
            if not self.saved_pictures:
                await asyncio.sleep(2)
                continue
            try:
                pic_bytes = random.choice(self.saved_pictures)
                await context.bot.set_chat_photo(chat_id=chat_id, photo=io.BytesIO(pic_bytes))
                await asyncio.sleep(2)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(2)

    async def multigc_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        if not context.args:
            await update.message.reply_text("Usage: .multigc <target>")
            return
        target = " ".join(context.args)
        chat_id = chat.id
        if chat_id in self.active_multigc_tasks:
            for t in self.active_multigc_tasks[chat_id]:
                t.cancel()
        tasks = []
        tasks.append(asyncio.create_task(self.multigc_nc_loop(chat_id, target, context)))
        tasks.append(asyncio.create_task(self.multigc_spam_loop(chat_id, target, context)))
        tasks.append(asyncio.create_task(self.multigc_gc_loop(chat_id, context)))
        self.active_multigc_tasks[chat_id] = tasks
        await update.message.reply_text("💥 MULTIGC started (NC+Spam+PFP).")

    async def stop_multigc_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_multigc_tasks:
            for t in self.active_multigc_tasks[chat_id]:
                t.cancel()
            del self.active_multigc_tasks[chat_id]
            await update.message.reply_text("🛑 MULTIGC stopped.")
        else:
            await update.message.reply_text("No active MULTIGC.")

    # ---------- FWDSPAM ----------
    async def fwdspam_loop(self, chat_id, from_chat_id, msg_id, context):
        while True:
            delay = self.chat_delays.get(chat_id, 0)
            try:
                await context.bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=msg_id)
                GLOBAL_STATS["fwd_spam_sent"] += 1
                if delay > 0:
                    await asyncio.sleep(delay)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1)

    async def fwdspam_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        msg = update.message
        from_chat_id = None
        msg_id = None
        if msg.reply_to_message:
            from_chat_id = chat_id
            msg_id = msg.reply_to_message.message_id
        elif context.args:
            link = context.args[0]
            m = re.search(r't\.me/c/(\d+)/(\d+)', link)
            if m:
                from_chat_id = int(f"-100{m.group(1)}")
                msg_id = int(m.group(2))
        if from_chat_id is None or msg_id is None:
            await msg.reply_text("Reply to a message or provide t.me/c/chatid/msgid")
            return
        if chat_id in self.active_fwdspam_tasks:
            self.active_fwdspam_tasks[chat_id].cancel()
        task = asyncio.create_task(self.fwdspam_loop(chat_id, from_chat_id, msg_id, context))
        self.active_fwdspam_tasks[chat_id] = task
        self.fwdspam_sources[chat_id] = (from_chat_id, msg_id)
        await msg.reply_text("📨 FwdSpam started.")

    async def stop_fwdspam_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        if chat_id in self.active_fwdspam_tasks:
            self.active_fwdspam_tasks[chat_id].cancel()
            del self.active_fwdspam_tasks[chat_id]
            self.fwdspam_sources.pop(chat_id, None)
            await update.message.reply_text("🛑 FwdSpam stopped.")
        else:
            await update.message.reply_text("No active FwdSpam.")

    # ---------- ADMIN COMMANDS ----------
    async def upadmin_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        me = await context.bot.get_me()
        target_ids = [bid for bid in ALL_BOT_IDS if bid != me.id]
        if not target_ids:
            await update.message.reply_text("No other bots registered.")
            return
        promoted = 0
        for bot_id in target_ids:
            try:
                await context.bot.promote_chat_member(
                    chat.id, bot_id,
                    can_change_info=True, can_delete_messages=True,
                    can_invite_users=True, can_restrict_members=True,
                    can_pin_messages=True, can_promote_members=True,
                    can_manage_chat=True, can_manage_video_chats=True
                )
                promoted += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Promoted {promoted} bot(s) to admin.")

    async def leaveall_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        for bot_obj in ALL_BOTS.values():
            try:
                await bot_obj.leave_chat(chat_id)
            except:
                pass
        await update.message.reply_text("👋 Left the group from all bots.")

    async def lock_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        no_perms = ChatPermissions(
            can_send_messages=False, can_send_polls=False,
            can_send_other_messages=False, can_add_web_page_previews=False,
            can_change_info=False, can_invite_users=False, can_pin_messages=False
        )
        for bot_obj in ALL_BOTS.values():
            try:
                await bot_obj.set_chat_permissions(chat.id, no_perms)
                await update.message.reply_text("🔒 Chat locked.")
                return
            except:
                pass
        await update.message.reply_text("Failed to lock.")

    async def unlock_command(self, update, context):
        if not await self.check_owner(update): return
        chat = update.effective_chat
        if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            await update.message.reply_text("Only groups!")
            return
        perms = ChatPermissions(
            can_send_messages=True, can_send_polls=True,
            can_send_other_messages=True, can_add_web_page_previews=True,
            can_change_info=False, can_invite_users=True, can_pin_messages=False
        )
        for bot_obj in ALL_BOTS.values():
            try:
                await bot_obj.set_chat_permissions(chat.id, perms)
                await update.message.reply_text("🔓 Chat unlocked.")
                return
            except:
                pass
        await update.message.reply_text("Failed to unlock.")

    async def broadcast_command(self, update, context):
        if not await self.check_owner(update): return
        if not context.args:
            await update.message.reply_text("Usage: .broadcast <msg>")
            return
        text = " ".join(context.args)
        total = len(KNOWN_CHATS) * len(ALL_BOTS)
        sent = 0
        for chat_id in list(KNOWN_CHATS):
            for bot_obj in ALL_BOTS.values():
                try:
                    await bot_obj.send_message(chat_id=chat_id, text=text)
                    sent += 1
                    await asyncio.sleep(0.05)
                except:
                    pass
        await update.message.reply_text(f"📢 Broadcast sent to {sent} chats.")

    async def delay_command(self, update, context):
        if not await self.check_owner(update): return
        if not context.args:
            await update.message.reply_text("Usage: .delay <seconds>")
            return
        try:
            d = float(context.args[0])
            if d < 0: raise ValueError
            self.chat_delays[update.effective_chat.id] = d
            await update.message.reply_text(f"⏱️ Delay set to {d}s for this chat.")
        except:
            await update.message.reply_text("Invalid delay.")

    async def threads_command(self, update, context):
        if not await self.check_owner(update): return
        if not context.args:
            await update.message.reply_text("Usage: .threads <number>")
            return
        try:
            t = int(context.args[0])
            if t < 1 or t > 50: raise ValueError
            self.chat_threads[update.effective_chat.id] = t
            await update.message.reply_text(f"🧵 Threads set to {t}.")
        except:
            await update.message.reply_text("Invalid number (1-50).")

    async def stopall_command(self, update, context):
        if not await self.check_owner(update): return
        chat_id = update.effective_chat.id
        stopped = []
        # NC tasks
        for key in list(self.active_nc_tasks.keys()):
            if key[1] == chat_id:
                for t in self.active_nc_tasks[key]:
                    t.cancel()
                del self.active_nc_tasks[key]
                stopped.append(key[0])
        # Others
        for attr in ['active_spam_tasks','active_reply_tasks','active_rr_tasks','active_rrspam_tasks','active_fwdspam_tasks','active_multigc_tasks','active_pic_tasks','active_picspam_tasks']:
            d = getattr(self, attr, {})
            if chat_id in d:
                if isinstance(d[chat_id], list):
                    for t in d[chat_id]:
                        t.cancel()
                else:
                    d[chat_id].cancel()
                del d[chat_id]
                stopped.append(attr.replace('active_','').replace('_tasks',''))
        # Custom NC and spam
        if self.customnc_running and self.customnc_chat_id == chat_id:
            self.customnc_running = False
            if self.customnc_task:
                self.customnc_task.cancel()
                self.customnc_task = None
            stopped.append("customnc")
        if self.customspam_running and self.customspam_chat_id == chat_id:
            self.customspam_running = False
            if self.customspam_task:
                self.customspam_task.cancel()
                self.customspam_task = None
            stopped.append("customspam")
        if stopped:
            await update.message.reply_text(f"🛑 Stopped: {', '.join(stopped)}")
        else:
            await update.message.reply_text("No active loops.")

    async def stats_command(self, update, context):
        if not await self.check_owner(update): return
        msg = f"📊 Stats:\nMessages Sent: {GLOBAL_STATS['messages_sent']}\nName Changes: {GLOBAL_STATS['name_changes']}\nReplies Sent: {GLOBAL_STATS['replies_sent']}\nFwd Spam: {GLOBAL_STATS['fwd_spam_sent']}"
        await update.message.reply_text(msg)

    async def ping_command(self, update, context):
        if not await self.check_owner(update): return
        start = time.time()
        await update.message.reply_text("Pong!")
        latency = (time.time() - start) * 1000
        await update.message.reply_text(f"🏓 {latency:.2f}ms")

    async def uptime_command(self, update, context):
        if not await self.check_owner(update): return
        uptime = int(time.time() - SYSTEM_START_TIME)
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        mins = (uptime % 3600) // 60
        secs = uptime % 60
        await update.message.reply_text(f"⏰ Uptime: {days}d {hours}h {mins}m {secs}s")

    async def sudo_command(self, update, context):
        if update.effective_user.id != self.owner_id:
            return
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("Reply to a user with .sudo")
            return
        user_id = None
        if update.message.reply_to_message:
            user_id = update.message.reply_to_message.from_user.id
        else:
            try:
                user_id = int(context.args[0])
            except:
                await update.message.reply_text("Invalid ID.")
                return
        self.sudo_users.add(user_id)
        await update.message.reply_text(f"✅ Sudo added for {user_id}")

    async def refresh_command(self, update, context):
        if not await self.check_owner(update): return
        await update.message.reply_text("Bot is active.")

    async def join_command(self, update, context):
        if not await self.check_owner(update): return
        await update.message.reply_text("Join command not implemented.")

    async def joinall_command(self, update, context):
        if not await self.check_owner(update): return
        await update.message.reply_text("Joinall not implemented.")

    # ---------- MESSAGE COLLECTOR ----------
    async def message_collector(self, update, context):
        msg = update.message or update.channel_post
        if not msg: return
        chat_id = update.effective_chat.id

        if chat_id in self.active_reply_targets:
            self.pending_replies.setdefault(chat_id, []).append(msg.message_id)

        if chat_id in self.active_rr_targets:
            sender = msg.from_user
            if sender and sender.id == self.active_rr_targets[chat_id]:
                self.pending_rr_replies.setdefault(chat_id, []).append(msg.message_id)

# ========== SPAM MESSAGES  ==========
SPAM_MESSAGE_TEMPLATE = """{target} Tᴇʀɪ Mᴀᴀ Cʜᴏᴅ Dᴀʟᴇɴɢᴇ ʀᴇ ─•────➤ ┆ ⤿🌀""" * 12
SPAM_MESSAGE_2 = """ {target} Dᴇʜᴋ Tᴇʀɪ Mᴀᴀ ᴋᴀ Bᴀʀᴄᴏᴅᴇ Jᴀɪsᴇ ʜɪ sᴄᴀɴ ʜᴏɢᴀ ᴛᴇʀɪ ᴍᴀᴀ ᴍʀᴊᴀʏᴇɢɪ 🌙 ↳ 𝄃𝄃𝄂𝄂𝄀𝄁𝄃𝄂𝄂𝄃""" * 12
SPAM_MESSAGE_3 = """ ˚˖𓍢ִ໋𑁍ּ ֶָ֢.─────୨ৎ────˚˖𓍢ִ໋𑁍ּ ֶָ֢.
˚˖𓍢ִ໋𑁍ּ ֶָ֢.  {target}        ˚˖𓍢ִ໋𑁍ּ ֶָ֢.
˚˖𓍢ִ໋𑁍ּ ֶָ֢.     Tᴇʀɪ 
˚˖𓍢ִ໋𑁍ּ ֶָ֢.           Mᴀ 
˚˖𓍢ִ໋𑁍ּ ֶָ֢.       ᴋᴇ 
˚˖𓍢ִ໋𑁍ּ ֶָ֢.           Cʜᴜᴅɴᴇ     
˚˖𓍢ִ໋𑁍ּ ֶָ֢.       Pᴀʀ       
˚˖𓍢ִ໋𑁍ּ ֶָ֢.    फूल बारसेएंगे ¡! 
˚˖𓍢ִ໋𑁍ּ ֶָ֢.
˚˖𓍢ִ໋𑁍ּ ֶָ֢.    मेई Aᴜʀ Mᴇʀᴇ दोस्त
˚˖𓍢ִ໋𑁍ּ ֶָ֢."""

RR_MESSAGES = [
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜. ㅅ ͜. )🥛 ʏᴜᴍᴍʏ ",
    "Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन Chod",
    "तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）",
    "तेरी माँ TELETHON से पैडा एच वी रंडी🩷🇵🇰💩",
    "𝐓ᴜ 𝐑ꫝꪀᴅ𝐈 ---×❤️×---",
    "Mar Gya Kya Mc",
    "TᴇʀI 𝐌ᴀA 𝐊ᴇ 𝐒ᴀᴛH 𝐗xx 𝐊ᴀR 𝐃ᴜɴɢA 😜😜🔥🔥😜🔥",
]

REPLY_MESSAGES = [
    "{target} 𝘍𝘈𝘜𝘑𝘐 𝘊𝘜𝘛𝘛𝘐𝘕𝘎 𝘞𝘈𝘓𝘌 𝘏𝘐𝘑𝘋𝘌 𝘗𝘌𝘏𝘓𝘌 𝘑𝘈𝘒𝘌 𝘈𝘗𝘕𝘐 𝘔𝘈𝘒𝘌 𝘑𝘏𝘈𝘛 𝘒𝘌 𝘉𝘈𝘈𝘓𝘖𝘕 𝘒𝘖 𝘞𝘖𝘓𝘍 𝘊𝘜𝘛 𝘒𝘙𝘞𝘈 😁🤟🏻💥❤️",
    "{target} 𝘊𝘏𝘜𝘋𝘈𝘐 𝘒𝘏𝘈𝘈 𝘔𝘋𝘊 𝘉𝘚𝘚 𝘛𝘜 🍭🍭🍭🍭",
    "{target} 𝘈𝘑𝘈 𝘛𝘙𝘠 𝘔𝘈𝘒𝘈 𝘉𝘏𝘖𝘚𝘋𝘈 𝘔𝘌𝘈𝘚𝘜𝘙𝘌 𝘒𝘙𝘜𝘕𝘎𝘈 😁🖖🏻📐📐",
    "{target} 𝘠𝘰 𝘞𝘢𝘯𝘯𝘢 𝘉𝘦 𝘌𝘯𝘨𝘭𝘪𝘴𝘩 𝘚𝘱𝘦𝘢𝘬𝘦𝘳 🔇 𝘵𝘮𝘬𝘤 𝘮 𝘴𝘪𝘳𝘦𝘯 𝘨𝘩𝘶𝘴𝘢 𝘥𝘶𝘯𝘨𝘢 𝘧𝘩𝘪𝘳 𝘫𝘢𝘣 𝘷 𝘵𝘶 𝘦𝘯𝘨𝘭𝘪𝘴𝘩 𝘣𝘰𝘭𝘦𝘨𝘢 𝘵𝘦𝘳𝘪 𝘮𝘢𝘢 𝘳𝘰 𝘥𝘦𝘨𝘪",
    "{target} 𝘒𝘢𝘭𝘪 𝘙𝘯𝘥𝘺𝘬𝘦 𝘉𝘈𝘊𝘊𝘏𝘌 𝐒ʜᴀʀ 𝘒𝘌 𝘚𝘈𝘔𝘕𝘌 𝘈𝘞𝘈𝘑 𝘜𝘛𝘏𝘈𝘠𝘌𝘎𝘈 𝘓𝘌 𝘊𝘏𝘜𝘋 🫯💘🩸💋👣",
    "{target} 🧑🏻‍🎤💃🏻🌹🌷𝘭𝘶𝘯𝘥 𝘤𝘩𝘶𝘴𝘴𝘦𝘳 𝘮𝘤",
]

MULTIGC_NC_MESSAGES = [
    " {target} ʟᴜꪀᴅᥴʜꫝᴛᴜ -(💭)-",
    "{target} Cʜɪꪀꫝʟ -(🥏)-",
    "{target} ᴄʜꪊᴅ -(🌀)-",
    "{target} ꪑꫝᴅꫝʀCʜꪮᴅ -(☢)-",
    "{target} ᴋꫝꪑᴊꪮʀ -(🌊)-",
    "{target} ʟꪊꪀᴅ ᥴʜᴜડ -(🧞‍♂️)-",
    "{target} ᴄʜꪊᴛꫝᴅ -(🏵️)-",
]

MULTIGC_SPAM_MESSAGES = [
    "{target} ᴋꫝꪑᴊꪮʀ ﴾🌙﴿ \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n {target} ᴋꫝꪑᴊꪮʀ ﴾🌙﴿ ",
    "{target} Cʜɪꪀꫝʟ ﴾🐕﴿ \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n {target} Cʜɪꪀꫝʟ ﴾🐕﴿",
    "{target} ʟᴜꪀᴅᥴʜꫝᴛᴜ ﴾❄️﴿ \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n {target} ʟᴜꪀᴅᥴʜꫝᴛᴜ ﴾❄️﴿",
]

# ========== BOT LAUNCH ==========
def create_application(token, bot_number):
    app = Application.builder().token(token).build()
    bot_instance = BotInstance(bot_number, OWNER_ID)

    # NC commands
    for mode in ['nc1','nc2','nc3','bignc','smlnc','rznc']:
        app.add_handler(CommandHandler(mode, lambda u,c,m=mode: bot_instance.nc_command(u,c,m)))
        app.add_handler(CommandHandler(f"stop{mode}", lambda u,c,m=mode: bot_instance.stop_nc_command(u,c,m)))

    # Custom NC and Spam
    app.add_handler(CommandHandler("customnc", bot_instance.customnc_command))
    app.add_handler(CommandHandler("stopcustomnc", bot_instance.stop_customnc_command))
    app.add_handler(CommandHandler("customspam", bot_instance.customspam_command))
    app.add_handler(CommandHandler("stopcustomspam", bot_instance.stop_customspam_command))

    # Picture
    app.add_handler(CommandHandler("save", bot_instance.save_command))
    app.add_handler(CommandHandler("stopsave", bot_instance.clear_save_command))
    app.add_handler(CommandHandler("pic", bot_instance.pic_command))
    app.add_handler(CommandHandler("stoppic", bot_instance.stop_pic_command))
    app.add_handler(CommandHandler("picspam", bot_instance.picspam_command))
    app.add_handler(CommandHandler("stoppicspam", bot_instance.stop_picspam_command))

    # Rayuga commands
    app.add_handler(CommandHandler("start", bot_instance.start))
    app.add_handler(CommandHandler("spam", bot_instance.spam_command))
    app.add_handler(CommandHandler("stopspam", bot_instance.stop_spam_command))
    app.add_handler(CommandHandler("reply", bot_instance.reply_command))
    app.add_handler(CommandHandler("stopreply", bot_instance.stop_reply_command))
    app.add_handler(CommandHandler("rr", bot_instance.rr_command))
    app.add_handler(CommandHandler("stoprr", bot_instance.stop_rr_command))
    app.add_handler(CommandHandler("rrspam", bot_instance.rrspam_command))
    app.add_handler(CommandHandler("stoprrspam", bot_instance.stop_rrspam_command))
    app.add_handler(CommandHandler("multigc", bot_instance.multigc_command))
    app.add_handler(CommandHandler("stopmultigc", bot_instance.stop_multigc_command))
    app.add_handler(CommandHandler("fwdspam", bot_instance.fwdspam_command))
    app.add_handler(CommandHandler("stopfwdspam", bot_instance.stop_fwdspam_command))
    app.add_handler(CommandHandler("upadmin", bot_instance.upadmin_command))
    app.add_handler(CommandHandler("leaveall", bot_instance.leaveall_command))
    app.add_handler(CommandHandler("lock", bot_instance.lock_command))
    app.add_handler(CommandHandler("unlock", bot_instance.unlock_command))
    app.add_handler(CommandHandler("broadcast", bot_instance.broadcast_command))
    app.add_handler(CommandHandler("delay", bot_instance.delay_command))
    app.add_handler(CommandHandler("threads", bot_instance.threads_command))
    app.add_handler(CommandHandler("stopall", bot_instance.stopall_command))
    app.add_handler(CommandHandler("stats", bot_instance.stats_command))
    app.add_handler(CommandHandler("ping", bot_instance.ping_command))
    app.add_handler(CommandHandler("uptime", bot_instance.uptime_command))
    app.add_handler(CommandHandler("sudo", bot_instance.sudo_command))
    app.add_handler(CommandHandler("refresh", bot_instance.refresh_command))
    app.add_handler(CommandHandler("join", bot_instance.join_command))
    app.add_handler(CommandHandler("joinall", bot_instance.joinall_command))

    # Aliases for delay and leave
    app.add_handler(CommandHandler("delay", bot_instance.delay_command))
    app.add_handler(CommandHandler("leave", bot_instance.leaveall_command))

    # Message collector for reply and rr
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, bot_instance.message_collector))

    return app

async def run_bot(token, bot_number):
    app = create_application(token, bot_number)
    try:
        await app.initialize()
        await app.start()
        me = await app.bot.get_me()
        ALL_BOT_IDS.add(me.id)
        ALL_BOTS[me.id] = app.bot
        BOT_START_TIMES[bot_number] = time.time()
        print(f"Bot {bot_number} started: @{me.username}")
        if app.updater:
            await app.updater.start_polling(drop_pending_updates=True)
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"Bot {bot_number} error: {e}")
    finally:
        if app.updater:
            await app.updater.stop()
        await app.stop()
        await app.shutdown()

async def keepalive_server():
    app_web = web.Application()
    app_web.router.add_get("/", lambda r: web.Response(text="OK"))
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 3000)
    await site.start()
    print("Keepalive server on port 3000")

async def main():
    print(f"Starting {len(BOT_TOKENS)} bots...")
    asyncio.create_task(keepalive_server())
    tasks = []
    for i, token in enumerate(BOT_TOKENS, 1):
        tasks.append(asyncio.create_task(run_bot(token, i)))
        await asyncio.sleep(0.1)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown.")