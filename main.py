import asyncio
import os
import re
import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.utils import get
import random
from nhattao import *
from datetime import datetime
import server



intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
HEADERS = []
THREADS = []
USERNAMES = []
GUILDID = 1122707918177960047


@client.event
async def on_ready():
    global HEADERS, THREADS, USERNAMES
    try:
        req=requests.get('http://localhost:8888')
        print(req.status_code)
        await client.close() 
        print('Client closed')
        exit()
    except:
        server.b()
        guild = client.get_guild(GUILDID)
        if not ping.is_running():
            ping.start()
        await tree.sync(guild=discord.Object(id=GUILDID))
        for category in guild.categories:
            if 'voz' in category.name:
                for channel in category.channels:
                    if 'threads-content' in channel.name:
                        contents = [msg async for msg in channel.history()]
            elif 'nhattao' in category.name:
                for channel in category.channels:
                    if 'contents' in channel.name:
                        contentsCh = channel
                        threads = channel.threads
                        threads += [thread async for thread in channel.archived_threads()]
        for msg in contents:
            file = False
            content = msg.content
            for att in msg.attachments:
                if 'text' in att.content_type:
                    content = await att.read()
                    content = content.decode('utf-8')
            title = re.search(r'.*Tên sản phẩm:\s(.*?)\..*', content).group(1)
            if title[1:-1] not in str(threads):
                if len(content) > 2000:
                    with open('content.txt', 'w') as file:
                        file.write(content)
                        file = discord.File('content.txt')
                        content = ''
                if file:
                    await contentsCh.create_thread(name=title, content=content, file=file)
                    os.remove('content.txt')
                else:
                    await contentsCh.create_thread(name=title, content=content)


@tasks.loop(seconds=3)
async def ping():
    print(datetime.now())


@tree.command(
    name="update_content",
    description="Update content/ images of product",
    guild=discord.Object(id=GUILDID)
)
async def first_command(interaction):
    await interaction.response.defer()
    msgs = [msg async for msg in interaction.channel.history()]
    hasText = False
    hasImage = False
    notEdit = False
    for i, msg in enumerate(msgs):
        if i == 1 and not msg.author.bot and len(msgs) > 2:
            content = msg.content
            files = []
            temp = []
            for att in msg.attachments:
                if 'text' in att.content_type:
                    content = await att.read()
                    content = content.decode('utf-8')
                    hasText = True
                    with open('content.txt', 'w') as file:
                        file.write(content)
                    files.append(discord.File('content.txt'))
                    temp.append('content.txt')
                    content = ''
                elif 'image' in att.content_type:
                    await att.save(att.filename)
                    files.append(discord.File(att.filename))
                    temp.append(att.filename)
                    hasImage = True
            await msg.delete()
        elif i == len(msgs)-1:
            if 'content' not in locals():
                content = ''
            if 'files' not in locals():
                files = []
            if 'temp' not in locals():
                temp = []
            if len(msgs) == 2 and not msgs[1].author.bot:
                notEdit = True
            if not hasText and len(content.strip()) == 0:
                content = msg.content
                for att in msg.attachments:
                    if 'text' in att.content_type:
                        content = await att.read()
                        content = content.decode('utf-8')
                        with open('content.txt', 'w') as file:
                            file.write(content)
                        files.append(discord.File('content.txt'))
                        temp.append('content.txt')
                        hasText = True
            if not hasImage:
                for att in msg.attachments:
                    if 'image' in att.content_type:
                        await att.save(att.filename)
                        files.append(discord.File(att.filename))
                        temp.append(att.filename)
            if notEdit:
                name = re.search(
                    r'.*Tên sản phẩm: (.*?)\..*', content).group(1)
                name = name.strip()[0:99]
                if hasText:
                    content = ''
                thread = await interaction.channel.parent.create_thread(name=name, content=content, files=files)
                await thread.thread.send('Need update!')
                await interaction.channel.delete()
            else:
                if hasText:
                    content = ''
                await msg.edit(content=content, attachments=files)
            for file in temp:
                if os.path.isfile(file):
                    os.remove(file)
        elif i != 0 and i != len(msgs)-1 and msg.author.bot and not notEdit:
            await msg.delete()
    if not notEdit:
        await interaction.edit_original_response(content='Need update!')
client.run(os.environ.get('botToken'))
