# bifrost.py
import os
import discord
import random
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print('Logueado: {0.user}'.format(client))

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
                if str(reaction.emoji) == '<:medivierte:747548032626720889>':
                    if random.randrange(1, 20) == 17:
                        await channel.send(f"{myid} guachin saca ya el me divierte https://www.youtube.com/watch?v=frZsl8nQPOo")
                            asyncio.sleep(600)

client.run(TOKEN)
