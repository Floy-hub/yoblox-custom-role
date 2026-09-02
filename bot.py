import discord
from discord.ext import commands

from config import TOKEN, BOOSTER_CHANNEL_ID
from database import init_database
from booster import BoosterPanelView, handle_booster_update


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True


# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print(f"✅ Bot login sebagai {bot.user}")

    # Database
    try:
        init_database()
        print("✅ Database berhasil terhubung.")
    except Exception as error:
        print(f"❌ Database error: {error}")
        return

    # Persistent button
    bot.add_view(
        BoosterPanelView()
    )

    print("✅ Booster Custom Role aktif.")
    print(f"📌 Channel ID: {BOOSTER_CHANNEL_ID}")


# =========================================================
# MEMBER UPDATE
# =========================================================

@bot.event
async def on_member_update(
    before: discord.Member,
    after: discord.Member
):

    await handle_booster_update(
        before,
        after
    )


# =========================================================
# SETUP PANEL
# =========================================================

@bot.command(
    name="setupbooster"
)
@commands.has_permissions(
    administrator=True
)
async def setup_booster(ctx):

    channel = bot.get_channel(
        BOOSTER_CHANNEL_ID
    )

    if channel is None:

        await ctx.send(
            "❌ Channel Booster Custom Role tidak ditemukan.",
            delete_after=5
        )
        return

    embed = discord.Embed(
        title="🚀 Booster Custom Role",
        description=(
            "Sebagai bentuk apresiasi untuk kamu yang telah "
            "membantu support **YOBLOX** dengan melakukan Boost "
            "Server, kamu mendapatkan akses untuk membuat "
            "Custom Role sendiri.\n\n"

            "✨ **FITUR**\n"
            "• Buat role dengan nama pilihanmu\n"
            "• Pilih dua warna untuk Custom Role\n"
            "• Custom Role khusus Server Booster\n"
            "• Bisa menghapus role sendiri\n"
            "• 1 member hanya dapat memiliki 1 Custom Role\n\n"

            "📜 **KETENTUAN**\n"
            "1. Custom Role hanya tersedia selama kamu menjadi "
            "**Server Booster YOBLOX**.\n\n"

            "2. Dilarang menggunakan nama yang mengandung unsur "
            "**SARA, penghinaan, seksual, atau provokasi**.\n\n"

            "3. Dilarang membuat role yang menyerupai "
            "**Admin, Moderator, atau Staff YOBLOX**.\n\n"

            "4. Dilarang menggunakan Custom Role untuk kegiatan "
            "**jual beli atau perdagangan**.\n\n"

            "⚠️ Role yang melanggar ketentuan dapat "
            "**dihapus tanpa pemberitahuan**.\n\n"

            "💎 Terima kasih sudah support **YOBLOX** "
            "dengan Boost Server!"
        ),
        color=discord.Color.gold()
    )

    embed.set_footer(
        text="YOBLOX • Booster Custom Role"
    )

    await channel.send(
        embed=embed,
        view=BoosterPanelView()
    )

    await ctx.send(
        f"✅ Panel berhasil dikirim ke {channel.mention}.",
        delete_after=5
    )


# =========================================================
# ERROR COMMAND
# =========================================================

@setup_booster.error
async def setup_booster_error(
    ctx,
    error
):

    if isinstance(
        error,
        commands.MissingPermissions
    ):

        await ctx.send(
            "❌ Hanya Administrator yang dapat "
            "menggunakan command ini.",
            delete_after=5
        )


# =========================================================
# TOKEN
# =========================================================

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN belum diisi di file .env"
    )


bot.run(TOKEN)