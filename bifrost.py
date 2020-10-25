# bifrost.py
import asyncio
import boto3
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
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
ID_ROLES_TO_BE_ANNOUNCED = list(map(int, os.getenv('ID_ROLES_TO_BE_ANNOUNCED').split(",")))
DEBUG = os.getenv('DEBUG')


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

#findIntroMP3PollyEdition
def findIntroMP3Polly(text):
    return glob.glob(f"{ANNOUNCERMP3PATH}/{text}.mp3")

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

#Sitentizar texto
def pollySynthesize(text):
    filename = text.replace(" ", "_")
    #Chequear si esta sintetización ya existe
    filepath = f'{ANNOUNCERMP3PATH}/{filename}.mp3'
    if os.path.isfile(f'{ANNOUNCERMP3PATH}/{filename}.mp3'):  
        return filepath
    elif os.path.isfile(f'{ANNOUNCERMP3PATH}/{filename}.mp3') is not True:  
        polly_client = boto3.Session(
                        aws_access_key_id=AWS_ACCESS_KEY_ID,                     
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1').client('polly')

        response = polly_client.synthesize_speech(VoiceId='Takumi',
                        OutputFormat='mp3', 
                        Text = text)

        file = open(filepath, 'wb')
        print(f"Generando archivo : {file}")
        file.write(response['AudioStream'].read())
        file.close()
        return filepath
    return None

def getAnnounceableRoles():
    announceable_roles = []
    for guild in client.guilds:
        for role in guild.roles:
            if role.id in ID_ROLES_TO_BE_ANNOUNCED:
                announceable_roles.append(role)
    return announceable_roles

def highestAnnounceableRoleOfUser(member):
    roles_of_member = member.roles
    announceable_roles = getAnnounceableRoles()
    roles_dict = {}
    for role in roles_of_member:
        if role in announceable_roles:
            roles_dict[role] = role.position
    if roles_dict:
        highest_hierachy_role_of_user = max(roles_dict, key=roles_dict.get)    
        return highest_hierachy_role_of_user
    else:
        return None

def createAnnouncementString(member):
    role = highestAnnounceableRoleOfUser(member)
    member_name = member.name
    if role:
        return f"{role} {member_name} has joined"
    else:
        return None


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

# @client.event
# async def on_voice_state_update(member, before, after):
#     if before.channel != after.channel and member != client.user:
#         if after.channel:
#             print(f"User {member.name}[{member.id}] voice connected {after.channel}")
#         mp3 = findIntroMP3(member.id)
#         if mp3:
#             try:            
#                 channel = after.channel
#                 vc = await channel.connect()
#                 vc.play(discord.FFmpegPCMAudio(mp3[0]), after=lambda e: vc.stop())
#                 await asyncio.sleep(4)
#                 vc.stop()
#                 await vc.disconnect()
#                 del vc
#             except Exception as e: 
#                 print(f"An exception has ocurred on {member.name} sound playing: {e}")

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel and member != client.user:
        announcement_string = createAnnouncementString(member)
        if announcement_string:
            filenameWithPath = pollySynthesize(announcement_string)
            if after.channel:
                print(f"User {member.name}[{member.id}] voice connected {after.channel}")
                if pollySynthesize:
                    try:            
                        channel = after.channel
                        vc = await channel.connect()
                        vc.play(discord.FFmpegPCMAudio(filenameWithPath), after=lambda e: vc.stop())
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
        print(f"Labels of img sent by {message.author}: {labels}")
    if 'Anime' in labels:
        print(f"'Anime' label found {message.author}, reacting -> ♍")
        await message.add_reaction('♍')

    if "Hajime" in str(message.author):
        reason = "Juan escribió algo"
        if disgrace(1,15, reason):
            await message.add_reaction('♍')

if DEBUG:
    @client.event
    async def on_message(message):
        #Solo detecta lo que habla en bifrost-text
        if message.channel.id == 752260472388190319:
            print(createAnnouncementString(message))

#LEGAW
clear()
client.run(TOKEN)