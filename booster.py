import asyncio
import discord

from config import BOOSTER_ROLE_ID

from database import (
    get_booster_role,
    save_booster_role,
    delete_booster_role,
)


# =========================================================
# KONFIGURASI
# =========================================================

DONATUR_ROLE_NAME = "Donatur"

# Jeda pergantian warna
COLOR_CHANGE_INTERVAL = 5


# =========================================================
# WARNA CUSTOM ROLE
# =========================================================

COLORS = {
    "Hitam": 0x000000,
    "Merah": 0xED4245,
    "Orange": 0xE67E22,
    "Kuning": 0xF1C40F,
    "Hijau": 0x2ECC71,
    "Cyan": 0x1ABC9C,
    "Biru": 0x3498DB,
    "Biru Muda": 0x5DADE2,
    "Ungu": 0x9B59B6,
    "Pink": 0xFF69B4,
    "Magenta": 0xFF00FF,
    "Putih": 0xFFFFFF,
}


# Urutan warna untuk auto rainbow
RAINBOW_COLORS = [
    0x000000,  # Hitam
    0xED4245,  # Merah
    0xE67E22,  # Orange
    0xF1C40F,  # Kuning
    0x2ECC71,  # Hijau
    0x1ABC9C,  # Cyan
    0x3498DB,  # Biru
    0x9B59B6,  # Ungu
    0xFF69B4,  # Pink
]

# =========================================================
# CEK AKSES
# =========================================================

def has_access(member: discord.Member) -> bool:

    # ADMIN BOLEH
    if member.guild_permissions.administrator:
        return True

    booster_role = member.guild.get_role(
        BOOSTER_ROLE_ID
    )

    if booster_role is None:
        return False

    return booster_role in member.roles


# =========================================================
# CARI ROLE DONATUR
# =========================================================

def get_donatur_role(
    guild: discord.Guild
):

    return discord.utils.get(
        guild.roles,
        name=DONATUR_ROLE_NAME
    )


# =========================================================
# PINDAHKAN ROLE DI ATAS DONATUR
# =========================================================

async def move_role_above_donatur(
    role: discord.Role
):

    guild = role.guild

    donatur_role = get_donatur_role(
        guild
    )

    if donatur_role is None:

        print(
            "⚠️ Role 'Donatur' tidak ditemukan."
        )

        return False

    bot_member = guild.me

    if bot_member is None:

        print(
            "❌ Bot member tidak ditemukan."
        )

        return False

    # Role bot harus lebih tinggi dari target
    if bot_member.top_role.position <= donatur_role.position:

        print(
            "❌ Role bot harus berada di atas "
            "role Donatur."
        )

        return False

    # Role yang baru dibuat biasanya berada
    # di bawah role bot.
    try:

        await role.edit(
            position=donatur_role.position + 1,
            reason="YOBLOX Booster Custom Role"
        )

        print(
            f"✅ Role {role.name} dipindahkan "
            "ke atas Donatur."
        )

        return True

    except discord.Forbidden:

        print(
            "❌ Bot tidak memiliki permission "
            "Manage Roles."
        )

        return False

    except discord.HTTPException as error:

        print(
            f"❌ Gagal memindahkan role: {error}"
        )

        return False


# =========================================================
# MODAL BUAT ROLE
# =========================================================

class CreateRoleModal(
    discord.ui.Modal,
    title="Buat Custom Role"
):

    role_name = discord.ui.TextInput(
        label="Nama Role",
        placeholder="Isi nama role yang di dibuat",
        required=True,
        min_length=1,
        max_length=100
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        member = interaction.user

        if not isinstance(
            member,
            discord.Member
        ):
            return

        # =================================================
        # CEK BOOSTER / ADMIN
        # =================================================

        if not has_access(member):

            await interaction.response.send_message(
                "🔒 **Akses Ditolak**\n\n"
                "Custom Role hanya tersedia untuk "
                "**Server Booster YOBLOX**.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK DATABASE
        # =================================================

        existing = get_booster_role(
            interaction.guild.id,
            member.id
        )

        if existing:

            old_role = interaction.guild.get_role(
                existing["role_id"]
            )

            if old_role:

                await interaction.response.send_message(
                    "⚠️ **Kamu sudah memiliki Custom Role.**\n\n"
                    f"Role kamu: {old_role.mention}\n\n"
                    "Satu member hanya dapat memiliki "
                    "**1 Custom Role**.",
                    ephemeral=True
                )

                return

            delete_booster_role(
                interaction.guild.id,
                member.id
            )

        # =================================================
        # NAMA ROLE
        # =================================================

        role_name = self.role_name.value.strip()

        if not role_name:

            await interaction.response.send_message(
                "❌ Nama role tidak boleh kosong.",
                ephemeral=True
            )

            return

        # =================================================
        # FILTER NAMA ROLE
        # =================================================

        banned_words = [
            "admin",
            "administrator",
            "moderator",
            "mod",
            "staff",
            "owner",
            "developer",
            "dev",
            "helper",
            "support",
            "donatur",
        ]

        lower_name = role_name.lower()

        for word in banned_words:

            if word in lower_name:

                await interaction.response.send_message(
                    "❌ Nama role tersebut tidak diperbolehkan.\n\n"
                    "Jangan menggunakan nama yang menyerupai "
                    "role Staff/Admin YOBLOX.",
                    ephemeral=True
                )

                return

        # =================================================
        # PILIH WARNA
        # =================================================

        view = ColorSelectionView(
            role_name=role_name
        )

        await interaction.response.send_message(
            embed=view.create_embed(),
            view=view,
            ephemeral=True
        )


# =========================================================
# DROPDOWN WARNA
# =========================================================

class ColorSelect(
    discord.ui.Select
):

    def __init__(
        self,
        color_number: int
    ):

        options = []

        for name in COLORS:

            options.append(
                discord.SelectOption(
                    label=name,
                    value=name
                )
            )

        if color_number == 1:

            placeholder = "Pilih Warna Pertama"
            custom_id = "yoblox_booster_color_1"

        else:

            placeholder = "Pilih Warna Kedua"
            custom_id = "yoblox_booster_color_2"

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            custom_id=custom_id
        )

        self.color_number = color_number

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        view = self.view

        if not isinstance(
            view,
            ColorSelectionView
        ):
            return

        selected = self.values[0]

        if self.color_number == 1:

            view.first_color = selected

        else:

            view.second_color = selected

        await interaction.response.edit_message(
            embed=view.create_embed(),
            view=view
        )


# =========================================================
# VIEW PILIH WARNA
# =========================================================

class ColorSelectionView(
    discord.ui.View
):

    def __init__(
        self,
        role_name: str
    ):

        super().__init__(
            timeout=300
        )

        self.role_name = role_name

        self.first_color = None
        self.second_color = None

        self.add_item(
            ColorSelect(1)
        )

        self.add_item(
            ColorSelect(2)
        )

    # =====================================================
    # EMBED
    # =====================================================

    def create_embed(self):

        first = (
            self.first_color
            if self.first_color
            else "Belum dipilih"
        )

        second = (
            self.second_color
            if self.second_color
            else "Belum dipilih"
        )

        embed = discord.Embed(
            title="🎨 Pilih Warna Custom Role",
            description=(
                f"**Nama Role:** {self.role_name}\n\n"

                f"**Warna Pertama**\n"
                f"{first}\n\n"

                f"**Warna Kedua**\n"
                f"{second}\n\n"

                "Silakan pilih kedua warna, "
                "lalu tekan **Submit**."
            ),
            color=discord.Color.gold()
        )

        embed.set_footer(
            text="YOBLOX • Booster Custom Role"
        )

        return embed

    # =====================================================
    # SUBMIT
    # =====================================================

    @discord.ui.button(
        label="Submit",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="yoblox_booster_submit"
    )
    async def submit(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        member = interaction.user

        if not isinstance(
            member,
            discord.Member
        ):
            return

        # =================================================
        # CEK AKSES
        # =================================================

        if not has_access(member):

            await interaction.response.send_message(
                "🔒 **Akses Ditolak**\n\n"
                "Fitur ini hanya tersedia untuk "
                "**Server Booster YOBLOX**.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK WARNA
        # =================================================

        if (
            self.first_color is None
            or self.second_color is None
        ):

            await interaction.response.send_message(
                "⚠️ Silakan pilih **kedua warna** terlebih dahulu.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK DATABASE LAGI
        # =================================================

        existing = get_booster_role(
            interaction.guild.id,
            member.id
        )

        if existing:

            old_role = interaction.guild.get_role(
                existing["role_id"]
            )

            if old_role:

                await interaction.response.send_message(
                    "⚠️ **Kamu sudah memiliki Custom Role.**\n\n"
                    f"Role: {old_role.mention}",
                    ephemeral=True
                )

                return

            delete_booster_role(
                interaction.guild.id,
                member.id
            )

        # =================================================
        # CEK BOT
        # =================================================

        bot_member = interaction.guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ Data bot tidak ditemukan.",
                ephemeral=True
            )

            return

        if not bot_member.guild_permissions.manage_roles:

            await interaction.response.send_message(
                "❌ Bot tidak memiliki permission "
                "**Manage Roles**.",
                ephemeral=True
            )

            return

        # =================================================
        # WARNA AWAL
        # =================================================

        primary_color = COLORS[
            self.first_color
        ]

        secondary_color = COLORS[
            self.second_color
        ]

        # =================================================
        # BUAT ROLE
        # =================================================

        try:

            role = await interaction.guild.create_role(
                name=self.role_name,
                colour=discord.Colour(
                    primary_color
                ),
                secondary_colour=discord.Colour(
                    secondary_color
                ),
                hoist=False,
                mentionable=False,
                reason=(
                    "YOBLOX Booster Custom Role | "
                    f"{member} ({member.id})"
                )
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Bot tidak memiliki permission "
                "**Manage Roles**.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"[CREATE ROLE ERROR] {error}"
            )

            await interaction.response.send_message(
                f"❌ Gagal membuat role.\n`{error}`",
                ephemeral=True
            )

            return

        except Exception as error:

            print(
                f"[CREATE ROLE ERROR] {error}"
            )

            await interaction.response.send_message(
                "❌ Terjadi kesalahan saat membuat role.",
                ephemeral=True
            )

            return

        # =================================================
        # PINDAHKAN DI ATAS DONATUR
        # =================================================

        moved = await move_role_above_donatur(
            role
        )

        if not moved:

            print(
                "⚠️ Role berhasil dibuat tetapi "
                "tidak berhasil dipindahkan."
            )

        # =================================================
        # BERIKAN ROLE
        # =================================================

        try:

            await member.add_roles(
                role,
                reason="YOBLOX Booster Custom Role"
            )

        except discord.Forbidden:

            try:

                await role.delete(
                    reason="Failed to assign Custom Role"
                )

            except Exception:
                pass

            await interaction.response.send_message(
                "❌ Role berhasil dibuat tetapi "
                "tidak bisa diberikan kepada kamu.\n\n"
                "Pastikan posisi role bot berada di atas "
                "Custom Role.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            try:

                await role.delete(
                    reason="Failed to assign Custom Role"
                )

            except Exception:
                pass

            await interaction.response.send_message(
                f"❌ Gagal memberikan role.\n`{error}`",
                ephemeral=True
            )

            return

        # =================================================
        # SIMPAN DATABASE
        # =================================================

        try:

            save_booster_role(
                interaction.guild.id,
                member.id,
                role.id
            )

        except Exception as error:

            print(
                f"[DATABASE ERROR] {error}"
            )

            try:

                await member.remove_roles(
                    role,
                    reason="Database error"
                )

            except Exception:
                pass

            try:

                await role.delete(
                    reason="Database error"
                )

            except Exception:
                pass

            await interaction.response.send_message(
                "❌ Custom Role gagal disimpan "
                "ke database.",
                ephemeral=True
            )

            return

        # =================================================
        # BERHASIL
        # =================================================

        embed = discord.Embed(
            title="🎉 Custom Role Berhasil Dibuat!",
            description=(
                f"Role kamu: {role.mention}\n\n"

                f"🎨 **Warna Pertama:** "
                f"{self.first_color}\n"

                f"🎨 **Warna Kedua:** "
                f"{self.second_color}\n\n"

                "Role otomatis ditempatkan "
                "**di atas Donatur**.\n\n"

                "🌈 Warna role akan berganti "
                "secara otomatis.\n\n"

                "Terima kasih sudah menjadi "
                "**Booster YOBLOX**! 🚀"
            ),
            color=discord.Colour(
                primary_color
            )
        )

        embed.set_footer(
            text="YOBLOX • Booster Custom Role"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )


# =========================================================
# PANEL UTAMA
# =========================================================

class BoosterPanelView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

    # =====================================================
    # BUAT ROLE
    # =====================================================

    @discord.ui.button(
        label="Buat Role",
        emoji="🎨",
        style=discord.ButtonStyle.success,
        custom_id="yoblox_booster_create"
    )
    async def create_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        member = interaction.user

        if not isinstance(
            member,
            discord.Member
        ):
            return

        # =================================================
        # CEK AKSES
        # =================================================

        if not has_access(member):

            await interaction.response.send_message(
                "🔒 **Akses Ditolak**\n\n"
                "Custom Role hanya bisa digunakan "
                "oleh **Server Booster YOBLOX**.\n\n"
                "🚀 Boost Server terlebih dahulu "
                "untuk mendapatkan akses.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK DATABASE
        # =================================================

        existing = get_booster_role(
            interaction.guild.id,
            member.id
        )

        if existing:

            role = interaction.guild.get_role(
                existing["role_id"]
            )

            if role:

                await interaction.response.send_message(
                    "⚠️ **Kamu sudah memiliki Custom Role.**\n\n"
                    f"Role kamu: {role.mention}\n\n"
                    "Satu member hanya dapat memiliki "
                    "**1 Custom Role**.",
                    ephemeral=True
                )

                return

            delete_booster_role(
                interaction.guild.id,
                member.id
            )

        # =================================================
        # BUKA MODAL
        # =================================================

        await interaction.response.send_modal(
            CreateRoleModal()
        )

    # =====================================================
    # HAPUS ROLE
    # =====================================================

    @discord.ui.button(
        label="Hapus Role",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="yoblox_booster_delete"
    )
    async def delete_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        member = interaction.user

        if not isinstance(
            member,
            discord.Member
        ):
            return

        # =================================================
        # CEK AKSES
        # =================================================

        if not has_access(member):

            await interaction.response.send_message(
                "🔒 **Akses Ditolak**\n\n"
                "Fitur ini hanya tersedia untuk "
                "**Server Booster YOBLOX**.",
                ephemeral=True
            )

            return

        # =================================================
        # DATABASE
        # =================================================

        data = get_booster_role(
            interaction.guild.id,
            member.id
        )

        if not data:

            await interaction.response.send_message(
                "❌ Kamu belum memiliki Custom Role.",
                ephemeral=True
            )

            return

        # =================================================
        # ROLE DISCORD
        # =================================================

        role = interaction.guild.get_role(
            data["role_id"]
        )

        if role is None:

            delete_booster_role(
                interaction.guild.id,
                member.id
            )

            await interaction.response.send_message(
                "ℹ️ Custom Role sudah tidak ditemukan.\n"
                "Data role telah dibersihkan.",
                ephemeral=True
            )

            return

        # =================================================
        # CEK POSISI ROLE
        # =================================================

        bot_member = interaction.guild.me

        if bot_member is None:

            await interaction.response.send_message(
                "❌ Data bot tidak ditemukan.",
                ephemeral=True
            )

            return

        if role >= bot_member.top_role:

            await interaction.response.send_message(
                "❌ Bot tidak dapat menghapus role ini.\n\n"
                "Pastikan role bot berada di atas "
                "Custom Role.",
                ephemeral=True
            )

            return

        # =================================================
        # HAPUS
        # =================================================

        try:

            await role.delete(
                reason=(
                    "YOBLOX Booster Custom Role deleted | "
                    f"{member} ({member.id})"
                )
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ Bot tidak memiliki izin "
                "untuk menghapus role.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                f"❌ Gagal menghapus role.\n`{error}`",
                ephemeral=True
            )

            return

        # =================================================
        # DATABASE
        # =================================================

        delete_booster_role(
            interaction.guild.id,
            member.id
        )

        # =================================================
        # SELESAI
        # =================================================

        await interaction.response.send_message(
            "🗑️ **Custom Role berhasil dihapus.**\n\n"
            "Kamu dapat membuat Custom Role baru "
            "selama masih menjadi **Server Booster YOBLOX**.",
            ephemeral=True
        )


# =========================================================
# AUTO HAPUS SAAT BERHENTI BOOST
# =========================================================

async def handle_booster_update(
    before: discord.Member,
    after: discord.Member
):

    booster_role = after.guild.get_role(
        BOOSTER_ROLE_ID
    )

    if booster_role is None:
        return

    was_booster = (
        booster_role in before.roles
    )

    is_booster = (
        booster_role in after.roles
    )

    # Tidak ada perubahan status booster
    if was_booster == is_booster:
        return

    # =====================================================
    # BERHENTI BOOST
    # =====================================================

    if was_booster and not is_booster:

        # ADMIN TETAP BOLEH MEMILIKI ROLE
        if after.guild_permissions.administrator:
            return

        data = get_booster_role(
            after.guild.id,
            after.id
        )

        if not data:
            return

        role = after.guild.get_role(
            data["role_id"]
        )

        if role:

            bot_member = after.guild.me

            if (
                bot_member
                and role < bot_member.top_role
            ):

                try:

                    await role.delete(
                        reason=(
                            "Member stopped boosting YOBLOX"
                        )
                    )

                    print(
                        f"🗑️ Custom Role {role.id} "
                        f"dihapus karena {after} "
                        "berhenti boost."
                    )

                except discord.HTTPException as error:

                    print(
                        f"❌ Gagal menghapus role: {error}"
                    )

        delete_booster_role(
            after.guild.id,
            after.id
        )


# =========================================================
# AUTO COLOR MANAGER
# =========================================================

class AutoColorManager:

    def __init__(
        self,
        bot: discord.Client
    ):

        self.bot = bot

        self.running = False
        self.task = None

        self.color_index = 0

    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.task is None:

            self.task = asyncio.create_task(
                self.color_loop()
            )

    # =====================================================
    # COLOR LOOP
    # =====================================================

    async def color_loop(self):

        await self.bot.wait_until_ready()

        self.running = True

        print(
            "🌈 Auto Color Custom Role aktif."
        )

        while not self.bot.is_closed():

            try:

                await self.update_all_roles()

            except Exception as error:

                print(
                    f"❌ Auto Color Error: {error}"
                )

            await asyncio.sleep(
                COLOR_CHANGE_INTERVAL
            )

    # =====================================================
    # UPDATE SEMUA ROLE
    # =====================================================

    async def update_all_roles(self):

        color_value = RAINBOW_COLORS[
            self.color_index
        ]

        self.color_index += 1

        if self.color_index >= len(
            RAINBOW_COLORS
        ):

            self.color_index = 0

        color = discord.Colour(
            color_value
        )

        # Ambil semua guild
        for guild in self.bot.guilds:

            try:

                # Ambil data Custom Role
                # dari setiap member booster
                for member in guild.members:

                    data = get_booster_role(
                        guild.id,
                        member.id
                    )

                    if not data:
                        continue

                    role = guild.get_role(
                        data["role_id"]
                    )

                    if role is None:
                        continue

                    # Pastikan role memang dimiliki member
                    if role not in member.roles:
                        continue

                    # Pastikan bot bisa edit role
                    bot_member = guild.me

                    if bot_member is None:
                        continue

                    if role >= bot_member.top_role:
                        continue

                    try:

                        await role.edit(
                            colour=color,
                            reason="YOBLOX Booster Auto Color"
                        )

                    except discord.Forbidden:

                        print(
                            f"⚠️ Tidak bisa mengubah "
                            f"warna role {role.id}"
                        )

                    except discord.HTTPException:
                        pass

            except Exception as error:

                print(
                    f"❌ Guild Auto Color Error "
                    f"({guild.id}): {error}"
                )


# =========================================================
# SETUP AUTO COLOR
# =========================================================

auto_color_manager = None


def start_auto_color(
    bot: discord.Client
):

    global auto_color_manager

    if auto_color_manager is None:

        auto_color_manager = AutoColorManager(
            bot
        )

        auto_color_manager.start()