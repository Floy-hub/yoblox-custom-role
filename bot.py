import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import init_database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN belum ditemukan di environment variables.")


# =========================
# INTENTS
# =========================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True


# =========================
# BOT
# =========================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# =========================
# LOAD BOOSTER
# =========================

async def load_extensions():
    try:
        await bot.load_extension("booster")
        print("✅ booster.py berhasil dimuat.")
    except Exception as e:
        print(f"❌ Gagal memuat booster.py: {e}")


# =========================
# READY
# =========================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"🤖 Bot       : {bot.user}")
    print(f"🆔 Bot ID    : {bot.user.id}")
    print(f"🌐 Server    : {len(bot.guilds)}")
    print("=" * 50)

    # Inisialisasi database
    try:
        init_database()
        print("✅ Database berhasil diinisialisasi.")
    except Exception as e:
        print(f"❌ Database Error: {e}")

    # Status bot
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="YOBLOX Booster"
    )

    await bot.change_presence(
        status=discord.Status.online,
        activity=activity
    )


# =========================
# ERROR HANDLER
# =========================

@bot.event
async def on_command_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    print(
        f"❌ Command Error: {error}"
    )


# =========================
# START BOT
# =========================

async def main():

    async with bot:

        await load_extensions()

        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot dihentikan.")
