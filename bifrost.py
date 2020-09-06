# bifrost.py
import asyncio
import ctypes
import ctypes.util
import datetime
import discord
import ffmpeg
import glob
import json
import logging
import random
import os
from datetime import timedelta
from dotenv import load_dotenv
from google.cloud import vision
from os import system, name

#/-----INITIALIZATION-----\
#.env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
ANNOUNCERMP3PATH = os.getenv('ANNOUNCER_MP3_PATH')

#discord client
client = discord.Client()

#load opus lib
a = ctypes.util.find_library('opus')
b = discord.opus.load_opus(a)
c = discord.opus.is_loaded()
if not(discord.opus.is_loaded()):
    print(f'Discord Opus error')

#google computervision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="client_secrets.json"
gcv_client = vision.ImageAnnotatorClient()

# import io
# path = 'Image.jpeg'
# print(path)
# with io.open(path, 'rb') as image_file:
#         content = image_file.read()
# image = vision.types.Image(content=content)
# response = gcv_client.image_properties(image=image)
# props = response.image_properties_annotation
# print(response)

#/-----Functions-----\

#clear
def clear():   
    if name == 'nt': 
        _ = system('cls') 
    else: 
        _ = system('clear')

#findIntroMP3
def findIntroMP3(userid):
    return glob.glob(f"{ANNOUNCERMP3PATH}/{str(userid)}_*.mp3")

#disgrace
def disgrace(target, dicesize, reason=None):
    number = random.randrange(1, dicesize)
    if reason == None:
        reason = "no especificada"
    print(f"Rolling for disgrace: rolled:{number} target: {target} dicesize:{dicesize} | Razón: {reason}")
    if number == target:
        return True
    else:
        return False


#/-----Events-----\

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            print(f'{client.user} connected to [{guild.name}][{guild.id}] ')
            break

#Guachin sacá ya el me divierte
#Acá primero tuve que conseguir la payload del evento de agregar emoji
#Luego el canal usando client.get_channel pasándole el id del canal sacado de la payload
#Para el msg lo mismo, pero usando el fetch_message con el id de la payload
@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "medivierte":
        myid = (f'<@{payload.user_id}>') 
        channel = client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        reactions = msg.reactions
        for reaction in reactions:
            if type(getattr(reaction,'emoji')) == discord.emoji.Emoji:
                # if str(reaction.emoji) == '<:medivierte:747548032626720889>':
                if ':medivierte:' in str(reaction.emoji):
                    if disgrace(17, 20):
                        await channel.send(f"{myid} guachin saca ya el me divierte https://www.youtube.com/watch?v=frZsl8nQPOo")
                        await asyncio.sleep(600)

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel and member != client.user:
        if after.channel:
            print(f"User {member.name}[{member.id}] voice connected {after.channel}")
        mp3 = findIntroMP3(member.id)
        if mp3:
            try:            
                channel = after.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(mp3[0]), after=lambda e: vc.stop())
                await asyncio.sleep(4)
                vc.stop()
                await vc.disconnect()
                del vc
            except Exception as e: 
                print(f"An exception has ocurred on {member.name} sound playing: {e}")

@client.event
async def on_member_join(member):
    print(f"{member.name} has joined the server")
    await member.create_dm()
    await member.dm_channel.send(
        f'Bienvenido a ToposCrew, {member.name}.'
    )

@client.event
async def on_message(message):
    labels = []
    if message.author == client.user:
        return
    if message.attachments:        
        for attachment in message.attachments:
            if attachment.url.endswith('jpg') or attachment.url.endswith('jpeg') or attachment.url.endswith('png'):
                response = gcv_client.annotate_image({
                'image': {'source': {'image_uri': f'{str(attachment.url)}'}},
                'features': [{'type': vision.enums.Feature.Type.LABEL_DETECTION}],
                })
        for annotation in response.label_annotations:
            labels.append(annotation.description)
            print(f"Etiquetas de la imagen enviada por {message.author}: {labels}")
    if 'Anime' in labels:
        print(f"Imagen otaku detectada enviada por {message.author}, reaccionando con ♍")
        await message.add_reaction('♍')

    if "Hajime" in str(message.author):
        reason = "Juan escribió algo"
        if disgrace(1,5, reason):
            await message.add_reaction('♍')

#LEGAW
clear()
client.run(TOKEN)


