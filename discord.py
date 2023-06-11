import re
import os
import json
import logging
import random
import datetime

import requests
import disnake
import json
import discord
from discord.ext import commands
from disnake.ext import commands

from collections import defaultdict
import asyncio

from webserver import keep_alive

import subprocess
import shutil

warnings = {
    "member_id_1": ["warning_1", "warning_2"],
    "member_id_2": ["warning_3"]
}

with open("warnings.json", "w") as f:
    json.dump(warnings, f)

# Игнорирование сообщений бота, чтобы избежать бесконечных циклов

users = {}

client = commands.Bot(command_prefix='!', intents=disnake.Intents.all())


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.message_count = 0
        self.level = 0

    def send_message(self):
        self.message_count += 1
        self.check_level()

    def check_level(self):
        levels = {
            1: 10,
            2: 50,
            3: 100,
            4: 200,
            5: 500,
            6: 1000,
            7: 2000,
            8: 3000,
            9: 5000
        }

        for level, message_limit in levels.items():
            if self.message_count >= message_limit:
                self.level = level


@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = message.author.id
    
    if user_id not in users:
        users[user_id] = User(user_id)
    
    try:
        users[user_id].send_message()
    except Exception as e:
        print(f"Failed to process message from user {user_id}: {str(e)}")
    
    await client.process_commands(message)


class buttons_class(disnake.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @disnake.ui.button(label="Машинист", style=disnake.ButtonStyle.green)
    async def button1(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role_id = 1021413103365279764
        guild = interaction.guild
        role = guild.get_role(role_id)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"Роль **<@{role}>** успешно выдана!", ephemeral=True)
        self.value = True


    @disnake.ui.button(label="Строитель", style=disnake.ButtonStyle.green)
    async def button2(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role_id = 1035227644570120403
        guild = interaction.guild
        role = guild.get_role(role_id)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"Роль **<@{role}>** успешно выдана!", ephemeral=True)
        self.value = False


# Slash команды
@client.slash_command()
@commands.has_role(1059480358556545085)  # Проверка на наличие роли
async def server(ctx):
    user = ctx.author

    if ctx.channel.id == 1003740091430223872:
        # Создание встроенного сообщения
        embed = disnake.Embed(description="Ссылка на сборку была успешно отправлена в личные сообщения.", color=disnake.Color.from_rgb(252, 185, 0))

        # Отправка встроенного сообщения в канал
        await ctx.send(embed=embed)

        # Создание встроенного сообщения для личных сообщений
        embed_dm = disnake.Embed(color=disnake.Color.from_rgb(252, 185, 0))

        # Добавление ссылки во встроенное сообщение для личных сообщений
        embed_dm.add_field(name="Скачать сборку", value="[Ссылка](https://cdn.discordapp.com/attachments/1022521502328950867/1116333592138760202/TexelRailway.zip)", inline=False)

        # Добавление информации о вызывающем пользователе в footer
        embed_dm.set_footer(text=f"Вызвано: {user}\nНи в коем случае не распространяйте сборку сервера!")

        # Отправка встроенного сообщения в личные сообщения
        await user.send(embed=embed_dm)
    else:
        # Отправка сообщения о недостатке прав в текущем канале
        await ctx.send("У вас недостаточно прав для выполнения данной команды в данном канале.")




@client.slash_command()
@commands.has_permissions(administrator=True)
async def embed(ctx, *, description=None, member: disnake.Member = None):
    channel = ctx.channel
    embed = disnake.Embed(description=description, color=disnake.Color.gold())
    if member:
        mention = member.mention
        embed.description = f"{mention} {description}"
    await channel.send(embed=embed)

@client.slash_command(name="server_info", description="Shows information about the server")
async def server_info(inter):
    embed = disnake.Embed(title=inter.guild.name, color=0xfcb900)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/950049591871561808/1105545200027324506/2023-05-06_15.13.03.png")
    embed.add_field(name="Server ID", value=inter.guild.id, inline=True)
    embed.add_field(name="Owner", value=inter.guild.owner, inline=True)
    embed.add_field(name="Member Count", value=inter.guild.member_count, inline=True)
    embed.add_field(name="Channel Count", value=len(inter.guild.channels), inline=True)
    embed.add_field(name="Verification Level", value=inter.guild.verification_level, inline=True)
    embed.add_field(name="Role Count", value=len(inter.guild.roles), inline=True)
    embed.add_field(name="Emoji Count", value=len(inter.guild.emojis), inline=True)
    embed.add_field(name="Server Creation Date", value=inter.guild.created_at.strftime("%d.%m.%Y %H:%M:%S"), inline=False)
    embed.set_footer(text=f"Message sent by - {inter.author.name}")
    await inter.response.send_message(embed=embed)


@client.slash_command(name='toxic', description='Deletes messages containing forbidden words and assigns a role.')
@commands.has_permissions(manage_messages=True)
async def toxic(ctx, user: disnake.Member):
    """Deletes messages containing forbidden words and assigns a role to the specified user."""

    forbidden_words = ['forbidden_word1', 'forbidden_word2']  # Replace with your forbidden words

    def contains_forbidden_words(message):
        for word in forbidden_words:
            if re.search(r'\b' + re.escape(word) + r'\b', message.content, re.IGNORECASE):
                return True
        return False

    deleted_messages = await ctx.channel.purge(check=contains_forbidden_words)

    response = f"Deleted {len(deleted_messages)} messages containing forbidden words."
    await ctx.send(response, delete_after=5)

    role_id = 1084778150745088010  # Replace with the ID of the role to assign
    role = ctx.guild.get_role(role_id)
    if role is None:
        await ctx.send(f"Role with ID {role_id} not found.")
        return

    member = user
    await member.remove_roles(*member.roles)  # Remove all roles from the member
    await member.add_roles(role)  # Assign the specified role

    duration = datetime.timedelta(days=4)
    await asyncio.sleep(duration.total_seconds())  # Wait for the specified duration

    # After the duration is over, remove the assigned role
    await member.remove_roles(role)
    await ctx.send(f"Role {role.name} has been removed from {member.display_name}.")



@client.slash_command(name='profile', description='Shows user profile.')
async def profile(inter, member: disnake.Member = None):
    member = member or inter.author

    messages = await inter.channel.history().flatten() if inter.channel.permissions_for(inter.guild.me).read_message_history else []
    messages = [msg for msg in messages if msg.author.id == member.id]

    embed = disnake.Embed(title='Profile', color=0xfcb900)
    embed.set_author(name=member.name, icon_url=member.avatar.url)
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name='Nickname', value=member.display_name, inline=True)
    embed.add_field(name='ID', value=member.id, inline=True)
    embed.add_field(name='Join Date', value=member.joined_at.strftime('%d.%m.%Y %H:%M:%S'), inline=True)
    embed.add_field(name='Account Creation Date', value=member.created_at.strftime('%d.%m.%Y %H:%M:%S'), inline=True)
    embed.add_field(name='Messages', value=str(len(messages)), inline=True)

    level = 0
    levels = {
        1: 10,
        2: 50,
        3: 100,
        4: 200,
        5: 500,
        6: 1000,
        7: 2000,
        8: 3000,
        9: 5000
    }

    for lvl, message_limit in levels.items():
        if len(messages) >= message_limit:
            level = lvl

    embed.add_field(name='Level', value=str(level), inline=True)
    embed.set_footer(text=f'Invoked by: {inter.author}', icon_url=inter.author.avatar.url)

    if inter.channel.id == 1094270574194348192:
        await inter.response.send_message(embed=embed)
    else:
        await inter.author.send(embed=embed)



@client.slash_command(name='warn', description='Issues a warning to the participant')
@commands.has_permissions(kick_members=True)
async def warn_member(ctx, участник: disnake.Member, *, причина=None):
    """Issues a warning to the participant"""

    warnings = {}
    with open("warnings.json", "r") as f:
        warnings = json.load(f)

    if str(участник.id) not in warnings:
        warnings[str(участник.id)] = []
    
    warnings[str(участник.id)].append(причина)
    
    with open("warnings.json", "w") as f:
        json.dump(warnings, f)
    
    embed = disnake.Embed(title=f'{участник} got a warning', color=0xff0000)
    embed.add_field(name='Reason', value=причина or 'Not specified')
    await ctx.send(embed=embed)


@client.slash_command(name='ban', description='Bans a member from the server')
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, участник: disnake.Member, *, причина=None):
    """Bans a member from the server"""
    await участник.ban(reason=причина)
    embed = disnake.Embed(title=f'{участник} banned on the server', color=0xff0000)
    embed.add_field(name='Reason', value=причина or 'not specified')
    await ctx.send(embed=embed)
  
@client.slash_command(name='unban', description='Unbans a member from the server')
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, *, member: str):
    """Unbans a member from the server"""
    bans = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in bans:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = disnake.Embed(title=f'{user} unbanned on the server', color=0x00ff00)
            await ctx.send(embed=embed)
            return
    embed = disnake.Embed(title=f'{member} was not banned from the server', color=0xff0000)
    await ctx.send(embed=embed)


@client.slash_command(name='kick', description='Kick a member from the server')
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, участник: disnake.Member, *, причина=None):
    """Kick a member from the server"""
    if причина == None:
        причина = 'not indicated'
    else:
        причина = причина
    await участник.kick(reason=причина)
    embed = disnake.Embed(title=f'{участник} kicked from the server', color=0xff0000)
    embed.add_field(name='Reason', value=причина or 'not indicated')
    await ctx.send(embed=embed)


@client.slash_command(name='clear', description='Очищает указанное количество сообщений в чате')
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, количество: int):
    """Очищает указанное количество сообщений в чате"""
    try:
        await ctx.response.send_message("Начинаю очистку сообщений...", ephemeral=True)
        await ctx.channel.purge(limit=количество+1)
        embed = disnake.Embed(title=f'Очищено {количество} сообщений в канале {ctx.channel.name}', color=0xff0000)
        await ctx.send(embed=embed, ephemeral=True)
    except disnake.errors.Forbidden:
        await ctx.send("Не достаточно прав на отправку команды!")
      
@client.event
async def on_ready():
    print(f'{client.user} подключился к Discord')
    channel = client.get_channel(1010492537817022514)
    message_id = 1114604075938484274  # Идентификатор существующего сообщения для обновления
    embed = disnake.Embed(title='Заявки на роль Машиниста/помощника! (Для проходки)', description="Если вы заинтересованы в подаче заявки на данную должность, пожалуйста, нажмите на соответствующие кнопки или выберите подходящие варианты из предложенных ниже.", color=disnake.Colour.from_rgb(255, 255, 0))
    
    try:
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed, view=buttons_class())
        print(f"Сообщение с идентификатором {message_id} успешно обновлено")
    except Exception as e:
        print(f"Не удалось обновить сообщение с идентификатором {message_id}: {str(e)}")

    while True:
        members = len(client.guilds[0].members)
        activity = f" to {members} members"
        await client.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=activity))
        await asyncio.sleep(10)


@client.event
async def on_message_edit(before, after):
    if before.author.bot: # не логируем сообщения ботов
        return
    channel = client.get_channel(1105448173054480394) # замените на ID канала, в который должны приходить сообщения
    embed = disnake.Embed(title=f"Изменено сообщение от {before.author.display_name}",
                          description=f"**Отправлено:** {before.content}\n\n**Изменено на:** {after.content}",
                          color=disnake.Color.blue())
    await channel.send(embed=embed)

@client.event
async def on_message_delete(message):
    if message.author.bot: # не логируем сообщения ботов
        return
    channel = client.get_channel(1105448173054480394) # замените на ID канала, в который должны приходить сообщения
    embed = disnake.Embed(title=f"Deleted message from {message.author.display_name}",
                          description=f"**Content:** {message.content}",
                          color=disnake.Color.red())
    await channel.send(embed=embed)

@client.command()
async def команды(ctx):
    """Shows a list of available commands"""
    embed = disnake.Embed(title="Commands", description="list of available commands", color=disnake.Color.yellow())
    await ctx.send(embed=embed)


  
@client.event
async def on_member_join(member):
    role = disnake.utils.get(member.guild.roles, id=1009377875591450707) # получаем объект роли по айди
    await member.add_roles(role) # выдаем роль при заходе на сервер
    channel = client.get_channel(1104058584582594670) # замените на ID канала, в который должно приходить сообщение
    await channel.send(f'<@{member.id}>, joined to TexelRailway')

@client.event #1104058584582594670
async def on_member_remove(member):
    channel = client.get_channel(1104058584582594670) # замените на ID канала, в который должно приходить сообщение
    await channel.send(f"{member.display_name} leave from the TexelRailway!")

keep_alive()
client.run(os.environ['TOKEN'])
