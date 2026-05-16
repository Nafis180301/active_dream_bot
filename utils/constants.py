"""
Constants for Active Dream Bot.
Emojis, message templates, service/country definitions.
"""

# ============================================================
# SERVICE DEFINITIONS
# ============================================================

SERVICES = {
    "facebook": {"name": "Facebook", "emoji": "📘", "code": "facebook"},
    "instagram": {"name": "Instagram", "emoji": "📸", "code": "instagram"},
    "whatsapp": {"name": "WhatsApp", "emoji": "💬", "code": "whatsapp"},
    "telegram": {"name": "Telegram", "emoji": "✈️", "code": "telegram"},
    "twitter": {"name": "Twitter/X", "emoji": "🐦", "code": "twitter"},
    "google": {"name": "Google", "emoji": "🔍", "code": "google"},
    "tiktok": {"name": "TikTok", "emoji": "🎵", "code": "tiktok"},
    "snapchat": {"name": "Snapchat", "emoji": "👻", "code": "snapchat"},
    "discord": {"name": "Discord", "emoji": "🎮", "code": "discord"},
    "microsoft": {"name": "Microsoft", "emoji": "🪟", "code": "microsoft"},
    "yahoo": {"name": "Yahoo", "emoji": "📧", "code": "yahoo"},
    "amazon": {"name": "Amazon", "emoji": "📦", "code": "amazon"},
    "any": {"name": "Any/Other", "emoji": "📱", "code": "any"},
}

# ============================================================
# COUNTRY DEFINITIONS (Popular ones for OTP)
# ============================================================

COUNTRIES = {
    "russia": {"name": "Russia", "flag": "🇷🇺", "code": "russia"},
    "usa": {"name": "USA", "flag": "🇺🇸", "code": "usa"},
    "uk": {"name": "UK", "flag": "🇬🇧", "code": "england"},
    "india": {"name": "India", "flag": "🇮🇳", "code": "india"},
    "indonesia": {"name": "Indonesia", "flag": "🇮🇩", "code": "indonesia"},
    "philippines": {"name": "Philippines", "flag": "🇵🇭", "code": "philippines"},
    "ethiopia": {"name": "Ethiopia", "flag": "🇪🇹", "code": "ethiopia"},
    "kenya": {"name": "Kenya", "flag": "🇰🇪", "code": "kenya"},
    "nigeria": {"name": "Nigeria", "flag": "🇳🇬", "code": "nigeria"},
    "bangladesh": {"name": "Bangladesh", "flag": "🇧🇩", "code": "bangladesh"},
    "pakistan": {"name": "Pakistan", "flag": "🇵🇰", "code": "pakistan"},
    "brazil": {"name": "Brazil", "flag": "🇧🇷", "code": "brazil"},
    "egypt": {"name": "Egypt", "flag": "🇪🇬", "code": "egypt"},
    "vietnam": {"name": "Vietnam", "flag": "🇻🇳", "code": "vietnam"},
    "ukraine": {"name": "Ukraine", "flag": "🇺🇦", "code": "ukraine"},
    "kazakhstan": {"name": "Kazakhstan", "flag": "🇰🇿", "code": "kazakhstan"},
    "myanmar": {"name": "Myanmar", "flag": "🇲🇲", "code": "myanmar"},
    "colombia": {"name": "Colombia", "flag": "🇨🇴", "code": "colombia"},
    "mexico": {"name": "Mexico", "flag": "🇲🇽", "code": "mexico"},
    "thailand": {"name": "Thailand", "flag": "🇹🇭", "code": "thailand"},
}

# ============================================================
# MESSAGE TEMPLATES
# ============================================================

MSG_WELCOME_NEW = """
🔒 *Welcome to Active Dream!*

This is a private bot. You need admin approval to access our services.

Please click the button below to request access.
"""

MSG_WELCOME_PENDING = """
⏳ *Access Pending*

Your access request has been submitted and is waiting for admin approval.

Please be patient — an admin will review your request shortly.
"""

MSG_WELCOME_REJECTED = """
❌ *Access Denied*

Your access request was rejected by the admin.

If you believe this is a mistake, you can request access again.
"""

MSG_WELCOME_BANNED = """
🚫 *Account Banned*

Your account has been banned from using this bot.

Contact the admin if you think this is an error.
"""

MSG_ACCESS_APPROVED = """
🎉 *Congratulations!*

Your access has been *approved*! 🎊

🤖 *Bot:* Active Dream
📱 *OTP Group:* Active Dream OTP
📢 *Channel:* Active Dream Channel

You can now use all bot features. Click /start to begin!
"""

MSG_MAIN_MENU = """
👋 *Welcome back, {name}!*

🤖 *Active Dream* — Virtual Number & OTP Bot

💰 *Balance:* ${balance:.2f}

Choose an option below:
"""

MSG_NUMBER_ASSIGNED = """
✅ *Number Assigned!*

📱 *{service}* | `{number}` | {country} {flag}

🏃 *Wait, Stay here... OTP Coming Soon!*

⏱ _Checking for OTP every {interval}s (max {max_wait}s)..._
"""

MSG_OTP_RECEIVED = """
🎉 *OTP Received!*

📱 *{service}* | `{number}` | {country} {flag}

🔑 *OTP Code:* `{code}`

📩 *Full SMS:* _{sms_text}_
"""

MSG_NO_OTP = """
⏰ *OTP Timeout*

📱 *{service}* | `{number}` | {country} {flag}

No OTP was received within the time limit.
Your balance has been refunded.
"""

MSG_ADMIN_ACCESS_REQUEST = """
🔔 *New Access Request!*

👤 *Name:* {name}
🆔 *Username:* @{username}
🔢 *User ID:* `{user_id}`
📅 *Requested:* {time}

Choose an action:
"""

MSG_ADMIN_PANEL = """
👑 *Admin Panel — Active Dream*

📊 *Statistics:*
├ 👥 Total Users: {total}
├ ✅ Approved: {approved}
├ ⏳ Pending: {pending}
├ ❌ Rejected: {rejected}
└ 🚫 Banned: {banned}

📱 *Numbers:*
├ 📊 Total Requested: {num_total}
├ ✅ Completed: {num_completed}
├ 🔄 Active: {num_active}
└ ❌ Cancelled: {num_cancelled}
"""

MSG_SELECT_SERVICE = """
📱 *Select a Service*

Choose the platform you need a number for:
"""

MSG_SELECT_COUNTRY = """
🌍 *Select a Country*

Service: *{service}* {emoji}

Choose a country for your virtual number:
"""

MSG_BALANCE = """
💰 *Your Balance*

💵 Current Balance: *${balance:.2f}*

📜 *Recent Transactions:*
{transactions}
"""

MSG_NO_ACTIVE_NUMBERS = """
📱 *Active Numbers*

You don't have any active numbers right now.

Use "📱 Get Number" to request a new number.
"""

MSG_ACTIVE_NUMBERS_HEADER = """
📱 *Your Active Numbers*

"""

MSG_WITHDRAW_INFO = """
🤑 *Withdraw*

💵 Current Balance: *${balance:.2f}*

To request a withdrawal, please contact the admin.
Minimum withdrawal: *$5.00*
"""
