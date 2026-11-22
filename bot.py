
import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DB = "referrals.db"

def setup():
    con = sqlite3.connect(DB)
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            referred_by INTEGER
        )
    """)
    con.commit()
    con.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    ref = None
    if context.args:
        try:
            ref = int(context.args[0])
        except ValueError:
            pass

    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (uid,))
    exists = cur.fetchone()

    if not exists:
        if ref != uid:
            cur.execute(
                "INSERT INTO users VALUES (?, ?)",
                (uid, ref)
            )
        else:
            cur.execute(
                "INSERT INTO users VALUES (?, NULL)", (uid,)
            )

    con.commit()
    con.close()

    await update.message.reply_text(
        f"Welcome {user.first_name}!\n\n"
        f"Your Telegram ID: {uid}\n"
        f"Use /stats to see your referrals."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    con = sqlite3.connect(DB)
    count = con.execute(
        "SELECT COUNT(*) FROM users WHERE referred_by=?",
        (uid,)
    ).fetchone()[0]
    con.close()

    await update.message.reply_text(
        f"Your total referrals: {count}"
    )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    setup()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.run_polling()

if __name__ == "__main__":
    main()
