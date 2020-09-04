# bifrost.py
import asyncio
import ctypes
import ctypes.util
import datetime
from datetime import timedelta
import discord
import ffmpeg
import glob
import logging
import random
import os

from dotenv import load_dotenv

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()



def findIntroMP3(userid):
    soundspath = "./mp3"
    mp3files = glob.glob(f"{soundspath}/{str(userid)}_*.mp3")
    return mp3files

    



@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            print('CONECTADO A TOPOSCREW')
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )


    #Loading OPUS---
    # print("ctypes - Find opus:")
    a = ctypes.util.find_library('opus')
    # print(a)
    
    # print("Discord - Load Opus:")
    b = discord.opus.load_opus(a)
    # print(b)
    
    # print("Discord - Is loaded:")
    c = discord.opus.is_loaded()
    # print(c)

    print(f'Is Opus library loaded?: {discord.opus.is_loaded()}')
    

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
                    randomMedivierte = random.randrange(1, 20)
                    print(f"Rolling for disgrace 'medivierte' target 17 ({randomMedivierte})")
                    if randomMedivierte == 17:
                        await channel.send(f"{myid} guachin saca ya el me divierte https://www.youtube.com/watch?v=frZsl8nQPOo")
                        await asyncio.sleep(600)


@client.event
async def on_voice_state_update(member, before, after):
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    #for miembro in guild.members:
    #   for role in miembro.roles: 
    #       if role.name == "Inspector":
    #           inspector.append(miembro)
    
    # rolesMiembro = [member for miembro in guild.members for role in miembro.roles if role.name == "Inspector"]



    if before.channel != after.channel and member != client.user:
        print(f"Entro el {member.name} id: {member.id} a {after.channel}")
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
client.run(TOKEN)


