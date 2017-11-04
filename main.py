#! /usr/bin/python

import discord
import asyncio
import inspect

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
    announce_channel = None
    for channel in emoji.server.channels:
        if(channel.name == "emoji-requests"):
            announce_channel = channel
            break

    if(not added):
        return

    message_destination = announce_channel
    message_emoji = "<:{}:{}>".format(emoji.name, emoji.id)
    message_content = "{} OwO, what's this? {}".format(message_emoji, message_emoji)

    print("Content: {}".format(message_content))

    send_response(message_content, message_destination)

async def backgroud_loop():
    await client.wait_until_ready()
    while not client.is_closed:
        announce_server = None
        for server in client.servers:
            if(server.name == "Geneffer"):
                announce_server = server
        if(announce_server == None):
            continue
        announce_channel = None
        for channel in announce_server.channels:
            if(channel.name == "bot-development"):
                announce_channel = channel
                break
        if(announce_channel == None):
            continue
        await send_response("Async FTW", announce_channel)
        await asyncio.sleep(1)

client.loop.create_task(backgroud_loop())

with open('token') as tokenFile:
    token = tokenFile.read().strip()
client.run(token)
