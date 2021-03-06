#! /usr/bin/python

import discord
import asyncio
import inspect
from time import time
from datetime import datetime
import requests

import extensions.Bakalari as Bakalari

SERVER_NAME = "Geneffer"
ANNOUNCEMENT_CHANNEL_NAME = "bot-development"
EMOJI_CHANNEL_NAME = "emoji-requests"

client = discord.Client()

def dump_message_information(message, event_type="on_message"):
    print("Event: {}".format(inspect.stack()[0][3]))
    print("--Message information follows---------")
    print("event_type:                {}".format(event_type))
    print("message.edited_timestamp:  {}".format(message.edited_timestamp))
    print("message.timestamp:         {}".format(message.timestamp))
    print("message.tts:               {}".format(message.tts))
    print("message.author.name:       {}".format(message.author.name))
    print("message.author.nick:       {}".format(message.author.nick))
    print("message.content:           {}".format(message.content))
    print("message.channel.name:      {}".format(message.channel.name))
    print("--End of message information----------")

async def process_command(message):
    command = message.content.split()[0][1:]
    print("Command: {}".format(command))
    await send_response("You issued the command {}".format(command), message.channel, message.author)

async def send_response(message, target, mention=None):
    mention_part = "" if mention == None else "<@{}> ".format(mention.id)
    message_contents = "{}{}".format(mention_part, message)
    await client.send_message(target, message_contents)

@client.event
async def on_ready():
    print("Event: {}".format(inspect.stack()[0][3]))
    print("--Initialization information follows--")
    print("discord.__version__:       {}".format(discord.__version__))
    print("client.user.name:          {}".format(client.user.name))
    print("client.user.id:            {}".format(client.user.id))
    print("client.user.discriminator: {}".format(client.user.discriminator))
    print("client.user.display_name:  {}".format(client.user.display_name))
    print("--End of initialization information---")

@client.event
async def on_message(message):
    print("Event: {}".format(inspect.stack()[0][3]))
    dump_message_information(message)
    content = message.content
    if(not message.content.startswith("!")):
        return
    await process_command(message)


@client.event
async def on_message_delete(message):
    print("Event: {}".format(inspect.stack()[0][3]))
    dump_message_information(message, "on_message_delete")

@client.event
async def on_message_edit(message_before, message_after):
    print("Event: {}".format(inspect.stack()[0][3]))
    dump_message_information(message_before, "on_message_edit->before")
    dump_message_information(message_after, "on_message_edit->after")

@client.event
async def on_reaction_add(reaction, user):
    print("Event: {}".format(inspect.stack()[0][3]))
    dump_message_information(reaction.message, "on_reaction_add->reaction.message")

@client.event
async def on_reaction_remove(reaction, user):
    print("Event: {}".format(inspect.stack()[0][3]))
    dump_message_information(reaction.message, "on_reaction_remove->reaction.message")

@client.event
async def on_reaction_clear(message, reactions):
    print("Event: {}".format(inspect.stack()[0][3]))

@client.event
async def on_channel_delete(channel):
    print("Event: {}".format(inspect.stack()[0][3]))

@client.event
async def on_channel_create(channel):
    print("Event: {}".format(inspect.stack()[0][3]))

@client.event
async def on_channel_update(channel_before, channel_after):
    print("Event: {}".format(inspect.stack()[0][3]))

@client.event
async def on_member_join(member):
    print("Event: {}".format(inspect.stack()[0][3]))

@client.event
async def on_member_remove(member):
    print("Event: {}".format(inspect.stack()[0][3]))

@client.event
async def on_member_update(member_before, member_after):
    print("Event: {}".format(inspect.stack()[0][3]))

async def get_current_server():
    current_server = None
    for server in client.servers:
        if(server.name == SERVER_NAME):
            current_server = server
    if(current_server == None):
        return None
    return current_server

async def get_channel(name):
    current_server = await get_current_server()
    current_channel = None
    for channel in current_server.channels:
        if(channel.name == name):
            current_channel = channel
            break
    if(current_channel == None):
        return None
    return current_channel

async def get_emote(name):
    server = await get_current_server()
    emojis = server.emojis
    emoji = None
    for _emoji in emojis:
        if(_emoji.name == name):
            emoji = _emoji
            break
    if(emoji == None):
        return None
    return "<:{}:{}>".format(emoji.name, emoji.id)

@client.event
async def on_server_emojis_update(emojis_before, emojis_after):
    added = False
    emoji = None
    for curEmoji in emojis_before:
        if(curEmoji not in emojis_after):
            emoji = curEmoji
            break
    for curEmoji in emojis_after:
        if(curEmoji not in emojis_before):
            added = True
            emoji = curEmoji
            break
    if(emoji == None):
        return
    announce_channel = await get_channel(EMOJI_CHANNEL_NAME)

    if(not added or announce_channel == None):
        return

    message_destination = announce_channel
    message_emoji = "<:{}:{}>".format(emoji.name, emoji.id)
    message_content = "{} OwO, what's this? {}".format(message_emoji, message_emoji)

    print("Content: {}".format(message_content))

    await send_response(message_content, message_destination)


async def scheduled_static_name_of_the_day():
    announce_channel = await get_channel(ANNOUNCEMENT_CHANNEL_NAME)

    svatek = requests.get("http://svatky.adresa.info/txt").text.split(";")[1].strip()
    if(svatek == "Petr"):
        svatek = await get_emote("antos")
    await send_response("{} má dnes svátek {}".format(svatek, await get_emote("agrSun")), announce_channel)

async def scheduled_static_rozvrh_zmeny():
    week_info = Bakalari.get_current_week_info()
    changes = Bakalari.get_changes_current_day(week_info)
    announce_channel = await get_channel(ANNOUNCEMENT_CHANNEL_NAME)
    for line in changes:
        await send_response("{}".format(line), announce_channel)

class Time:
    def __init__(self, hour, minute, second=0):
        self.i = (hour - 1) * 3600 + minute * 60 + second
    def __int__(self):
        return self.i

#cas urcujici kdy se spusti, nazev obsluzne async funkce, den posledniho spusteni
scheduled_static = [
    [Time(4, 30), "scheduled_static_name_of_the_day", -1],
    [Time(4, 30), "scheduled_static_rozvrh_zmeny", -1]
]

scheduled_dynamic = [
    
]

async def backgroud_loop():
    await client.wait_until_ready()
    while not client.is_closed:
        current_time = time()
        current_day = datetime.now().day
        for i in range(len(scheduled_static)):
            validation_this_day_seconds = int(current_time % 86400)
            validation_scheduled_seconds = int(scheduled_static[i][0])
            validation_does_current_day_differ = scheduled_static[i][2] != current_day
            validation_scheduled_seconds_end = validation_scheduled_seconds + 300
            eligible = validation_this_day_seconds > validation_scheduled_seconds and validation_does_current_day_differ and validation_this_day_seconds < validation_scheduled_seconds_end
            print("Checking if {} is elegible for execution.. {}".format(scheduled_static[i][1], "Yes" if eligible else "No"))
            if(eligible):
                scheduled_static[i][2] = current_day
                await globals()[scheduled_static[i][1]]()
        await asyncio.sleep(1)

client.loop.create_task(backgroud_loop())

with open('token') as tokenFile:
    token = tokenFile.read().strip()
client.run(token)
