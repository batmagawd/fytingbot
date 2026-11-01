import asyncio
import time
import random
import re
from datetime import datetime
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ChatPermissions
try:
    from telegram import CopyTextButton
except ImportError:
    CopyTextButton = None
from telegram.error import TelegramError
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import RetryAfter
# ========================= MULTI BOT CONFIG =========================
BOT_TOKENS = [
"8600041613:AAGLQoUdtBoFNTqC9HXwMeSxxAzNamWhYgg",
"7639678823:AAGNJnIMvLg69RmdyyrYmzm7veg4Sl7V2Ow",
"8814978940:AAEWMAnC3ZGJHKVD-4HdnJVtX9JAhzijg7o",
"8719538849:AAE-hgkpK17lgOhGrh0_vgtheHEq7P3K03w",
"8928867947:AAEgwZ0YM-OWD_K2GamQbqdlyirvl7joZQQ",
"8629200436:AAEq_gSGmFfWu0IahHaZaqx27orwdi3DfbQ",
"8649599062:AAHsaywstu_OLpX1ECvXSYzy5wf0g-Ysb2Y",
"8927721901:AAEYfROGQ8p3Kv80X8bmivkussm6AvsdbXA",
"8961641953:AAHcI65UY06Y5mMhLtth6OJnsAq5dlQyU7w",
"8809301934:AAEKLMAadqSFIigqhpv8DG-4F5UWk1u1fFo"
]

OWNER_ID = 8572048945

# ====================== PHOTO STORAGE ======================
SAVED_PHOTOS = {}  # {group_id: [photo_file_ids]}
ACTIVE_PHOTO_LOOPS = {}  # {f"{group_id}_photo": asyncio.Task}

# ====================== GROUP TRACKING ======================
GROUP_TRACKER = {}  # {group_id: group_name}
TASK_START_TIMES = {}  # {task_key: start_time}
ACTIVE_GROUPS = set()  # Set of group IDs where bot is active

# ====================== ULTRA FAST CONFIG - NO DELAYS ======================
DELAYS = {
    'nc': 0,        # NO DELAY - INSTANT!
    'spam': 0,      # NO DELAY - MACHINE GUN!
    'swipe': 0,     # NO DELAY - LIGHTNING!
    'reply': 0,     # NO DELAY - SUPERSONIC!
}

# ====================== AUTO RESTART CONFIG ======================
AUTO_RESTART = False  # Disable auto restart - continuous loop is enough
RESTART_DELAY = 0    # Restart after 2 seconds

# ====================== 👥 FRIENDS & TEAM 👥 ======================
FRIENDS = {
    'creator': 'x7sᴜᴍɪᴛ',
}

# ====================== TEXT LISTS ======================
NC_TEXTS = {
    'snc': [
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇦🇨〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇦🇶〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇧🇲〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🏳️‍🌈〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇧🇱〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇧🇬〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇦🇪〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇧🇷〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇰🇮〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
        r"{target} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🇱🇰〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡"
    ],
    'ssnc': [
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🌀)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🔥)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(💀)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(⚡)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(😈)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(☠️)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🌪️)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(👑)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(💥)",
        r"{target}ᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷ᯓᯓ🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🚨)"
    ],
    'fnc': [
        r"˚⊱━━🍁━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━🔥━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━💀━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━⚡━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━😈━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━☠️━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━🌪️━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━👑━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━💥━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━🚨━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅"
    ],
    'cnc': [
        r"{target} Tᴇʀɪ ᴍꫝ 🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳🐳 Wʜꫝʟᴇ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄🦄 Uɴɪᴄᴏʀɴ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼 Pꫝɴᴅꫝ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒🐒 Mᴏɴᴋᴇʏ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍🦍 Gᴏʀɪʟʟꫝ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂🦂 Sᴄᴏʀᴘɪᴏɴ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺 Wᴏʟғ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊🐊 Cʀᴏᴄᴏᴅɪʟᴇ ᴄʜᴏᴅᴇɢꫝ 👀",
        r"{target} Tᴇʀɪ ᴍꫝ 🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏🦏 Rʜɪɴᴏ ᴄʜᴏᴅᴇɢꫝ 👀✨",
        r"{target} Tᴇʀɪ ᴍꫝ 🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🇯🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓🦓 Zᴇʙʀꫝ ᴄʜᴏᴅᴇɢꫝ 👀"
    ],
    'bnc': [
        r"✨ {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑💫",
        r"🌟 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑✨",
        r"🌀 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑💫",
        r"🔱 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙??𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑✨",
        r"🌈 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑??👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑💫",
        r"⭐ {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑✨",
        r"🫧 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑💫",
        r"🪩 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑✨",
        r"🪷 {target}  𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑💫",
        r"🌙 {target} 𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑𒈙👑✨"
    ],
    'sgcnc': [
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🥶ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🫤ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🤓ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😎ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🤢ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🤥ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😵ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🥺ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😡ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🙄ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😀ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🤔ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😑ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😷ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🥴ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😒ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🥵ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🤭ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴🫣ྀ࿐",
        r"ᎷᎯᎠᎯᏒᏨᎻᎾᎠ⁀➴😗ྀ࿐"
    ]
}

SPAM_TEXTS = {
    'bspam': [
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」"
    ],
    'aspam': [
        r"🤍{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   🤍",
        r" 🖤{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   🖤",
        r" 🤎{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   🤎",
        r" 💜{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   💜",
        r" 💙{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   💙",
        r" 🩵{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   🩵",
        r" 💚{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   💚",
        r" 💛{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   💛",
        r" 🧡{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   🧡",
        r" ❤️{target}  ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ   ❤️"
    ],
    'sspam': [
        r"{target}  CVR KR MC GAREEB 👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞 {target}  CVR KR MC GAREEB{target}  CVR KR MC GAREEB 👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞 {target}  CVR KR MC GAREEB {target}  CVR KR MC GAREEB 👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞 {target}  CVR KR MC GAREEB"
    ],
    'fspam': [
        r"࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐\n࿐💞➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳➳{target} 𝐓ᴇʀɪ 𝐌∆∆ 𝐂ʜ⭕ᴅ 𝐃∆ʟᴇɴ𝐆ᴇ ࿐"
    ],
    'gspam': [
        r"𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .\n\n𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼{target}   CHUDKAD                             𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ"
    ],
    'rspam': [
        r"{target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺𝐒υмιт 𝑲𝑨 कुतिया के 🥂🌙"
    ]
}

SWIPE_TEXTS = {
    'aswipe': [
        r"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝐒υмιт~𝐒ᴇ - 🦢💘",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝐒υмιт~! 🌙",
        r"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
        r"chudke bhaga kaise 😂💥🤣🤘🏻",
        r"ne toh 𝐒υмιт~ka lun muh me lelia 😂🙏🏻😂🙏🏻",
        r"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
        r"mkl lun te vaj 😂✊🏻💦",
        r"𝗧ᴍᴋ𝗕 pe 𝐒υмιт~ka hamla 😂⚔🔥💥",
        r"𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
        r"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
        r"chl rndyce chud ke dikha 😂💥🤣🔥",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        r"tera baap bass 𝐒υмιт~hai 😂🎀",
        r" try maa hagte hue paad mari -#😹🔥🥀",
        r"  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝐒υмιт~𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
        r"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ 𝐒υмιт~𝐒ᴇ - 🦢💘",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝐒υмιт~! 🌙",
        r"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥"
    ],
    'fswipe': [
        r"chudke bhaga kaise 😂💥🤣🤘🏻",
        r"ne toh 𝐒υмιт~ka lun muh me lelia 😂🙏🏻😂🙏🏻",
        r"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
        r"mkl lun te vaj 😂✊🏻💦",
        r"𝗧ᴍᴋ𝗕 pe 𝐒υмιт~ka hamla 😂⚔🔥💥",
        r"𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
        r"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
        r"chl rndyce chud ke dikha 😂💥🤣🔥",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        r"tera baap bass 𝐒υмιт~hai 😂🎀",
        r" try maa hagte hue paad mari -#😹🔥🥀",
        r"  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ 𝐒υмιт~𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜"
    ],
    'rrswipe': [
        r"𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💜 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💖 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💗 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💓 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💞 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💕 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💘 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💝 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💟 ݁˖⭑.ᐟ"
    ],
    'cswipe': [
        r" 𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸 ⇝ ༼ 🍓༽ ",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍈༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫜༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍒༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍐༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥥༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍎༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫛༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥔༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍅༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥬༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🧅༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🌶️༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫑༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫚༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍉༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍏༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫘༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍑༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥝༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🌰༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍊༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥑༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥜༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍐༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫒༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍞༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥭༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥦༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫓༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍍༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥒༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥯༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍌༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫐༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🧇༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍋༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍇༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍳༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🌽༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍆༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥩༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍋‍🟩༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍠༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍟༽"
    ]
}

REPLY_TEXTS = {
    'rreply': [
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐒υмιт~बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐒υмιт~बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        r"सोच तेरी बहन को 𝐒υмιт~बाप का गुलाम चोद रहा 😎🔥",
        r"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        r"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐒υмιт~/\~ 👑 बाप से सही chudi 🥵🔥"
    ],
    'breply': [
        r"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐒υмιт~बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
        r"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐒υмιт~बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐒υмιт~बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        r"सोच तेरी बहन को 𝐒υмιт~बाप का गुलाम चोद रहा 😎🔥",
        r"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        r"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐒υмιт~/\~ 👑 बाप से सही chudi 🥵🔥",
        r"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐒υмιт~बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
        r"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐒υмιт~बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥"
    ],
    'creply': [
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐒υмιт~बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        r"सोच तेरी बहन को 𝐒υмιт~बाप का गुलाम चोद रहा 😎🔥",
        r"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        r"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन 𝐒υмιт~/\~ 👑 बाप से सही chudi 🥵🔥",
        r"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ 𝐒υмιт~बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
        r"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद 𝐒υмιт~बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ 𝐒υмιт~बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥"
    ]
}

# ====================== STATE ======================
active_tasks = {}
sudo_users = {OWNER_ID}
sudo_list = [OWNER_ID]
start_time = time.time()

def is_sudo(user_id: int) -> bool:
    # Direct check for owner - no sudo_users dependency
    if user_id == OWNER_ID:
        return True
    if user_id in sudo_users:
        return True
    return False

async def replace_target(text: str, target: str = "") -> str:
    if target:
        text = text.replace("{target}", target).replace("<target>", target).replace("<TARGET>", target.upper())
    return text

# ====================== SUPER FAST LOOPS ======================
async def nc_loop(context, bot_id, chat_id, loop_type, target):
    key = f"{bot_id}_{chat_id}_{loop_type}"
    texts = NC_TEXTS.get(loop_type, NC_TEXTS['snc'])
    i = 0
    
    error_skip = 0
    while key in active_tasks:
        try:
            title = await replace_target(texts[i % len(texts)], target)
            try:
                await context.bot.set_chat_title(chat_id, title)
                i += 1
                error_skip = 0
            except Exception as send_err:
                if "FloodWait" in str(send_err):
                    wait_match = re.search(r'retry after (\d+)', str(send_err))
                    wait_time = int(wait_match.group(1)) if wait_match else 1
                    await asyncio.sleep(wait_time)
                else:
                    # Skip error, continue to next text
                    i += 1
                    error_skip += 1
                    if error_skip > 50:
                        error_skip = 0
                    await asyncio.sleep(0.001) if error_skip > 10 else None
        except asyncio.CancelledError:
            break
        except:
            # Silently skip any other error
            i += 1
            await asyncio.sleep(0.001)
    
    # AUTO RESTART FUNCTIONALITY
    if AUTO_RESTART and key in active_tasks:
        print(f"🔄 Auto-Restarting {loop_type}...")
        await asyncio.sleep(RESTART_DELAY)
        if key in active_tasks:
            asyncio.create_task(nc_loop(context, bot_id, chat_id, loop_type, target))

async def spam_loop(context, bot_id, chat_id, loop_type, target):
    key = f"{bot_id}_{chat_id}_{loop_type}"
    texts = SPAM_TEXTS.get(loop_type, SPAM_TEXTS['bspam'])
    i = 0
    
    while key in active_tasks:
        try:
            msg = await replace_target(texts[i % len(texts)], target)
            try:
                await context.bot.send_message(chat_id, msg)
                i += 1
            except Exception as send_err:
                if "FloodWait" in str(send_err):
                    wait_match = re.search(r'retry after (\d+)', str(send_err))
                    wait_time = int(wait_match.group(1)) if wait_match else 1
                    await asyncio.sleep(wait_time)
                else:
                    i += 1
                    await asyncio.sleep(0.001)
        except asyncio.CancelledError:
            break
        except:
            i += 1
    
    # AUTO RESTART FUNCTIONALITY
    if AUTO_RESTART and key in active_tasks:
        print(f"🔄 Auto-Restarting {loop_type}...")
        await asyncio.sleep(RESTART_DELAY)
        if key in active_tasks:
            asyncio.create_task(spam_loop(context, bot_id, chat_id, loop_type, target))

async def swipe_loop(context, bot_id, chat_id, reply_to, loop_type, target, is_reply=False):
    key = f"{bot_id}_{chat_id}_{reply_to}_{loop_type}"
    texts = SWIPE_TEXTS.get(loop_type) if not is_reply else REPLY_TEXTS.get(loop_type)
    if not texts:
        return
    i = 0
    
    while key in active_tasks:
        try:
            text = await replace_target(texts[i % len(texts)], target)
            try:
                await context.bot.send_message(chat_id, text, reply_to_message_id=reply_to)
                i += 1
            except Exception as send_err:
                if "FloodWait" in str(send_err):
                    wait_match = re.search(r'retry after (\d+)', str(send_err))
                    wait_time = int(wait_match.group(1)) if wait_match else 1
                    await asyncio.sleep(wait_time)
                else:
                    i += 1
                    await asyncio.sleep(0.001)
        except asyncio.CancelledError:
            break
        except:
            i += 1
    
    # AUTO RESTART FUNCTIONALITY
    if AUTO_RESTART and key in active_tasks:
        print(f"🔄 Auto-Restarting {loop_type}...")
        await asyncio.sleep(RESTART_DELAY)
        if key in active_tasks:
            asyncio.create_task(swipe_loop(context, bot_id, chat_id, reply_to, loop_type, target, is_reply))

# ====================== GAME OVER (FIXED) ======================

async def gameover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_sudo(user.id):
        await update.message.reply_text("𝐒υмιт ❤️‍🩹")
        return

    text = update.message.text or ""

    # parse !gameover <target>
    parts = text.split(" ", 1)
    target = parts[1].strip() if len(parts) > 1 else "Bhai"

    now = datetime.now()

    game_msg = f"""
╭───────ꪆৎ───────╮
  Gᴀᴍᴇ Oᴠᴇʀ Bʏ 𝐒υмιт~
╰───────ꪆৎ───────╯
{target} Gᴀᴍᴇ Oᴠᴇʀ Gᴜʟᴀᴍ 
Dᴀᴛᴇ :- {now.strftime("%d %b %Y")}
Tɪᴍᴇ :- {now.strftime("%H:%M:%S")}
Dᴀʏ :- {now.strftime("%A")}
╭───────ꪆৎ───────╮
             𝐆ᴀᴍᴇ 𝐎ᴠᴇʀ
╰───────ꪆৎ───────╯
""".strip()

    # Change only the current group's title and description using the target.
    new_group_text = f"𝐆ᴀᴍᴇ 𝐎ᴠᴇʀ  ({target}) 𝐍ᴏᴡ 𝐆ᴏ 𝐀ɴᴅ 𝐂ʀʏ 𝐊ɪᴅ 🧸🕊️"
    try:
        await context.bot.set_chat_title(
            chat_id=update.effective_chat.id,
            title=new_group_text
        )
    except Exception:
        pass

    try:
        await context.bot.set_chat_description(
            chat_id=update.effective_chat.id,
            description=new_group_text
        )
    except Exception:
        pass

    if GAMEOVER_IMAGE_URL and not GAMEOVER_IMAGE_URL.startswith("PASTE_"):

        try:

            await update.message.reply_photo(photo=GAMEOVER_IMAGE_URL, caption=game_msg)

            return

        except Exception:

            pass

    await update.message.reply_text(game_msg)
# ====================== PIN COMMANDS ======================
async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pin the replied message"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт ❤️‍🩹")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to pin it!\nExample: Reply to a message and type !pin")
        return
    
    try:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 Message pinned successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nMake sure bot has admin rights!")

async def unpin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unpin the replied message"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт Bʜᴀɢᴡᴀɴ  💢")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to unpin it!\nExample: Reply to a message and type !unpin")
        return
    
    try:
        await update.message.reply_to_message.unpin()
        await update.message.reply_text("📌 Message unpinned successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nMake sure bot has admin rights!")

async def unpin_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove all pinned messages"""
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт")
        return
    
    chat = update.effective_chat
    
    try:
        await chat.unpin_all_messages()
        await update.message.reply_text("📌 All pinned messages removed!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nMake sure bot has admin rights!")

# ====================== MUTE/UNMUTE COMMANDS ======================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт~Bʜᴀɢᴡᴀɴ Hᴀɪ ❤️‍🩹")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to user message.")
        return

    chat_id = update.effective_chat.id
    user_id = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )
        await update.message.reply_text("✅ MUTED")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ---------------- UNMUTE ----------------
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт Bʜᴀɢᴡᴀɴ ❤️‍🩹")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to user message.")
        return

    chat_id = update.effective_chat.id
    user_id = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        )
        await update.message.reply_text("✅ UNMUTED")

    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def gcmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("No access")
        return

    chat_id = update.effective_chat.id

    perms = ChatPermissions(
        can_send_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False
    )

    await context.bot.set_chat_permissions(
        chat_id=chat_id,
        permissions=perms
    )

    await update.message.reply_text("🔇 GC MUTED")


# ---------------- GROUP UNMUTE ----------------
async def gcunmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("No access")
        return

    chat_id = update.effective_chat.id

    perms = ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False
    )

    await context.bot.set_chat_permissions(
        chat_id=chat_id,
        permissions=perms
    )

    await update.message.reply_text("🔊 GC UNMUTED")

# ====================== OTHER COMMANDS ======================
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт~Bʜᴀɢᴡᴀɴ Hᴀɪ ❤️‍🩹")
        return
    chat_id = update.effective_chat.id
    removed = 0
    for key in list(active_tasks.keys()):
        if str(chat_id) in key:
            task = active_tasks.pop(key, None)
            if task and not task.done():
                task.cancel()
                removed += 1
    stop_msg = f"""╭───────ꪆৎ───────╮

   𝐀ʟʟ 𝐒ᴛᴏᴘᴘᴇᴅ 

 𝐒υмιт~ 𝐍ᴇᴠᴇʀ 𝐃ɪᴇꜱ

──────── ♡ ────────

✧ 𝐒υмιт~ 𝐎ꜰꜰ¿🌚🖕🏻

╰───────ꪆৎ───────╯
"""
    if STOPALL_IMAGE_URL and not STOPALL_IMAGE_URL.startswith("PASTE_"):
        try:
            await update.message.reply_photo(
                photo=STOPALL_IMAGE_URL,
                caption=stop_msg,
            )
            return
        except Exception:
            pass
    await update.message.reply_text(stop_msg)

async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only Owner can give sudo!")

    # Reply se user
    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id

    # Argument se user ID
    elif context.args:
        try:
            user_id = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID!")

    else:
        return await update.message.reply_text(
            "Usage:\n"
            "• !sudo <user_id>\n"
            "• Reply to a user's message with !sudo"
        )

    if user_id in sudo_users:
        return await update.message.reply_text("Already sudo!")

    sudo_users.add(user_id)

    if user_id not in sudo_list:
        sudo_list.append(user_id)

    await update.message.reply_text(f"✅ Sudo added: `{user_id}`", parse_mode="Markdown")

async def remove_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id

    elif context.args:
        try:
            user_id = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID!")

    else:
        return await update.message.reply_text(
            "Usage:\n"
            "• !dsudo <user_id>\n"
            "• Reply to a sudo user's message with !dsudo"
        )

    sudo_users.discard(user_id)

    if user_id in sudo_list:
        sudo_list.remove(user_id)

    await update.message.reply_text(f"❌ Sudo removed: `{user_id}`", parse_mode="Markdown")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ban_unban(update, context, True)

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ban_unban(update, context, False)

async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE, ban_action: bool = True):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐭ᴇʀɪ 𝐢ᴛɴɪ 𝐨ᴋᴀᴛ ɴʏ ʀɴᴅʏᴋᴇ 𝐥ᴀᴅᴄᴇ ɢᴀʀɪʙ😂🫵🏻")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message!")
        return
    user = update.message.reply_to_message.from_user
    chat = update.effective_chat
    try:
        if ban_action:
            await chat.ban_member(user.id)
            await update.message.reply_text(f"✅ {user.first_name} BANNED!")
        else:
            await chat.unban_member(user.id)
            await update.message.reply_text(f"✅ {user.first_name} UNBANNED!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def delmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐒υмιт ❤️‍🩹")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message!")
        return
    try:
        await update.message.reply_to_message.delete()
        await update.message.reply_text("✅ Message deleted!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def sudolist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    if sudo_users:
        await update.message.reply_text(f"**Sudo List** ({len(sudo_users)})\n" + "\n".join(map(str, sudo_users)))
    else:
        await update.message.reply_text("No sudo users.")

async def adminlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    try:
        admins = await update.effective_chat.get_administrators()
        admin_names = [f"{admin.user.first_name} (ID: {admin.user.id})" for admin in admins]
        await update.message.reply_text(f"**Admin List**\n" + "\n".join(admin_names))
    except Exception as e:
        await update.message.reply_text(f"Cannot fetch: {str(e)}")

async def banlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    await update.message.reply_text("**Ban List** - Check manually.")

async def refreshsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    global sudo_users, sudo_list
    sudo_users = {OWNER_ID}
    sudo_list = [OWNER_ID]
    await update.message.reply_text("✅ Sudo refreshed! Only Owner is sudo now.")

async def refresh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    global active_tasks, sudo_users, sudo_list, start_time
    for key, task in list(active_tasks.items()):
        if not task.done():
            task.cancel()
    active_tasks.clear()
    sudo_users = {OWNER_ID}
    sudo_list = [OWNER_ID]
    start_time = time.time()
    stop_msg = "✅ Bot refreshed! All tasks stopped."
    if STOPALL_IMAGE_URL and not STOPALL_IMAGE_URL.startswith("PASTE_"):
        try:
            await update.message.reply_photo(photo=STOPALL_IMAGE_URL, caption=stop_msg)
            return
        except Exception:
            pass
    await update.message.reply_text(stop_msg)
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nc = sum(1 for k in active_tasks if "nc_" in k)
    spam = sum(1 for k in active_tasks if "spam_" in k)
    swipe = sum(1 for k in active_tasks if "swipe_" in k)
    reply = sum(1 for k in active_tasks if any(x in k for x in ['rreply', 'breply', 'creply']))
    
    await update.message.reply_text(
        f"**📊 BOT STATUS**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔹 NC: {nc}\n"
        f"🔹 Spam: {spam}\n"
        f"🔹 Swipe: {swipe}\n"
        f"🔹 Reply: {reply}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 Total: {len(active_tasks)}"
    )

# ====================== MENU ======================
MENU_TEXT = """
━━━━━━━━━━━━━━━━━━━━࿐
        𝐒υмιт~ 𝐎ꜰꜰ
━━━━━━━━━━━━━━━━━━━━࿐

╭━━━〔 𝐂ᴏᴍᴍᴀɴᴅ 𝐌ᴇɴᴜ 〕━━━╮

✦ 𝐂ꪮᴍᴍꫝɴᴅ 𝐏ʀꫀꫀғɪx  ➜ ~

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐍ᥴ 𝐒ᴛʏʟᴇ 〕━━━╮

➤ ~snc       ⤳ ʂ𝓽ᴀʀᴛ ɴᴄ
➤ ~ssnc      ⤳ ꜱᴜᴘᴇʀ ɴᴄ
➤ ~fnc       ⤳ ꜰɪʀᴇ ɴᴄ
➤ ~cnc       ⤳ ᴄᴏᴏʟ ɴᴄ
➤ ~bnc       ⤳ ʙᴜɪʟᴛ ɴᴄ
➤ ~sgcnc     ⤳ ꜱᴘᴇᴄɪᴀʟ ɴᴄ
➤ ~dnc       ⤳ ᴅᴇʟᴇᴛᴇ ɴᴄ
➤ ~dallnc    ⤳ ᴄʟᴇᴀʀ ɴᴄ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐒ᴘᴀᴍ 𝐏ᴜʟꜱᴇ 〕━━━╮

✦ ~bspam      ⤳ ʙɪɢ ꜱᴘᴀᴍ
✦ ~aspam      ⤳ ᴀʀᴛɪꜱᴛɪᴄ ꜱᴘᴀᴍ
✦ ~sspam      ⤳ ꜱᴛʀᴏɴɢ ꜱᴘᴀᴍ
✦ ~fspam      ⤳ ꜰᴀꜱᴛ ꜱᴘᴀᴍ
✦ ~gspam      ⤳ ɢʟᴏᴡ ꜱᴘᴀᴍ
✦ ~rspam      ⤳ ʀɪᴄʜ ꜱᴘᴀᴍ
✦ ~dbspam     ⤳ ᴅᴇʟᴇᴛᴇ ꜱᴘᴀᴍ
✦ ~dallspam   ⤳ ᴄʟᴇᴀʀ ꜱᴘᴀᴍ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐒ʟɪᴅᴇ 𝐌ᴏᴅᴇ 〕━━━╮

➤ ~aswipe     ⤳ ᴀᴍᴀᴢɪɴɢ ꜱʟɪᴅᴇ
➤ ~fswipe     ⤳ ꜰᴀꜱᴛ ꜱʟɪᴅᴇ
➤ ~rrswipe    ⤳ ʀᴀɪᴅ ꜱʟɪᴅᴇ
➤ ~cswipe     ⤳ ᴄᴏᴏʟ ꜱʟɪᴅᴇ
➤ ~daswipe    ⤳ ᴅᴇʟᴇᴛᴇ ꜱʟɪᴅᴇ
➤ ~dallswipe  ⤳ ᴄʟᴇᴀʀ ꜱʟɪᴅᴇ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐑ᴇᴘʟʏ 𝐌ᴏᴅᴇ 〕━━━╮

✧ ~rreply     ⤳ ʀɪᴄʜ ʀᴇᴘʟʏ
✧ ~breply     ⤳ ʙɪɢ ʀᴇᴘʟʏ
✧ ~creply     ⤳ ᴄᴏᴏʟ ʀᴇᴘʟʏ
✧ ~drreply    ⤳ ꜱᴛᴏᴘ ʀᴇᴘʟʏ
✧ ~dallreply  ⤳ ᴄʟᴇᴀʀ ʀᴇᴘʟɪᴇꜱ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐏ʜᴏᴛᴏ 𝐋ᴏᴏᴘ 〕━━━╮

➤ ~savephoto   ⤳ ꜱᴀᴠᴇ ᴘʜᴏᴛᴏ
➤ ~startphoto  ⤳ ꜱᴛᴀʀᴛ ᴘʜᴏᴛᴏ
➤ ~stopphoto   ⤳ ꜱᴛᴏᴘ ᴘʜᴏᴛᴏ
➤ ~dphoto      ⤳ ᴅᴇʟᴇᴛᴇ ᴘʜᴏᴛᴏ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐃ᴇʟᴀʏ 𝐂ᴏɴᴛʀᴏʟ 〕━━━╮

✦ ~setdelaync     ⤳ ɴᴄ ꜱᴘᴇᴇᴅ
✦ ~setdelayspam   ⤳ ꜱᴘᴀᴍ ꜱᴘᴇᴇᴅ
✦ ~setdelayswipe  ⤳ ꜱʟɪᴅᴇ ꜱᴘᴇᴇᴅ
✦ ~setdelayreply  ⤳ ʀᴇᴘʟʏ ꜱᴘᴇᴇᴅ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐒ᴛᴏʀᴍ 𝐀ᴅᴍɪɴ 〕━━━╮

➤ ~sudo        ⤳ ᴀᴅᴅ ꜱᴜᴅᴏ
➤ ~dsudo       ⤳ ʀᴇᴍᴏᴠᴇ ꜱᴜᴅᴏ
➤ ~sudolist    ⤳ ꜱᴜᴅᴏ ʟɪꜱᴛ
➤ ~refreshsudo ⤳ ʀᴇꜰʀᴇꜱʜ ꜱᴜᴅᴏ
➤ ~ban         ⤳ ʙʟᴀᴄᴋʟɪꜱᴛ
➤ ~unban       ⤳ ʀᴇᴍᴏᴠᴇ ʙʟᴀᴄᴋʟɪꜱᴛ
➤ ~adminlist   ⤳ ᴀᴅᴍɪɴ ʟɪꜱᴛ
➤ ~banlist     ⤳ ʙᴀɴ ʟɪꜱᴛ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐌ᴜᴛᴇ 𝐂ᴏɴᴛʀᴏʟ 〕━━━╮

✧ ~mute        ⤳ ꜱɪʟᴇɴᴛ ᴜꜱᴇʀ
✧ ~unmute      ⤳ ᴜɴᴍᴜᴛᴇ ᴜꜱᴇʀ
✧ ~gcmute      ⤳ ᴍᴜᴛᴇ ɢʀᴏᴜᴘ
✧ ~gcunmute    ⤳ ᴜɴᴍᴜᴛᴇ ɢʀᴏᴜᴘ
✧ ~delmsg      ⤳ ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐒ᴛᴀᴛᴜꜱ 𝐓ᴏᴏʟꜱ 〕━━━╮

➤ ~status      ⤳ ᴄʜᴇᴄᴋ ꜱᴛᴀᴛᴜꜱ
➤ ~ping        ⤳ ᴄʜᴇᴄᴋ ᴘɪɴɢ
➤ ~uptime      ⤳ ᴄʜᴇᴄᴋ ᴜᴘᴛɪᴍᴇ
➤ ~refresh     ⤳ ʀᴇꜰʀᴇꜱʜ ꜱᴇᴛᴛɪɴɢꜱ
➤ ~pin         ⤳ ᴘɪɴ ᴍᴇꜱꜱᴀɢᴇ
➤ ~unpin       ⤳ ᴜɴᴘɪɴ ᴍᴇꜱꜱᴀɢᴇ
➤ ~revpin      ⤳ ᴄʟᴇᴀʀ ᴘɪɴꜱ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐆ʀᴏᴜᴘ 𝐌ᴀɴᴀɢᴇᴍᴇɴᴛ 〕━━━╮

✦ ~groups      ⤳ ɢʀᴏᴜᴘ ʟɪꜱᴛ
✦ ~statusg     ⤳ ɢʀᴏᴜᴘ ꜱᴛᴀᴛᴜꜱ
✦ ~overg       ⤳ ɢʀᴏᴜᴘ ᴄᴏɴᴛʀᴏʟ
✦ ~leaveg      ⤳ ʟᴇᴀᴠᴇ ɢʀᴏᴜᴘ

╰━━━━━━━━━━━━━━━━━━╯

╭━━━〔 𝐃ᴇꜱᴛʀᴜᴄᴛɪᴠᴇ 𝐌ᴏᴅᴇ 〕━━━╮

➤ ~gameover    ⤳ ɢᴀᴍᴇ ᴏᴠᴇʀ
➤ ~stopall     ⤳ ꜱᴛᴏᴘ ᴀʟʟ
➤ ~stopnc      ⤳ ꜱᴛᴏᴘ ɴᴄ
➤ ~stopspam    ⤳ ꜱᴛᴏᴘ ꜱᴘᴀᴍ
➤ ~stopswipe   ⤳ ꜱᴛᴏᴘ ꜱʟɪᴅᴇ

╰━━━━━━━━━━━━━━━━━━╯

━━━━━━━━━━━━━━━━━━━━࿐
      
      𝐒υмιт~𝐏ᴇʀᴍᴀ 𝐎ꜰꜰ
━━━━━━━━━━━━━━━━━━━━࿐

"""

# ====================== MENU DISPLAY CONFIG ======================
# Only this bot displays ~menu. 0 = first bot, 1 = second bot, etc.
MENU_BOT_INDEX = 0

# Put your Catbox direct image URL here.
# Example: "https://files.catbox.moe/xxxxx.jpg"
MENU_IMAGE_URL = "https://files.catbox.moe/by6ru3.jpeg"

# ====================== CONTROL IMAGE URLS ======================
STOPALL_IMAGE_URL = "https://files.catbox.moe/pph0rq.jpg"
GAMEOVER_IMAGE_URL = "https://files.catbox.moe/lnjqy4.jpg"

# ====================== BUTTON MENU ======================
# Same button-style navigation as the reference menu, while keeping
# this file's original commands/handlers unchanged.

def _menu_font(text):
    small = str.maketrans(dict(zip(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )))
    bold = dict(zip(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞ғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    ))
    parts = re.split(r'(\s+|[^A-Za-z]+)', str(text))
    out = []
    for part in parts:
        if part and part[0].isalpha() and part.isascii():
            out.append(bold.get(part[0], part[0]) + part[1:].lower().translate(small))
        else:
            out.append(part)
    return ''.join(out)


def get_panel_categories():
    return {
        "⚡ NC Style": ["~snc", "~ssnc", "~fnc", "~cnc", "~bnc", "~sgcnc", "~dnc", "~dallnc"],
        "💥 Spam Pulse": ["~bspam", "~aspam", "~sspam", "~fspam", "~gspam", "~rspam", "~dbspam", "~dallspam"],
        "🌪️ Slide Mode": ["~aswipe", "~fswipe", "~rrswipe", "~cswipe", "~daswipe", "~dallswipe"],
        "💬 Reply Mode": ["~rreply", "~breply", "~creply", "~drreply", "~dallreply"],
        "📸 Photo Loop": ["~savephoto", "~startphoto", "~stopphoto", "~dphoto"],
        "⚙️ Delay Control": ["~setdelaync", "~setdelayspam", "~setdelayswipe", "~setdelayreply"],
        "👑 Storm Admin": ["~sudo", "~dsudo", "~sudolist", "~refreshsudo", "~ban", "~unban", "~adminlist", "~banlist"],
        "🔇 Mute Control": ["~mute", "~unmute", "~gcmute", "~gcunmute", "~delmsg"],
        "📊 Status Tools": ["~status", "~ping", "~uptime", "~refresh", "~pin", "~unpin", "~revpin"],
        "👥 Group Management": ["~groups", "~statusg", "~overg", "~leaveg"],
        "🛑 Destructive Mode": ["~gameover", "~stopall", "~stopnc", "~stopspam", "~stopswipe"],
    }

_PANEL_EMOJIS = {
    "snc":"⚡", "ssnc":"🔥", "fnc":"💥", "cnc":"❄️", "bnc":"🔷", "sgcnc":"👑", "dnc":"⛔", "dallnc":"🧹",
    "bspam":"💣", "aspam":"🎨", "sspam":"🔥", "fspam":"⚡", "gspam":"✨", "rspam":"💫", "dbspam":"⛔", "dallspam":"🧹",
    "aswipe":"🌪️", "fswipe":"⚡", "rrswipe":"🔄", "cswipe":"❄️", "daswipe":"⛔", "dallswipe":"🧹",
    "rreply":"💬", "breply":"📨", "creply":"❄️", "drreply":"⛔", "dallreply":"🧹",
    "savephoto":"💾", "startphoto":"▶️", "stopphoto":"⏹️", "dphoto":"🗑️",
    "setdelaync":"⚙️", "setdelayspam":"⚙️", "setdelayswipe":"⚙️", "setdelayreply":"⚙️",
    "sudo":"🤝", "dsudo":"↩️", "sudolist":"📋", "refreshsudo":"🔄", "ban":"🚫", "unban":"✅", "adminlist":"👑", "banlist":"📕",
    "mute":"🔇", "unmute":"🔊", "gcmute":"🔒", "gcunmute":"🔓", "delmsg":"🗑️",
    "status":"📊", "ping":"🏓", "uptime":"⏱️", "refresh":"🔄", "pin":"📌", "unpin":"📍", "revpin":"🧹",
    "groups":"👥", "statusg":"📈", "overg":"🛑", "leaveg":"🚪",
    "gameover":"💀", "stopall":"🚨", "stopnc":"⛔", "stopspam":"🛑", "stopswipe":"🛑",
}


def _panel_command(label):
    return label.strip().lstrip('~').split()[0].lower()


def _panel_button(label):
    command = _panel_command(label)
    emoji = _PANEL_EMOJIS.get(command, "✦")
    if CopyTextButton is not None:
        return InlineKeyboardButton(
            f"{emoji} {_menu_font(label)}",
            copy_text=CopyTextButton(text=label)
        )
    return InlineKeyboardButton(
        f"{emoji} {_menu_font(label)}",
        callback_data=f"panel_cmd:{command}"
    )


def _panel_prefix_button():
    if CopyTextButton is not None:
        return InlineKeyboardButton("📋 ~", copy_text=CopyTextButton(text="~"))
    return InlineKeyboardButton("📋 ~", callback_data="panel_prefix")


def get_panel_keyboard():
    keyboard, row = [], []
    for category in get_panel_categories():
        row.append(InlineKeyboardButton(_menu_font(category), callback_data=f"panel_menu:{category}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton("📊 𝐒ᴛᴀᴛᴜs", callback_data="panel_status"),
        InlineKeyboardButton("🛑 𝐒ᴛᴏᴘ 𝐀ʟʟ", callback_data="panel_stopall"),
    ])
    keyboard.append([_panel_prefix_button()])
    return InlineKeyboardMarkup(keyboard)


def get_panel_category_keyboard(category):
    commands = get_panel_categories().get(category, [])
    keyboard, row = [], []
    for command in commands:
        row.append(_panel_button(command))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ 𝐁ᴀᴄᴋ ᴛᴏ 𝐌ᴀɪɴ 𝐌ᴇɴᴜ", callback_data="panel_main")])
    keyboard.append([_panel_prefix_button()])
    return InlineKeyboardMarkup(keyboard)


async def panel_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if data == "panel_main":
        # Keep the menu message as a photo; just restore its buttons.
        try:
            await query.message.edit_caption(caption="", reply_markup=get_panel_keyboard())
        except Exception:
            await query.message.edit_reply_markup(reply_markup=get_panel_keyboard())
        return
    if data.startswith("panel_menu:"):
        category = data.split(":", 1)[1]
        if category in get_panel_categories():
            try:
                await query.message.edit_caption(
                    caption="",
                    reply_markup=get_panel_category_keyboard(category)
                )
            except Exception:
                await query.message.edit_reply_markup(
                    reply_markup=get_panel_category_keyboard(category)
                )
        return
    if data == "panel_status":
        await query.message.reply_text("Use `~status` to check the current status.", parse_mode="Markdown")
        return
    if data == "panel_stopall":
        await query.message.reply_text("Use `~stopall` to stop active loops.", parse_mode="Markdown")
        return
    if data == "panel_prefix":
        await query.answer("Prefix: ~", show_alert=True)
        return
    if data.startswith("panel_cmd:"):
        await query.answer("Command button — copy it, then add its arguments if needed.", show_alert=True)


# ====================== PHOTO COMMAND FUNCTIONS ======================
async def savephoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save photos from the group"""
    msg = update.message
    chat_id = msg.chat_id
    
    # Check if replying to a message with photo
    if msg.reply_to_message and msg.reply_to_message.photo:
        if chat_id not in SAVED_PHOTOS:
            SAVED_PHOTOS[chat_id] = []
        
        photo = msg.reply_to_message.photo[-1]  # Get highest quality
        file_id = photo.file_id
        
        SAVED_PHOTOS[chat_id].append(file_id)
        await msg.reply_text(f"✅ Photo Saved! Total: {len(SAVED_PHOTOS[chat_id])} photos\n📸 Use ~startphoto to start changing DP!")
    else:
        await msg.reply_text("❌ Reply to a photo with ~savephoto to save it!")

async def startphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start changing group DP with saved photos in loop"""
    msg = update.message
    chat_id = msg.chat_id
    
    if chat_id not in SAVED_PHOTOS or not SAVED_PHOTOS[chat_id]:
        return await msg.reply_text("❌ No photos saved! Use ~savephoto first!")
    
    # Check if already running
    task_key = f"{chat_id}_photo"
    if task_key in ACTIVE_PHOTO_LOOPS:
        return await msg.reply_text("⚠️ Photo loop already running! Use ~stopphoto to stop!")
    
    async def photo_loop():
        idx = 0
        while task_key in ACTIVE_PHOTO_LOOPS:
            try:
                photo_list = SAVED_PHOTOS.get(chat_id, [])
                if not photo_list:
                    await asyncio.sleep(0.1)
                    continue
                
                file_id = photo_list[idx % len(photo_list)]
                try:
                    # Get file from file_id
                    file = await context.bot.get_file(file_id)
                    # Download the file
                    photo_file = await file.download_to_memory()
                    # Set as chat photo
                    await context.bot.set_chat_photo(chat_id=chat_id, photo=photo_file)
                    idx += 1
                    await asyncio.sleep(0.5)  # Small delay between changes
                except Exception as photo_err:
                    if "FloodWait" in str(photo_err):
                        wait_match = re.search(r'retry after (\d+)', str(photo_err))
                        wait_time = int(wait_match.group(1)) if wait_match else 5
                        await asyncio.sleep(wait_time)
                    else:
                        idx += 1
                        await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except:
                idx += 1
                await asyncio.sleep(1)
    
    task = asyncio.create_task(photo_loop())
    ACTIVE_PHOTO_LOOPS[task_key] = task
    await msg.reply_text(f"🔄 Started changing DP! Full speed mode! 🚀\n📸 {len(SAVED_PHOTOS[chat_id])} photos rotating!")

async def stopphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop the photo DP changing loop"""
    msg = update.message
    chat_id = msg.chat_id
    
    task_key = f"{chat_id}_photo"
    if task_key not in ACTIVE_PHOTO_LOOPS:
        return await msg.reply_text("❌ No photo loop running!")
    
    task = ACTIVE_PHOTO_LOOPS.pop(task_key, None)
    if task and not task.done():
        task.cancel()
        await msg.reply_text("⛔ Photo loop stopped!")
    else:
        await msg.reply_text("❌ Could not stop loop!")

async def dphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete saved photos and show menu"""
    msg = update.message
    chat_id = msg.chat_id
    
    # Stop if running
    task_key = f"{chat_id}_photo"
    if task_key in ACTIVE_PHOTO_LOOPS:
        task = ACTIVE_PHOTO_LOOPS.pop(task_key)
        if task and not task.done():
            task.cancel()
    
    # Delete saved photos
    if chat_id in SAVED_PHOTOS:
        count = len(SAVED_PHOTOS[chat_id])
        del SAVED_PHOTOS[chat_id]
    else:
        count = 0
    
    # Show menu
    menu_text = f"""🎬 PHOTO MANAGER MENU 📸

━━━━━━━━━━━━━━━━━━━━
✅ Deleted {count} photos!

📋 Commands:
• ~savephoto - Save photo (reply to it)
• ~startphoto - Start DP changes 🚀
• ~stopphoto - Stop the loop ⛔
• ~dphoto - Delete all & show menu
━━━━━━━━━━━━━━━━━━━━

✨ All photos deleted! Photo loop stopped!"""
    
    await msg.reply_text(menu_text)

# ====================== GROUP MANAGEMENT COMMANDS ======================
async def groups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all groups where bot is active"""
    msg = update.message
    
    if not ACTIVE_GROUPS:
        return await msg.reply_text("❌ Bot kisi bhi group mein active nahi hai!")
    
    text = f"📊 BOT ACTIVE GROUPS: {len(ACTIVE_GROUPS)}\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for i, group_id in enumerate(ACTIVE_GROUPS, 1):
        group_name = GROUP_TRACKER.get(group_id, f"Group {group_id}")
        text += f"{i}. {group_name}\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━━━"
    await msg.reply_text(text)

async def statusg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show status of all commands in each group"""
    msg = update.message
    
    if not active_tasks:
        return await msg.reply_text("❌ Koi bhi command chal nahi rahi!")
    
    text = "📈 GROUP-WISE COMMAND STATUS:\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    group_commands = defaultdict(list)
    
    # Organize tasks by group
    for task_key in active_tasks:
        parts = task_key.rsplit('_', 1)
        if len(parts) == 2:
            group_id = int(parts[1])
            cmd_type = parts[0]
            
            if group_id in GROUP_TRACKER:
                start_time = TASK_START_TIMES.get(task_key, time.time())
                elapsed = int(time.time() - start_time)
                mins = elapsed // 60
                secs = elapsed % 60
                
                group_commands[group_id].append(f"  • {cmd_type.upper()} ({mins}m {secs}s)")
    
    if not group_commands:
        return await msg.reply_text("❌ Koi active command nahi!")
    
    for group_id in sorted(group_commands.keys()):
        group_name = GROUP_TRACKER.get(group_id, f"Group {group_id}")
        text += f"🔹 {group_name}\n"
        for cmd in group_commands[group_id]:
            text += cmd + "\n"
        text += "\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    await msg.reply_text(text)

async def overg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop all commands in a specific group"""
    msg = update.message
    args = msg.text.split()[1:]
    
    if not args:
        return await msg.reply_text("❌ Group name likho! Format: !overg <group_name>")
    
    group_name = ' '.join(args)
    
    # Find group by name
    target_group_id = None
    for gid, gname in GROUP_TRACKER.items():
        if group_name.lower() in gname.lower():
            target_group_id = gid
            break
    
    if not target_group_id:
        return await msg.reply_text(f"❌ Group '{group_name}' nahi mila!")
    
    # Stop all tasks in this group
    removed = 0
    for task_key in list(active_tasks.keys()):
        if str(target_group_id) in task_key:
            task = active_tasks.pop(task_key, None)
            if task and not task.done():
                task.cancel()
                removed += 1
    
    # Send "over" message to that group
    try:
        await context.bot.send_message(
            chat_id=target_group_id,
            text="⚠️ OVER ⚠️\n\nSab commands stop ho gaye!"
        )
    except:
        pass
    
    await msg.reply_text(f"✅ Group '{GROUP_TRACKER.get(target_group_id)}' ka {removed} command stop!")

async def leaveg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot leaves a specific group"""
    msg = update.message
    args = msg.text.split()[1:]
    
    if not args:
        return await msg.reply_text("❌ Group name likho! Format: !leaveg <group_name>")
    
    group_name = ' '.join(args)
    
    # Find group by name
    target_group_id = None
    for gid, gname in GROUP_TRACKER.items():
        if group_name.lower() in gname.lower():
            target_group_id = gid
            break
    
    if not target_group_id:
        return await msg.reply_text(f"❌ Group '{group_name}' nahi mila!")
    
    # Stop all tasks in this group
    for task_key in list(active_tasks.keys()):
        if str(target_group_id) in task_key:
            task = active_tasks.pop(task_key, None)
            if task and not task.done():
                task.cancel()
    
    # Send goodbye message
    try:
        await context.bot.send_message(
            chat_id=target_group_id,
            text="👋 Bye bye! Bot leave ho raha hai!"
        )
    except:
        pass
    
    # Leave the group
    try:
        await context.bot.leave_chat(chat_id=target_group_id)
        ACTIVE_GROUPS.discard(target_group_id)
        if target_group_id in GROUP_TRACKER:
            del GROUP_TRACKER[target_group_id]
        await msg.reply_text(f"✅ Bot '{group_name}' se leave ho gaya!")
    except Exception as e:
        await msg.reply_text(f"❌ Error: {e}")

# ====================== MAIN HANDLER ======================
async def make_handler(bot_id: str):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        text = update.message.text
        if not text.startswith('~'):
            return

        msg = update.message
        cmd_parts = text.lower().strip().split()
        cmd = cmd_parts[0][1:] if cmd_parts else ""
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

        # PUBLIC COMMANDS
        if cmd == "menu":
            # Only the selected bot displays the menu.
            if str(bot_id) != str(MENU_BOT_INDEX):
                return

            if not MENU_IMAGE_URL or MENU_IMAGE_URL.startswith("PASTE_"):
                return await msg.reply_text(
                    "⚠️ MENU_IMAGE_URL me apna Catbox image link daalo."
                )

            try:
                return await msg.reply_photo(
                    photo=MENU_IMAGE_URL,
                    reply_markup=get_panel_keyboard()
                )
            except Exception as e:
                return await msg.reply_text(f"❌ Menu image send failed: {e}")
        
        if cmd == "whoami":
            user_id = update.effective_user.id
            is_owner = "✅ YES! Tu OWNER hai!" if user_id == OWNER_ID else f"❌ Nahi. Owner ID: {OWNER_ID}, Tera ID: {user_id}"
            return await msg.reply_text(f"🔍 **Your ID:** {user_id}\n{is_owner}")
        
        if cmd == "ping":
            start = time.time()
            await msg.reply_text("🏓 Pong!")
            end = time.time()
            await msg.reply_text(f"⚡ Response: {round((end-start)*1000)}ms")
            return
        
        if cmd == "uptime":
            up = int(time.time() - start_time)
            hours = up // 3600
            minutes = (up % 3600) // 60
            seconds = up % 60
            await msg.reply_text(f"⏱️ Uptime: {hours}h {minutes}m {seconds}s")
            return

        # SUDO ONLY COMMANDS
        # GAME OVER / STOP ALL: only the first bot should respond.
        if cmd in ("gameover", "stopall") and bot_id != "0":
            return

        if not is_sudo(update.effective_user.id):
            return await msg.reply_text("𝐒υмιт~𝐊ᴀ 𝐂ʜᴜꜱᴇɢᴀ? 🍆")

        chat_id = msg.chat.id

        # GAME OVER
        if cmd == "gameover":
            return await gameover(update, context)
        
        if cmd == "stopall":
            return await stopall(update, context)
        
        # PIN COMMANDS
        if cmd == "pin":
            return await pin_message(update, context)
        
        if cmd == "unpin":
            return await unpin_message(update, context)
        
        if cmd == "revpin":
            return await unpin_all_messages(update, context)

        # START COMMANDS
        if cmd in NC_TEXTS or cmd in SPAM_TEXTS or cmd in SWIPE_TEXTS or cmd in REPLY_TEXTS:
            target = " ".join(args) if args else msg.from_user.first_name
            is_swipe = cmd in SWIPE_TEXTS
            is_reply = cmd in REPLY_TEXTS
            
            if is_swipe or is_reply:
                if not msg.reply_to_message:
                    return await msg.reply_text("Reply to a message!")
                reply_to = msg.reply_to_message.message_id
                target_name = msg.reply_to_message.from_user.first_name if msg.reply_to_message.from_user else target
                key = f"{bot_id}_{chat_id}_{reply_to}_{cmd}"
                if key in active_tasks:
                    return await msg.reply_text("⚠️ Already Running!")
                task = asyncio.create_task(swipe_loop(context, bot_id, chat_id, reply_to, cmd, target_name, is_reply))
            elif cmd in SPAM_TEXTS:
                key = f"{bot_id}_{chat_id}_{cmd}"
                if key in active_tasks:
                    return await msg.reply_text("⚠️ Already Running!")
                task = asyncio.create_task(spam_loop(context, bot_id, chat_id, cmd, target))
            else:
                key = f"{bot_id}_{chat_id}_{cmd}"
                if key in active_tasks:
                    return await msg.reply_text("⚠️ Already Running!")
                task = asyncio.create_task(nc_loop(context, bot_id, chat_id, cmd, target))
            
            active_tasks[key] = task
            
            # Track group and task start time
            ACTIVE_GROUPS.add(chat_id)
            if chat_id not in GROUP_TRACKER:
                group_name = msg.chat.title or f"Group_{chat_id}"
                GROUP_TRACKER[chat_id] = group_name
            TASK_START_TIMES[key] = time.time()
            
            await msg.reply_text(f"✅ {cmd.upper()} Started!")

        # STOP COMMANDS
        elif cmd.startswith('d'):
            removed = 0
            base_cmd = cmd.replace('d', '', 1)
            
            if cmd in ['dallnc', 'dallspam', 'dallswipe', 'dallreply']:
                category = cmd.replace('dall', '')
                for key in list(active_tasks.keys()):
                    if category in key and str(chat_id) in key:
                        task = active_tasks.pop(key, None)
                        TASK_START_TIMES.pop(key, None)
                        if task and not task.done():
                            task.cancel()
                            removed += 1
            else:
                for key in list(active_tasks.keys()):
                    if key.endswith(f"_{base_cmd}") and str(chat_id) in key:
                        task = active_tasks.pop(key, None)
                        TASK_START_TIMES.pop(key, None)
                        if task and not task.done():
                            task.cancel()
                            removed += 1
            
            await msg.reply_text(f"✅ Stopped {removed} loop(s)!")

        # DELAY SET
        elif cmd.startswith("setdelay"):
            try:
                if not args:
                    return await msg.reply_text("Usage: ~setdelaync 0.001")
                sec = float(args[0])
                if sec < 0:
                    sec = 1
                dtype = cmd.replace("setdelay", "")
                if dtype in DELAYS:
                    DELAYS[dtype] = sec
                    await msg.reply_text(f"✅ {dtype.upper()} Delay = {sec}s")
                else:
                    await msg.reply_text(f"❌ Invalid! Use: nc, spam, swipe, reply")
            except:
                await msg.reply_text("❌ Invalid number!")

        # SUDO MANAGEMENT
        elif cmd == "sudo":
            await add_sudo(update, context)
        elif cmd == "dsudo":
            await remove_sudo(update, context)
        elif cmd == "sudolist":
            await sudolist_cmd(update, context)
        elif cmd == "refreshsudo":
            await refreshsudo(update, context)

        # BAN/UNBAN
        elif cmd == "ban":
            await ban(update, context)
        elif cmd == "unban":
            await unban(update, context)

        # MUTE/UNMUTE
        elif cmd == "mute":
            await mute(update, context)
        elif cmd == "unmute":
            await unmute(update, context)
        elif cmd == "gcmute":
            await gcmute(update, context)
        elif cmd == "gcunmute":
            await gcunmute(update, context)

        # MESSAGE MANAGEMENT
        elif cmd == "delmsg":
            await delmsg(update, context)

        # LISTS
        elif cmd == "adminlist":
            await adminlist_cmd(update, context)
        elif cmd == "banlist":
            await banlist_cmd(update, context)

        # TOOLS
        elif cmd == "status":
            await status_cmd(update, context)
        elif cmd == "refresh":
            await refresh_cmd(update, context)
        
        # PHOTO COMMANDS 📸
        elif cmd == "savephoto":
            await savephoto_cmd(update, context)
        elif cmd == "startphoto":
            await startphoto_cmd(update, context)
        elif cmd == "stopphoto":
            await stopphoto_cmd(update, context)
        elif cmd == "dphoto":
            await dphoto_cmd(update, context)
        
        # GROUP MANAGEMENT COMMANDS
        elif cmd == "groups":
            await groups_cmd(update, context)
        elif cmd == "statusg":
            await statusg_cmd(update, context)
        elif cmd == "overg":
            await overg_cmd(update, context)
        elif cmd == "leaveg":
            await leaveg_cmd(update, context)

    return handler

# ====================== RUN MULTI BOT ======================
async def run_multibot():
    applications = []
    
    for i, token in enumerate(BOT_TOKENS):
        if not token or "YOUR_BOT_TOKEN" in token:
            continue
        
        try:
            app = Application.builder().token(token).build()
            handler = await make_handler(str(i))
            app.add_handler(CallbackQueryHandler(panel_button_callback))
            app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex(r'^~'), handler))
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            
            applications.append(app)
            print(f"🚀 Bot {i+1} Started - {token[-8:]}")
            
        except Exception as e:
            print(f"❌ Bot {i+1} failed: {e}")

    if applications:
        print("\n✅ Bot is running! Press Ctrl+C to stop.\n")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            for app in applications:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            print("✅ Stopped!")
    else:
        print("❌ No bots started!")

if __name__ == '__main__':
    print("RUDRA SECY BOT  ")
    print("⚡ Sᴘᴇᴇᴅ 0.1ms - Mᴀᴄʜɪɴᴇ Gᴜɴ Mᴏᴅᴇ ")
    print("🚀Aᴜᴛᴏ Rᴇsᴛᴀʀᴛ: Eɴᴀʙʟᴇᴅ")
    print("💨 Iɴsᴀɴᴇ Vᴇʟᴏᴄɪᴛʏ - Fᴀsᴛᴇʀ Tʜᴀɴ Lɪɢʜᴛ")
    print("="*50)
    
    try:
        asyncio.run(run_multibot())
    except KeyboardInterrupt:
        print("\n👋 Stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")