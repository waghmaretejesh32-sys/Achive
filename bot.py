import json
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN =  "8658792467:AAEjtNIFhN0t3Pd99ICE36-nuNm1VR85BMQ"

DATA_FILE = "players.json"
ADMIN_FILE = "admins.json"
USER_FILE = "users.json"

DEFAULT_ADMINS = [6224332712, 8000127916]


def load_json(file, default):
    if not os.path.exists(file):
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_admins():
    admins = load_json(ADMIN_FILE, DEFAULT_ADMINS.copy())
    for a in DEFAULT_ADMINS:
        if a not in admins:
            admins.append(a)
    save_json(ADMIN_FILE, admins)
    return admins


def is_admin(user_id):
    return user_id in get_admins()


def save_user(user_id):
    users = load_json(USER_FILE, [])
    if user_id not in users:
        users.append(user_id)
        save_json(USER_FILE, users)


def load_players():
    return load_json(DATA_FILE, {})


def save_players(data):
    save_json(DATA_FILE, data)


def get_player(data, username):
    username = username.replace("@", "")
    if username not in data:
        data[username] = {
            "achievements": [],
            "stats": {"matches": 0, "runs": 0, "wickets": 0}
        }
    return data[username]


HELP_TEXT = """
📌 GPL Seasons Winners Bot Commands

👥 Public:
/start
/achievements @user
/stats @user
/topruns
/topwickets
/list
/myid
/help

👑 Admin:
/addachievement @user GPL S1 WINNER 🏆
/removeachievement @user 1
/addstats @user matches 10 runs 250 wickets 8
/promoteadmin USER_ID
/removeadmin USER_ID
/adminlist
/broadcast message
"""


async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Start GPL Bot"),
        BotCommand("achievements", "Show player achievements"),
        BotCommand("stats", "Show player stats"),
        BotCommand("topruns", "Top run scorers"),
        BotCommand("topwickets", "Top wicket takers"),
        BotCommand("list", "Player list"),
        BotCommand("myid", "Show your ID"),
        BotCommand("help", "Help menu"),
        BotCommand("addachievement", "Add achievement Admin"),
        BotCommand("removeachievement", "Remove achievement Admin"),
        BotCommand("addstats", "Add stats Admin"),
        BotCommand("promoteadmin", "Add admin"),
        BotCommand("removeadmin", "Remove admin"),
        BotCommand("adminlist", "Show admin list"),
        BotCommand("broadcast", "Send message to all users"),
    ]
    await app.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    keyboard = [
        [InlineKeyboardButton("🏆 Achievements", callback_data="ach_help")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats_help")],
        [InlineKeyboardButton("🔥 Top Runs", callback_data="topruns")],
        [InlineKeyboardButton("🎯 Top Wickets", callback_data="topwickets")],
        [InlineKeyboardButton("📋 Player List", callback_data="list")],
        [InlineKeyboardButton("🆔 My ID", callback_data="myid")],
        [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]

    await update.message.reply_text(
        "🏏 Welcome to GPL Seasons Winners Bot\n\n"
        "🏆 GPL Winners: S1 to S10\n"
        "📊 Player Stats\n"
        "🏅 Player Achievements\n\n"
        "Choose option below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "help":
        await q.message.reply_text(HELP_TEXT)

    elif q.data == "ach_help":
        await q.message.reply_text("Use:\n/achievements @user")

    elif q.data == "stats_help":
        await q.message.reply_text("Use:\n/stats @user")

    elif q.data == "myid":
        await q.message.reply_text(f"🆔 Your ID: `{q.from_user.id}`", parse_mode="Markdown")

    elif q.data == "list":
        await list_players(update, context)

    elif q.data == "topruns":
        await topruns(update, context)

    elif q.data == "topwickets":
        await topwickets(update, context)

    elif q.data == "adminlist":
        await adminlist(update, context)

    elif q.data == "admin_panel":
        if not is_admin(q.from_user.id):
            await q.message.reply_text("❌ Only admin can use this panel.")
            return

        keyboard = [
            [InlineKeyboardButton("🏆 GPL S1 WINNER", callback_data="s1"),
             InlineKeyboardButton("🏆 GPL S2 WINNER", callback_data="s2")],
            [InlineKeyboardButton("🏆 GPL S3 WINNER", callback_data="s3"),
             InlineKeyboardButton("🏆 GPL S4 WINNER", callback_data="s4")],
            [InlineKeyboardButton("🏆 GPL S5 WINNER", callback_data="s5"),
             InlineKeyboardButton("🏆 GPL S6 WINNER", callback_data="s6")],
            [InlineKeyboardButton("🏆 GPL S7 WINNER", callback_data="s7"),
             InlineKeyboardButton("🏆 GPL S8 WINNER", callback_data="s8")],
            [InlineKeyboardButton("🏆 GPL S9 WINNER", callback_data="s9"),
             InlineKeyboardButton("🏆 GPL S10 WINNER", callback_data="s10")],
            [InlineKeyboardButton("👑 Admin List", callback_data="adminlist")]
        ]

        await q.message.reply_text(
            "👑 Admin Panel\n\n"
            "/addachievement @user GPL S1 WINNER 🏆\n"
            "/addstats @user matches 10 runs 250 wickets 8\n"
            "/broadcast message",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif q.data.startswith("s"):
        season = q.data.replace("s", "")
        await q.message.reply_text(
            f"Copy command:\n/addachievement @user GPL S{season} WINNER 🏆"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: `{update.effective_user.id}`", parse_mode="Markdown")


async def promoteadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Only admin can promote admin.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Use: /promoteadmin USER_ID")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ USER_ID number me dalo.")
        return

    admins = get_admins()

    if user_id not in admins:
        admins.append(user_id)
        save_json(ADMIN_FILE, admins)

    await update.message.reply_text(f"✅ New admin added: {user_id}")


async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Only admin can remove admin.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Use: /removeadmin USER_ID")
        return

    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ USER_ID number me dalo.")
        return

    if user_id in DEFAULT_ADMINS:
        await update.message.reply_text("❌ Default admin remove nahi ho sakta.")
        return

    admins = get_admins()

    if user_id in admins:
        admins.remove(user_id)
        save_json(ADMIN_FILE, admins)

    await update.message.reply_text(f"✅ Admin removed: {user_id}")


async def adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = get_admins()
    text = "👑 Admin List\n\n"

    for i, a in enumerate(admins, 1):
        text += f"{i}. `{a}`\n"

    if update.callback_query:
        await update.callback_query.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


async def addachievement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Only admin can add achievements.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Use: /addachievement @user GPL S1 WINNER 🏆")
        return

    username = context.args[0]
    achievement = " ".join(context.args[1:])

    data = load_players()
    player = get_player(data, username)
    player["achievements"].append(achievement)
    save_players(data)

    await update.message.reply_text(f"✅ Added for {username}\n🏆 {achievement}")


async def removeachievement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Only admin can remove achievements.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Use: /removeachievement @user 1")
        return

    username = context.args[0].replace("@", "")

    try:
        index = int(context.args[1]) - 1
    except:
        await update.message.reply_text("❌ Number dalo. Example: /removeachievement @user 1")
        return

    data = load_players()

    if username not in data or index < 0 or index >= len(data[username]["achievements"]):
        await update.message.reply_text("❌ Achievement not found.")
        return

    removed = data[username]["achievements"].pop(index)
    save_players(data)

    await update.message.reply_text(f"✅ Removed:\n{removed}")


async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Use: /achievements @user")
        return

    username = context.args[0].replace("@", "")
    data = load_players()

    if username not in data or not data[username]["achievements"]:
        await update.message.reply_text("❌ No achievements found.")
        return

    text = f"🏆 @{username}'s Achievements\n\n"
    for i, ach in enumerate(data[username]["achievements"], 1):
        text += f"{i}. {ach}\n"

    await update.message.reply_text(text)


async def addstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Only admin can add stats.")
        return

    if len(context.args) != 7:
        await update.message.reply_text("Use: /addstats @user matches 10 runs 250 wickets 8")
        return

    username = context.args[0]

    try:
        matches = int(context.args[2])
        runs = int(context.args[4])
        wickets = int(context.args[6])
    except:
        await update.message.reply_text("❌ Stats number me dalo.")
        return

    data = load_players()
    player = get_player(data, username)

    player["stats"]["matches"] += matches
    player["stats"]["runs"] += runs
    player["stats"]["wickets"] += wickets

    save_players(data)

    await update.message.reply_text("✅ Stats added successfully.")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Use: /stats @user")
        return

    username = context.args[0].replace("@", "")
    data = load_players()

    if username not in data:
        await update.message.reply_text("❌ Player not found.")
        return

    s = data[username]["stats"]

    await update.message.reply_text(
        f"📊 @{username}'s Stats\n\n"
        f"🏏 Matches: {s['matches']}\n"
        f"🔥 Runs: {s['runs']}\n"
        f"🎯 Wickets: {s['wickets']}"
    )


async def topruns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_players()
    ranking = sorted(data.items(), key=lambda x: x[1]["stats"]["runs"], reverse=True)

    text = "🔥 Top Runs Leaderboard\n\n"

    if not ranking:
        text += "No players found."
    else:
        for i, (user, info) in enumerate(ranking[:10], 1):
            text += f"{i}. @{user} - {info['stats']['runs']} runs\n"

    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)


async def topwickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_players()
    ranking = sorted(data.items(), key=lambda x: x[1]["stats"]["wickets"], reverse=True)

    text = "🎯 Top Wickets Leaderboard\n\n"

    if not ranking:
        text += "No players found."
    else:
        for i, (user, info) in enumerate(ranking[:10], 1):
            text += f"{i}. @{user} - {info['stats']['wickets']} wickets\n"

    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)


async def list_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_players()

    if not data:
        text = "❌ No players found."
    else:
        text = "📋 Player List\n\n"
        for i, username in enumerate(data.keys(), 1):
            text += f"{i}. @{username}\n"

    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Only admin can broadcast.")
        return

    if not context.args:
        await update.message.reply_text("Use: /broadcast Your message here")
        return

    msg = " ".join(context.args)
    users = load_json(USER_FILE, [])

    sent = 0
    failed = 0

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 Broadcast\n\n{msg}")
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(f"✅ Broadcast done\nSent: {sent}\nFailed: {failed}")


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(set_bot_commands).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("myid", myid))

    app.add_handler(CommandHandler("addachievement", addachievement))
    app.add_handler(CommandHandler("removeachievement", removeachievement))
    app.add_handler(CommandHandler("achievements", achievements))

    app.add_handler(CommandHandler("addstats", addstats))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("topruns", topruns))
    app.add_handler(CommandHandler("topwickets", topwickets))
    app.add_handler(CommandHandler("list", list_players))

    app.add_handler(CommandHandler("promoteadmin", promoteadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("adminlist", adminlist))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(CallbackQueryHandler(buttons))

    print("GPL Seasons Winners Bot Started ✅")
    app.run_polling()


if __name__ == "__main__":
    main()
