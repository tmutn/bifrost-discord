# bifrost.py
import asyncio
import boto3
import ctypes
import ctypes.util
import datetime
import discord
import ffmpeg
import glob
import inspect
import json
import random
import os
import sqlite3
from datetime import timedelta
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv
from sqlite3 import Error
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

#HARDCODED CANTIDAD DE VOTOS POR PERSONA
VOTES_PER_ELECTOR_ROLE = 2

#discord
intents = discord.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
discordBot = commands.Bot(command_prefix='>', intents=intents)

#load opus lib
a = ctypes.util.find_library('opus')
b = discord.opus.load_opus(a)
c = discord.opus.is_loaded()
if not(discord.opus.is_loaded()):
	print(f'Discord Opus error')

#google computervision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="client_secrets.json"
gcv_client = vision.ImageAnnotatorClient()

#/-----FUNCTIONS-----\
#clear
def clear():   
	if name == 'nt': 
		_ = system('cls') 
	else: 
		_ = system('clear')

#getArity
def getArity(func):
	return inspect.getfullargspec(func)

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

#executeSqlite
def executeSqlite(script):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(script)
		condb.commit()
	except Error as err:
		print(err)
	finally:
		condb.close()

#FUNCIONES BIFROST-POLLY
#Sitentizar texto
def pollySynthesize(text, voiceId='Takumi', engine='standard', textType ='text', forceName = False):
	filename = text.replace(" ", "_")
	polly_client = boto3.Session(
					aws_access_key_id=AWS_ACCESS_KEY_ID,                     
		aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
		region_name='us-east-1').client('polly')


	if voiceId == 'Matthew':
		engine = 'neural'

	response = polly_client.synthesize_speech(Engine = engine,
					VoiceId=voiceId,
					OutputFormat='mp3', 
					Text = text,
					TextType = textType)


	#Chequear si esta sintetización ya existe
	filepath = f'{ANNOUNCERMP3PATH}/{filename}-voiceID={voiceId}.mp3'
	if forceName:
		filepath = f'{ANNOUNCERMP3PATH}/{forceName}.mp3'

	if os.path.isfile(f'{ANNOUNCERMP3PATH}/{filename}.mp3') and not forceName:  
		return filepath
		
	elif os.path.isfile(f'{ANNOUNCERMP3PATH}/{filename}.mp3') is not True:  
		file = open(filepath, 'wb')
		print(f"Generando archivo : {file}")
		file.write(response['AudioStream'].read())
		file.close()

		return filepath
	return None

def getAnnounceableRoles():
	announceable_roles = []
	for guild in discordBot.guilds:
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

def isAdministrator(member):
	if member.guild_permissions.administrator:
		return True
	else:
		return False

async def disconnectVoiceObject(vc):
	try:            
		await vc.disconnect()
	except Exception as e: 
		print(f"An exception has ocurred on elections end sound playing: {e}")

async def dmEveryone(ctx, message):
	for member in ctx.guild.members:
		if member != discordBot.user:
			await member.send(message)
		



#FUNCIONES AUXILIARES BIFROST-DEMOCRATIA
#Obtener el objeto member al recibir como parámetro un @alguien y el contexto
def	getPingedMember(ctx, pingedMember):
	charactersToRemove = "<>@!&"
	idPingedMember = pingedMember
	for character in charactersToRemove:
		idPingedMember = idPingedMember.replace(character, '')
	try:
		idPingedMember = int(idPingedMember)
	except:
		print("String is not transferible to int")
		return None	
	for member in ctx.guild.members:
		if member.id ==  idPingedMember:
			return member
	return None

#Obtener el objeto member al recibir como parámetro un @alguien y el contexto
def	getPingedRole(ctx, pingedRole):
	charactersToRemove = "<>@!&"
	idPingedRole = pingedRole
	for character in charactersToRemove:
		idPingedRole = idPingedRole.replace(character, '')
	try:
		idPingedRole = int(idPingedRole)
	except:
		print("String is not transferible to int")
		return None	
	for role in ctx.guild.roles:
		if role.id ==  idPingedRole:
			return role
	return None

async def sendDM(member, content):
	await member.send(content)


#HARDCODED O LAS ELECCIONES NO SE HACEN NUNCA
async def displayLists(channel):
	congressmenId = getAllElectableCongressmanIds(channel)
	electableOptionsList = []
	for congressmanId in congressmenId:
		electionRoles = getElectionRoles(channel)
		ecd = getElectableCongressmanData(congressmanId, channel)
		lmd = getListMembersData(congressmanId)
		inspectorNames = []
		inspectorNamesString = ''
		colorHexString = str(ecd['list_color'])
		try:
			color = int(colorHexString, base=16)
		except ValueError as err:
			color = int('0xFFFFFF', base=16)
		embed = discord.Embed(title=f"{ecd['list_name']}", description=f"Lista {ecd['list_id']}", color=discord.Color(color))
		embed.add_field(name=f"Congressman", value=f"{channel.guild.get_member(ecd['member_id']).name}")
		if lmd:
			for listMember in lmd:
				if listMember['role_name'] == "First Inspector":
					#HARDCODED SE ASUME UN SOLO INSPECTOR
					member_id = listMember['candidate_member_id']
					embed.add_field(name=f"First Inspector", value=f"{channel.guild.get_member(member_id).name}")
				if listMember['role_name'] == "Inspector":
					inspectorNames.append(channel.guild.get_member(listMember['candidate_member_id']).name)	
			if inspectorNames:	
				for inspectorName in inspectorNames:
					inspectorNamesString += inspectorName + '\n'
				embed.add_field(name=f"Inspectors", value=f"{inspectorNamesString}")
		if ecd['list_image']:
			urlImagen = ecd['list_image']
		else:
			urlImagen = 'https://i.imgur.com/mFpWgS1.jpg'
		try:	
			embed.set_image(url=urlImagen)
			embed.set_footer(text=f"{ecd['member_id']}")
			await channel.send(embed=embed)
		except discord.HTTPException as err:
			print(err)
	#HARDCORDED el amount de votos en el string



#TEXT FUNCTIONS BIFROST-DEMOCRATIOA
def electionInformation(ctx):
	electionRoles = getElectionRoles(ctx)
	congressman = electionRoles[0]
	firstInspector = electionRoles[1]
	inspector = electionRoles[2] 
	topo = electionRoles[3]
	message = f"""
En esta elección, todos los que tengan el rango **{topo['role_name']}** podrán postularse para ser uno de los 3 **{congressman['role_name']}** del servidor

Cada **{congressman['role_name']}** que se postule deberá crear una lista con {inspector['amount_per_congressman']} **{inspector['role_name']}**.

Opcionalmente, podrá incluir {firstInspector['amount_per_congressman']} **{firstInspector['role_name']}** en su lista. Este rol es único en el servidor
Será designado como {firstInspector['role_name']} el que pertenezca a la lista del **{congressman['role_name']}** con más votos

Empates y la ausencia de postulantes a **{firstInspector['role_name']}** será resuelta por Bifrost
```arm\n              _
			 / \\
			/   \\
		   /     \\
		  /       \\
		 / BIFROST \\
		/           \\
	   / CONGRESSMAN \\     ►3
	  /               \\
	 / FIRST INSPECTOR \\   ►1
	/                   \\
   /      INSPECTORS     \\ ►6
  /                       \\
 /          TOPOS          \\
/___________________________\\	

```

**FASES DE LA ELECCIÓN**:

**1 - FASE DE LISTAS**
Todos los que tengan rango **{topo['role_name']}** pueden postularse a **{congressman['role_name']}** utilizando el comando >postularme [Numero de Lista] [Nombre de Lista]
 
Ejemplo: ```>postularme 10 Frente de Discord``` 
Una vez postulado, el candidato a **{congressman['role_name']}** tendrá un espacio de campaña asignado donde podrá invitar a miembros con el rango **{topo['role_name']}** a participar de su lista

Los postulantes podrán encontrar los requerimientos e información adicional en su espacio asignado

**Las listas que no cumplan los requerimientos no pasarán a la próxima fase**


**2 - FASE DE VOTACIÓN**
En esta fase, todos los que tengan el rango **{topo['role_name']}** podrán votar, tendrán {VOTES_PER_ELECTOR_ROLE} votos que deberán distribuir entre los candidatos disponibles

Para votar deben utilizar el siguiente comando:

```>quieroVotar```

Al escribir ese comando, tendrás un espacio en la categoría ╠════ CUARTO OSCURO ════╣

En el cuarto oscuro podrán encontrar información de como votar y las listas disponibles


**3 - FASE DE ESCRUTINIO**
Cuando se active el escritinio, Bifrost hará una ceremonia en un canal de voz designado donde se anunciará a los ganadores
"""
	return message


#QUERYs BIFROST-DEMOCRATIA
def getGuildElectablesCategory(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT category_electables_id FROM election WHERE election_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		category_id = rows[0][0]
		category =  discordBot.get_channel(category_id)
		return category
	else:
		return None

def getCandidateCampaignChannel(memberId):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT text_channel_id FROM electable_congressman WHERE member_id = {memberId}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		channelId = rows[0][0]
		campaignChannel =  discordBot.get_channel(channelId)
		return campaignChannel
	else:
		return None

def isThisACampaignChannel(ctx):
	rows = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT text_channel_id FROM electable_congressman WHERE text_channel_id = {ctx.channel.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		category_id = rows[0][0]
		category =  discordBot.get_channel(category_id)
		return category
	else:
		return None

#TOPO CHECK
def memberCastsVote(ctx, member_id):
	member = ctx.guild.get_member(member_id)
	voterRole = getCastVoteRole(ctx)
	for role in member.roles:
		if voterRole == role:
			return True
	return False
def getCastVoteRole(ctx):
	rows = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT role_id FROM election_role WHERE election_id = {ctx.guild.id} AND casts_vote = 1")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		return ctx.guild.get_role(rows[0][0])
	else:
		return None
	



def getElectableCongressmanData(member_id, ctx):
	rows = []
	result = []
	data = {}

	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()

		cursorObj.execute(f"SELECT * FROM electable_congressman WHERE member_id = {member_id} and guild_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	
	if rows:
		for row in rows:
			result = row
		data = {
			'member_id' : result[0],
			'discord_username' : result[1],
			'text_channel_id' : result[2],
			'guild_id' : result[3],
			'list_id' : result[4],
			'list_name' : result[5],
			'list_image' : result[6],
			'list_color' : result[7],
			'date_joined' : result[8]
		}
		return data
	else:
		return None

#CONTINUE podría mergearse con la de getElectableCongressmanData utilizando parámetros opcionales
def getAllElectableCongressmanIds(ctx):
	rows = []
	result = []
	dataArray = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT member_id FROM electable_congressman WHERE guild_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	
	if rows:
		for row in rows:
			result = row
			dataArray.append(result[0])
		return dataArray
	else:
		return None

def getListMembersData(electable_congressman_id):
	rows = []
	result = []
	data = {}
	dataArray = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT cc.candidate_member_id, cc.candidate_postulated_role_id, er.role_name FROM confirmed_candidate as cc INNER JOIN election_role as er ON cc.candidate_postulated_role_id = er.role_id WHERE cc.congressman_id = {electable_congressman_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	
	if rows:
		for row in rows:
			result = row
			data = {
				'candidate_member_id' : result[0],
				'candidate_postulated_role_id' : result[1],
				'role_name' : result[2]
			}
			dataArray.append(data)
		return dataArray
	else:
		return None

#CONTINUE
def getConfirmedCandidateInspectorData(congressman_id, role_id):
	rows = []
	result = []
	data = {}
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT * FROM electable_congressman WHERE member_id = {member_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()	
	if rows:
		for row in rows:
			result = row
		data = {
			'member_id' : result[0],
			'discord_username' : result[1],
			'text_channel_id' : result[2],
			'guild_id' : result[3],
			'list_id' : result[4],
			'list_name' : result[5],
			'list_image' : result[6],
			'date_joined' : result[7]
		}
		return data
	else:
		return None

#Returns three values to populate table confirmed_candidate
def hasOfferInThisList(ctx):
	rows = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT postulated_member_id, role_id, postulator_member_id FROM pending_postulation_offer WHERE postulated_member_id = {ctx.author.id} AND confirmation_channel = {ctx.channel.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	result = []
	if rows:
		for row in rows:
			result = row
		return tuple(result)
	else:
		return None

def getGuildBoothsCategory(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT category_booths_id from election WHERE election_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		category_id = rows[0][0]
		category =  discordBot.get_channel(category_id)
		return category
	else:
		return None

def isVoterInsideHisBooth(member_id, channel_id, guild_id):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		values = (member_id, channel_id, guild_id)
		cursorObj.execute(f"SELECT * FROM voter WHERE member_id = ? AND voting_private_channel_id = ? AND guild_id = ?", values)
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		return rows[0][0]
	else:
		return None


async def postulateCongressman(ctx, channel, listId, listName):
	error = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		author_name = str(ctx.author)
		values = (ctx.author.id, author_name, channel.id, ctx.guild.id, listId, listName, '', 'FFFFFF')
		cursorObj.execute("INSERT INTO electable_congressman(member_id, discord_username, text_channel_id, guild_id, list_id, list_name, list_image, list_color, date_joined) VALUES(?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", values)
		condb.commit()
	except Error as err:
		error = err
		print(err)
		await channel.delete()
		await ctx.author.send("Ese número o nombre de la lista ya está tomado")		
		error = True
		return False
	finally:
		condb.close()
		if not error:
			return True

def registerVoter(ctx, channel):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		values = (ctx.author.id, channel.id, ctx.guild.id)
		cursorObj.execute(f"INSERT INTO voter VALUES(?,?,?)", values)
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()

async def addPostulationOffer(ctx, postulator_member_id, postulated_member_id, confirmation_channel, role_id):
	error = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		values = (postulator_member_id, postulated_member_id, confirmation_channel, role_id)
		cursorObj.execute(f"INSERT INTO pending_postulation_offer VALUES(?,?,?,?)", values)
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		error = err
		await ctx.author.send("Ya le enviaste una oferta a este miembro")
		print(err)
		return False
	finally:
		condb.close()
		if not error:
			return True

def addConfirmedCandidate(values):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"INSERT INTO confirmed_candidate VALUES(?,?,?)", values)
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()

def countRolePostulationsInList(electable_congressman_id, role_id):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT count({role_id}) from confirmed_candidate as cc WHERE cc.congressman_id = {electable_congressman_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None

def getMaxPostulationsPerRole(role_id, election_id):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT amount_per_congressman FROM election_role WHERE role_id = {role_id} and election_id = {election_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None


def areListRequirementsOk(electable_congressman_id, election_id):
	rows = None
	data = {}
	dataMandatoryElectionRoles = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT * FROM election_role WHERE is_mandatory = 1 and election_id = {election_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		for row in rows:
			data = {
				'role_id' : row[0],
				'election_id' : row[1],
				'role_name' : row[2],
				'amount_per_congressman' : row[3],
				'is_mandatory' : row[4],
				'casts_vote' : row[5]
			}
		dataMandatoryElectionRoles.append(data)
	else:
		return None
	for mandatoryRole in dataMandatoryElectionRoles:
		try:
			condb = sqlite3.connect('bifrost.db')
			cursorObj = condb.cursor()
			cursorObj.execute(f"SELECT COUNT(candidate_member_id) FROM confirmed_candidate WHERE congressman_id = {electable_congressman_id} AND candidate_postulated_role_id = {mandatoryRole['role_id']}")
			condb.commit()
			rows = cursorObj.fetchall()
		except Error as err:
			print(err)
		finally:
			condb.close()
		if rows:
			amountOfRoleInList = rows[0][0]
			if amountOfRoleInList < mandatoryRole['amount_per_congressman']:
				return False
	return True



def isRoleMandatory(role_id, election_id):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT is_mandatory FROM election_role WHERE role_id = {role_id} and election_id = {election_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None


def isMemberElectableCongressman(member_id):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT member_id from electable_congressman WHERE member_id = {member_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None

def isMemberOwnerOfElectionChannel(ctx):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT member_id from electable_congressman WHERE member_id = {ctx.author.id} AND text_channel_id = {ctx.channel.id} ")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		return True
	else:
		return None

def isOnAListAlready(member_id):
	rows = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT candidate_member_id FROM confirmed_candidate WHERE candidate_member_id = {member_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None

def isVoterAlready(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT member_id from voter WHERE member_id = {ctx.author.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None

def areElectionsRunning(guild_id):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT election_id from election WHERE election_id = {guild_id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None

# def getElectables(ctx):
# 	try:
# 		condb = sqlite3.connect('bifrost.db')
# 		cursorObj = condb.cursor()
# 		cursorObj.execute(f"SELECT member_id from electable_congressman WHERE guild_id = {ctx.guild.id}")
# 		condb.commit()
# 		rows = cursorObj.fetchall()
# 	except Error as err:
# 		print(err)
# 	finally:
# 		condb.close()
# 	if rows:
# 		i = 0
# 		candidatos = {}
# 		for row in rows:
# 			member_id = row[0]
# 			member = ctx.guild.get_member(member_id)
# 			candidatos[i] = member
# 			i+=1
# 		return candidatos
# 	else:
# 		return None

def getElectionRoles(ctx):
	rows = []
	electionRoles = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT * from election_role WHERE election_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		for row in rows:
			electionRoles.append(row)
	else:
		return None
	#HARDCODED
	congressman = {}
	firstInspector = {}
	inspector = {}		
	topo = {}
	for role in electionRoles:
		if "Congressman" in role:
			congressman = {
				"role_id" : role[0],
				"election_role_id" : role[1],
				"role_name" : role[2],
				"amount_per_congressman" : role[3],
				"is_mandatory" : role[4],
				"casts_vote" : role[5]
			}
		if "First Inspector" in role:
			firstInspector = {
				"role_id" : role[0],
				"election_role_id" : role[1],
				"role_name" : role[2],
				"amount_per_congressman" : role[3],
				"is_mandatory" : role[4],
				"casts_vote" : role[5]
			}
		if "Inspector" in role:
			inspector = {
				"role_id" : role[0],
				"election_role_id" : role[1],
				"role_name" : role[2],
				"amount_per_congressman" : role[3],
				"is_mandatory" : role[4],
				"casts_vote" : role[5]
			}
		if "Topo" in role:
			topo = {
				"role_id" : role[0],
				"election_role_id" : role[1],
				"role_name" : role[2],
				"amount_per_congressman" : role[3],
				"is_mandatory" : role[4],
				"casts_vote" : role[5]
			}
	result = []
	result.append(congressman)
	result.append(firstInspector)
	result.append(inspector)
	result.append(topo)
	return result


#CONTINUE
async def endPostulations(ctx):
	rows = None
	data = {}
	purgeData = []
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"UPDATE election SET postulation_phase = 0 WHERE election_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT member_id, text_channel_id FROM electable_congressman WHERE guild_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
		if rows:
			for row in rows:
				data = {
					'member_id' : row[0],
					'channel_id' : row[1]
				}
			purgeData.append(data)
		print(purgeData)
	except Error as err:
		print(err)
	finally:
		condb.close()
	for lista in purgeData:
		if areListRequirementsOk(lista['member_id'], ctx.guild.id):
			pass
		else:
			scripts = [f"DELETE from pending_postulation_offer WHERE postulator_member_id = {lista['member_id']}",f"DELETE from confirmed_candidate WHERE congressman_id = {lista['member_id']}",f"DELETE from electable_congressman WHERE member_id = {lista['member_id']}"]
			for script in scripts:
				executeSqlite(script)
				channelToDelete = discordBot.get_channel(lista['channel_id'])
			await channelToDelete.delete()


def arePostulationsRunning(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT postulation_phase from election WHERE election_id = {ctx.guild.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None

def alreadyBelongsToList(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT * from confirmed_candidate WHERE candidate_member_id = {ctx.author.id}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
		return result
	else:
		return None


#ESTO TAMBIÉN VERIFICA QUE NO TE PASES CON LOS VOTOS ANTES DE AGREGARLO A LA BASE DE DATOS
async def addVote(payload, voterId, congressmanId):
	currentChannel = discordBot.get_channel(payload.channel_id)

	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT COUNT(*) FROM voter_votes_electable WHERE member_id  = {voterId}")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		result = rows[0][0]
	else:
		result = 0

	if result >= VOTES_PER_ELECTOR_ROLE:
		await payload.member.send("Ya no te quedan votos, gracias por participar en las elecciones")
		return

	error = None
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		values = (voterId, congressmanId)
		cursorObj.execute("INSERT INTO voter_votes_electable VALUES(?,?)", values)
		condb.commit()
	except Error as err:
		error = err
		print(err)
		
		await currentChannel.send("Ya votaste a este candidato")		
		error = True
		return False
	finally:
		condb.close()
		if not error:
			return result + 1

def countVotesAndSort(ctx):
	dictResult = {
		'congressman_id' : 0,
		'votes' : 0,
		'list_id' : 0,
		'list_name' : ''
	}
	result = []


	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute("SELECT vve.electable_id, COUNT(vve.electable_id), ec.list_id , ec.list_name FROM voter_votes_electable vve INNER JOIN electable_congressman as ec on vve.electable_id = ec.member_id  GROUP BY electable_id ORDER BY COUNT(vve.electable_id) DESC LIMIT 3")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		for row in rows:
			result.append(
				{
				'congressman_id' : row[0],
				'votes' : row[1],
				'list_id' : row[2],
				'list_name' : row[3]
				}
			)
		return result
	else:
		result = 0




#/-----Events-----\
@discordBot.event
async def on_ready():
	print(f"{discordBot.user} is connected to the following guilds:")
	for guild in discordBot.guilds:
		print(
			f'{guild.name}(id: {guild.id})'
		)


#Guachin sacá ya el me divierte
#Acá primero tuve que conseguir la payload del evento de agregar emoji
#Luego el canal usando discordBot.get_channel pasándole el id del canal sacado de la payload
#Para el msg lo mismo, pero usando el fetch_message con el id de la payload
@discordBot.event
async def on_raw_reaction_add(payload):
	if payload.emoji.name == "medivierte":
		myid = (f'<@{payload.user_id}>') 
		channel = discordBot.get_channel(payload.channel_id)
		msg = await channel.fetch_message(payload.message_id)
		reactions = msg.reactions
		for reaction in reactions:
			if type(getattr(reaction,'emoji')) == discord.emoji.Emoji:
				# if str(reaction.emoji) == '<:medivierte:747548032626720889>':
				if ':medivierte:' in str(reaction.emoji):
					if disgrace(17, 20):
						await channel.send(f"{myid} guachin saca ya el me divierte https://www.youtube.com/watch?v=frZsl8nQPOo")
						await asyncio.sleep(600)

# @discordBot.event
# async def on_voice_state_update(member, before, after):
#     if before.channel != after.channel and member != discordBot.user:
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

@discordBot.event
async def on_voice_state_update(member, before, after):
	if before.channel != after.channel and member != discordBot.user:
		announcement_string = createAnnouncementString(member)
		if announcement_string:
			filenameWithPath = pollySynthesize(announcement_string)
			if after.channel:
				print(f"User {member.name}[{member.id}] voice connected {after.channel}")
				if filenameWithPath:
					try:            
						channel = after.channel
						vc = await channel.connect()
						vc.play(discord.FFmpegPCMAudio(filenameWithPath), after=lambda e: vc.stop())
						while vc.is_playing():
							await asyncio.sleep(.1)
						await vc.disconnect()
						del vc
					except Exception as e: 
						print(f"An exception has ocurred on {member.name} sound playing: {e}")

@discordBot.event
async def on_member_join(member):
	print(f"{member.name} has joined the server")
	await member.create_dm()
	await member.dm_channel.send(
		f'Bienvenido a ToposCrew, {member.name}.'
	)

#React to images using Google Computervision
@discordBot.event
async def on_message(message):
	labels = []
	if message.author == discordBot.user:
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
	await discordBot.process_commands(message)

#Per user reactions
@discordBot.event
async def on_message(message):
	if "Hajime" in str(message.author):
		reason = "Juan escribió algo"
		if disgrace(1,15, reason):
			await message.add_reaction('♍')
	await discordBot.process_commands(message)

@discordBot.command(name="elecciones", hidden=True)
async def startElections(ctx, arrobaCongressman, arrobaFirstInspector, arrobaInspector, arrobaTopo):
	if isAdministrator(ctx.message.author):
		if areElectionsRunning(ctx.guild.id):
			await sendDM(ctx.author, f"Ya una elección en curso")
			return
		else:
			categoryElectables = await ctx.guild.create_category(name='╠═ELECCIONES CONGRESSMAN═╣')
			categoryBooths = await ctx.guild.create_category(name='╠════ CUARTO OSCURO ════╣')
		#CREAR RECORD DE ELECCIONES
		try:
			condb = sqlite3.connect('bifrost.db')
			cursorObj = condb.cursor()
			insert_election = (ctx.guild.id, categoryElectables.id, categoryBooths.id)
			cursorObj.execute("INSERT INTO election VALUES(?,CURRENT_TIMESTAMP,1,?,?,1)", insert_election)
			condb.commit()
		except Error as err:
			print(err)
		finally:
			condb.close()

		#HARDCODED, CANTIDAD DE COSOS POR CONGRESSMAN Y OBLIGATORIEDAD
		#role = (amount , Is Mandatory)
		# inspector_per_congressman = [2,'True']
		# firstInspector_per_congressman = [1,'False']
		#CREAR RECORD DE IDS PARA CONGRESSMAN FIRST E INSPECTOR ASOCIADOS FK A TABLA ELECCIONES
		congressman = getPingedRole(ctx, arrobaCongressman)
		firstInspector = getPingedRole(ctx, arrobaFirstInspector)
		inspector = getPingedRole(ctx, arrobaInspector)
		topo = getPingedRole(ctx, arrobaTopo)
		insert_election_role = []
		insert_election_role.append((congressman.id, ctx.guild.id,congressman.name, 0, False, False))
		insert_election_role.append((firstInspector.id, ctx.guild.id,firstInspector.name, 1, False, False))
		insert_election_role.append((inspector.id, ctx.guild.id,inspector.name, 2, True, False))
		insert_election_role.append((topo.id, ctx.guild.id,topo.name, 0, False, True))

		for tupla in insert_election_role:
			try:
				condb = sqlite3.connect('bifrost.db')
				cursorObj = condb.cursor()
				cursorObj.execute("INSERT INTO election_role VALUES(?,?,?,?,?,?)", tupla)
				condb.commit()
			except Error as err:
				print(err)
			finally:
				condb.close()

		dmEveryone(ctx,electionInformation(ctx))
	else:
		print(f"{ctx.message.author} is NOT ADMINISTRATOR. Warning issued.")


@discordBot.command(name="cerrarListas", hidden=True)
async def endPostulationsCommand(ctx):
	if isAdministrator(ctx.message.author):
		await endPostulations(ctx)
	else:
		print(f"{ctx.message.author} is NOT ADMINISTRATOR. Warning issued.")

@discordBot.command(name="postularme", brief='Postularse a Congressman')
async def becomeElectable(ctx, listId, *listName):
	if not areElectionsRunning(ctx.guild.id):
		await sendDM(ctx.author, f"No hay una elección en curso")
		return
	if not memberCastsVote(ctx, ctx.author.id):
		await sendDM(ctx.author, f"Tu rango no es suficiente para postularte")
		return
	if not arePostulationsRunning(ctx):	
		await sendDM(ctx.author, f"Las listas ya están cerradas, mejor suerte para la próxima")
		return
	if isMemberElectableCongressman(ctx.author.id):
		await sendDM(ctx.author, f"Ya estás postulado")
		return
	if alreadyBelongsToList(ctx):
		await sendDM(ctx.author, f"No podés postularte a Congressman, ya confirmaste tu puesto en una lista")
		return
	nombreDeLista = ''
	if listName:
		for palabra in listName:
			nombreDeLista+=' '+palabra
	nombreDeLista = nombreDeLista.strip()
	campaignChannelCategory = getGuildElectablesCategory(ctx)
	#Continue
	try:
		listId = int(listId)
		if listId > 999:
			await ctx.author.send("El número ingresado debe ser de tres dígitos.")		
			return
	except:
		await ctx.author.send("El número ingresado es inválido.")		
		return
	if campaignChannelCategory:
		overwrites = {
			ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
			ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
		}	
		channel = await ctx.guild.create_text_channel(name=f'{ctx.author}', category=campaignChannelCategory, overwrites=overwrites)	
		if not nombreDeLista:
			nombreDeLista = f"La lista de {ctx.author.name}"
		if not await postulateCongressman(ctx, channel, listId, nombreDeLista):		
			return
		await sendDM(ctx.author, f"Te has postulado para el cargo Congressman.")
		await sendDM(ctx.author, f"Se te ha asignado el canal {ctx.author} en la sección **ELECCIONES CONGRESSMAN** para realizar tu campaña")
		await sendDM(channel, f"Este es el canal de la lista **{nombreDeLista}** del postulante a **Congressman** {ctx.author.mention}\n")
		#HARDCODED los requerimientos
		await sendDM(channel, f"**Los requerimientos mínimos son que tu lista tenga por lo menos 2 inspectores**\n")
		await channel.send(f'Comandos disponibles:')
		await channel.send(f'```Invitar un First Inspector a tu lista: \n>agregarFirstInspector @nombreDelUsuario```')
		await channel.send(f'```Invitar un Inspector a tu lista: \n>agregarInspector @nombreDelUsuario```')
		await channel.send(f'```Ver el estado de tu lista y si cumple los requerimientos mínimos: \n>estadoLista```')
		await channel.send(f'```Agregar imagen de lista: \n>agregarImagenLista [URL de imagen]```')
		await channel.send(f'```Agregar color de lista (código hexadecimal sin el #): \n>agregarColorLista F2A23B```')
	else:
		await sendDM(ctx.author, f"No hay elecciones en progreso")


@discordBot.command(name="agregarInspector", brief='Agregar inspector a mi lista')
async def addInspector(ctx, inspector):
	#HARDCODED. CAMBIAR PARA ACTUALIZACION
	inspectorRole = getInspectorRole(ctx)
	name_of_role = "Inspector"
	#_____________________________________
	campaignChannel = getCandidateCampaignChannel(ctx.author.id)
	if not isMemberOwnerOfElectionChannel(ctx):
		await sendDM(ctx.author, "Este comando solo puede ser utilizado en tu canal de campaña")
		return 
	if not arePostulationsRunning(ctx):	
		await sendDM(ctx.author, f"Las listas ya están cerradas, mejor suerte para la próxima")
		return
	postulatedInspector = getPingedMember(ctx, inspector)
	if not postulatedInspector:
		await sendDM(ctx.author, f"El miembro enviado no existe, asegurate de usar @NombreMiembro para encontrarlo")
		return
	if not memberCastsVote(ctx, postulatedInspector.id):
		await sendDM(ctx.author, f"El miembro que invitaste a tu lista no tiene rango suficiente")
		return
	if isOnAListAlready(postulatedInspector.id):
		await sendDM(ctx.author, f"El miembro al que se le envió la oferta ya confirmó su participación en otra lista")
		return
	if postulatedInspector.id == ctx.author.id:
		await sendDM(ctx.author, f"No te podés enviar una oferta a vos mismo para un cargo en tu campaña, otario")
		return
	if getCandidateCampaignChannel(postulatedInspector.id):
		await sendDM(ctx.author, f"A {postulatedInspector.mention} no se le puede enviar una oferta como {name_of_role} de tu lista. Es un candidato a Congressman")
		return	
	if hasOfferInThisList(ctx):
		await sendDM(ctx.author, f"Error al agregar inspector {postulatedInspector.mention}: Este usuario ya recibió una oferta de tu parte")
		return
	postulationStatus = await addPostulationOffer(ctx, ctx.author.id, postulatedInspector.id, campaignChannel.id, inspectorRole.id)
	if postulationStatus == True:
		await sendDM(ctx.author, f"Has enviado una oferta a {postulatedInspector.mention} para ser {name_of_role} en tu lista. Solo falta que la confirme")
		await sendDM(campaignChannel, f"{postulatedInspector.mention}: {ctx.author.mention} quiere que seas {name_of_role} en su lista. Para confirmar utiliza el siguiente comando en este canal: ```>confirmar```")
		await ctx.channel.set_permissions(postulatedInspector, send_messages=True)


@discordBot.command(name="agregarFirstInspector", brief='Agregar First Inspector a mi lista')
async def addInspector(ctx, inspector):
	#HARDCODED. CAMBIAR PARA ACTUALIZACION
	inspectorRole = getFirstInspectorRole(ctx)
	name_of_role = "First Inspector"
	#_____________________________________
	campaignChannel = getCandidateCampaignChannel(ctx.author.id)
	if not isMemberOwnerOfElectionChannel(ctx):
		await sendDM(ctx.author, "Este comando solo puede ser utilizado en tu canal de campaña")
		return 
	if not arePostulationsRunning(ctx):	
		await sendDM(ctx.author, f"Las listas ya están cerradas, mejor suerte para la próxima")
		return
	postulatedInspector = getPingedMember(ctx, inspector)
	if not postulatedInspector:
		await sendDM(ctx.author, f"El miembro enviado no existe, asegurate de usar @NombreMiembro para encontrarlo")
		return
	if not memberCastsVote(ctx, postulatedInspector.id):
		await sendDM(ctx.author, f"El miembro que invitaste a tu lista no tiene rango suficiente")
		return
	if isOnAListAlready(postulatedInspector.id):
		await sendDM(ctx.author, f"El miembro al que se le envió la oferta ya confirmó su participación en otra lista")
		return
	if postulatedInspector.id == ctx.author.id:
		await sendDM(ctx.author, f"No te podés enviar una oferta a vos mismo para un cargo en tu campaña, otario")
		return
	if getCandidateCampaignChannel(postulatedInspector.id):
		await sendDM(ctx.author, f"A {postulatedInspector.mention} no se le puede enviar una oferta como {name_of_role} de tu lista. Es un candidato a Congressman")
		return	
	if hasOfferInThisList(ctx):
		await sendDM(ctx.author, f"Error al agregar {name_of_role} {postulatedInspector.mention}: Este usuario ya recibió una oferta de tu parte")
		return
	postulationStatus = await addPostulationOffer(ctx, ctx.author.id, postulatedInspector.id, campaignChannel.id, inspectorRole.id)
	if postulationStatus == True:
		await sendDM(ctx.author, f"Has enviado una oferta a {postulatedInspector.mention} para ser {name_of_role} en tu lista. Solo falta que la confirme")
		await sendDM(campaignChannel, f"{postulatedInspector.mention}: {ctx.author.mention} quiere que seas {name_of_role} en su lista. Para confirmar utiliza el siguiente comando en este canal: ```>confirmar```")
		await ctx.channel.set_permissions(postulatedInspector, send_messages=True)





#QUERYs BIFROST-DEMOCRATIA
#HARDCODED
def getCongressmanRole(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT role_id from election_role WHERE role_name = 'Congressman'")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		role_id = rows[0][0]
		role =  ctx.guild.get_role(role_id)
		return role
	else:
		return None


def getInspectorRole(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT role_id from election_role WHERE role_name = 'Inspector'")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		role_id = rows[0][0]
		role =  ctx.guild.get_role(role_id)
		return role
	else:
		return None

#HARDCODED
def getFirstInspectorRole(ctx):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"SELECT role_id from election_role WHERE role_name = 'First Inspector'")
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()
	if rows:
		role_id = rows[0][0]
		role =  ctx.guild.get_role(role_id)
		return role
	else:
		return None

@discordBot.command(name="confirmar", brief='Este comando confirma el puesto que se te ha ofrecido en una lista')
async def confirmPostulationOffer(ctx):
	if isOnAListAlready(ctx.author.id):
		await sendDM(ctx.author, "Ya aceptaste una oferta. Esto es irrevocable.")
		return
	if not isThisACampaignChannel(ctx):
		await sendDM(ctx.author, "Este comando solo puede ser utilizado en un canal de campaña en el cual tengas una oferta")
		return
	if getElectableCongressmanData(ctx.author.id, ctx):
		await sendDM(ctx.author, "No podés aceptar una posición en otra lista, sos candidato a Congresman")
		return
	confirmedCandidateTuple = hasOfferInThisList(ctx)
	if confirmedCandidateTuple:
		postulatedRoleId = confirmedCandidateTuple[1]
		congressmanPostulatorId = confirmedCandidateTuple[2]
		print(f"postulatedRoleId: {postulatedRoleId}")
		print(f"congressmanPostulatorId: {congressmanPostulatorId}")

		print(f"Postulaciones del rol:{countRolePostulationsInList(congressmanPostulatorId, postulatedRoleId)}")
		print(f"Cupos totales: {getMaxPostulationsPerRole(postulatedRoleId, ctx.guild.id)}")

		if countRolePostulationsInList(congressmanPostulatorId, postulatedRoleId) >= getMaxPostulationsPerRole(postulatedRoleId, ctx.guild.id):
			await sendDM(ctx.author, "El que te envió esta oferta ya llenó todos los cupos para este puesto")
			return
		addConfirmedCandidate(confirmedCandidateTuple)
		# eliminarTodasLasPostulacionesTemporales
		# await sendDM(ctx.author, "Tu participación en esta lista ha sido confirmada")
		await sendDM(ctx.channel, f"{ctx.author.mention} ha confirmado su participación en esta lista")


@discordBot.command(name="estadoLista", brief='Ver el estado de tu lista y si ya podés confirmar la misma')
async def listStatus(ctx):
	if not arePostulationsRunning:
		pass
	if not isMemberOwnerOfElectionChannel(ctx):
		await sendDM(ctx.author, "Este comando solo puede ser utilizado en tu canal de campaña")
		return 
	electionRoles = getElectionRoles(ctx)
	ecd = getElectableCongressmanData(ctx.author.id, ctx)
	lmd = getListMembersData(ctx.author.id)
	inspectorNames = []
	inspectorNamesString = ''
	colorHexString = str(ecd['list_color'])
	
	try:
		color = int(colorHexString, base=16)
	except ValueError as err:
		color = int('0xFFFFFF', base=16)
	embed = discord.Embed(title=f"{ecd['list_name']}", description=f"Lista {ecd['list_id']}", color=discord.Color(color))
	embed.add_field(name=f"Congressman", value=f"{ctx.guild.get_member(ecd['member_id']).name}")
	if lmd:
		for listMember in lmd:
			if listMember['role_name'] == "First Inspector":
				#HARDCODED SE ASUME UN SOLO INSPECTOR
				member_id = listMember['candidate_member_id']
				embed.add_field(name=f"First Inspector", value=f"{ctx.guild.get_member(member_id).name}")
			if listMember['role_name'] == "Inspector":
				inspectorNames.append(ctx.guild.get_member(listMember['candidate_member_id']).name)	
		if inspectorNames:	
			for inspectorName in inspectorNames:
				inspectorNamesString += inspectorName + '\n'
			embed.add_field(name=f"Inspectors", value=f"{inspectorNamesString}")
	if ecd['list_image']:
		urlImagen = ecd['list_image']
	else:
		urlImagen = 'https://i.imgur.com/mFpWgS1.jpg'
	try:	
		embed.set_image(url=urlImagen)
		await ctx.send(embed=embed)
	except discord.HTTPException as err:
		print(err)
		await ctx.author.send("Hay un error con la imagen de tu campaña, asegurate que el link que agregaste lleva a una imagen")
	if areListRequirementsOk(ctx.author.id, ctx.guild.id):
		await ctx.send("Esta lista cumple los requerimientos, pasará el cierre de listas")
	else:
		await ctx.send("Esta lista todavía no cumple los requermientos mínimos, asegurate de completarla para pasar el cierre de listas")

@discordBot.command(name="agregarImagenLista", brief='Agregar la imagen de tu lista, debe ser un link que lleve a una imagen')
async def addListImage(ctx, imageURL):
	if not isMemberOwnerOfElectionChannel(ctx):
		await sendDM(ctx.author, "Este comando solo puede ser utilizado en tu canal de campaña")
		return 
	if not arePostulationsRunning(ctx):	
		await sendDM(ctx.author, f"Las listas ya están cerradas, mejor suerte para la próxima")
		return
	error = None
	values = (str(imageURL), ctx.guild.id, ctx.author.id)
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"UPDATE electable_congressman SET list_image = ? WHERE guild_id = ? AND member_id = ?", values)
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()

@discordBot.command(name="agregarColorLista", brief='Agregar color lista. Debe ser hexadecimal, sin el #, ejemplo F2AC11')
async def addListImage(ctx, listColor):
	if not isMemberOwnerOfElectionChannel(ctx):
		await sendDM(ctx.author, "Este comando solo puede ser utilizado en tu canal de campaña")
		return 
	if not arePostulationsRunning(ctx):	
		await sendDM(ctx.author, f"Las listas ya están cerradas, mejor suerte para la próxima")
		return
	error = None
	color = '0x'+listColor
	values = (str(color), ctx.guild.id, ctx.author.id)
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(f"UPDATE electable_congressman SET list_color = ? WHERE guild_id = ? AND member_id = ?", values)
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		print(err)
	finally:
		condb.close()


@discordBot.command(name="ping", brief='TEST FUNCTION')
async def testFunction(ctx):
	pass




@discordBot.command(name="quieroVotar", hidden=True)
async def wantToVote(ctx):
	if not areElectionsRunning(ctx.guild.id):
		await ctx.author.send("No hay elecciones en curso")
		return
	if not memberCastsVote(ctx, ctx.author.id):
		await ctx.author.send("Tu rango no es suficiente para votar")
		return
	if arePostulationsRunning(ctx):
		await ctx.author.send("Las listas todavía no están cerradas")
		return
	if isVoterAlready(ctx):
		await sendDM(ctx.author, f"**Ya estás registrado como votante**, para más información andá a la sección **CUARTO OSCURO**")
		return
	boothChannelCategory = getGuildBoothsCategory(ctx)
	if boothChannelCategory:
		overwrites = {
			ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
			ctx.author: discord.PermissionOverwrite(read_messages=True)
		}	
		channel = await ctx.guild.create_text_channel(f'{ctx.author.name}', category = boothChannelCategory, overwrites=overwrites)	
		registerVoter(ctx, channel)
		await sendDM(channel, f"Este es tu cuarto oscuro {ctx.author.mention}, solo ***vos*** podés ver este canal\n\n")
		await displayLists(channel)
		await channel.send("Para votar, reaccioná a la(s) lista(s) que quieras con :thumbsup:")
		await channel.send(f"```Votos restantes: {VOTES_PER_ELECTOR_ROLE}```")

@discordBot.event
async def on_raw_reaction_add(payload):
	print(payload)
	if payload.emoji.name != '👍':
		print("solo pulgarcito arriba vota")
		return
	if not areElectionsRunning(payload.guild_id):
		await sendDM(ctx.author, f"No hay una elección en curso")
		return
	if not isVoterInsideHisBooth(payload.user_id, payload.channel_id, payload.guild_id):
		print("Tu pulgar arriba no vota, no estás adentro de tu cabina px")
		return
	currentChannel = discordBot.get_channel(payload.channel_id)
	reactedMessage = await currentChannel.fetch_message(payload.message_id)
	voterId = payload.user_id
	votedCongressmanId = 0
	

	embeds = reactedMessage.embeds
	for embed in embeds:
		try:
			votedCongressmanId = int(embed.to_dict()['footer']['text'])
		except:
			return

	if voterId and votedCongressmanId:
		votosEmitidos = await addVote(payload, voterId, votedCongressmanId)
		print(votosEmitidos)
		if votosEmitidos:
			await currentChannel.send(f"Votaste al candidato a Congressman {payload.member.guild.get_member(votedCongressmanId)}\n```Votos restantes = {VOTES_PER_ELECTOR_ROLE - votosEmitidos}```")


async def disconnectVoice(vc):
	await vc.stop()



@discordBot.command(name="finalizarElecciones")
async def endElections(ctx):
	if not isAdministrator(ctx.message.author):
		return
	if not areElectionsRunning:
		return
	if not arePostulationsRunning:
		return
	channel = ctx.author.voice.channel
	congressmanRole = getCongressmanRole(ctx)
	firstInspectorRole = getFirstInspectorRole(ctx)
	inspectorRole = getInspectorRole(ctx)

	msg = '<speak></speak>'
	

# SALUDO INICIAL
	msg = '''
	<speak>
	みなさん、こんにちは。
	<emphasis>Bifurosuto</emphasis> desu  has joined <break time="1s"/> Elections have finished <break time="1s"/> Switching voice to spanish mode
	</speak>
	'''
	filenameWithPath = pollySynthesize(msg, voiceId="Takumi", engine='standard', textType='ssml', forceName='electionsEnd')
	voiceCoso = await playAudio(filenameWithPath, channel, False)

# ELIMINAR TODOS LOS CARGOS ANTERIORES
	msg = '''
	<speak>
	Bienvenidos al recuento. Luego de quitar los cargos actuales, se anunciarán los ganadores. <break time="1.5s"/>
	Removiendo todos los cargos anteriores. Gracias por los servicios prestados. Por favor cierren la puerta cuando salgan, que hace frío afuera.	
	<break time="0.5s"/>
	</speak>
	'''

	filenameWithPath = pollySynthesize(msg, voiceId="Miguel", engine='standard', textType='ssml', forceName='electionsEnd')
	voiceCoso = await playAudio(filenameWithPath, channel, False, voiceCoso)

	while voiceCoso.is_playing():
		await asyncio.sleep(.1)


	for member in ctx.guild.members:
		if congressmanRole in member.roles:
			await member.remove_roles(congressmanRole)
		if firstInspectorRole in member.roles:
			await member.remove_roles(firstInspectorRole)
		if inspectorRole in member.roles:
			await member.remove_roles(inspectorRole)

#ASIGNAR CARGOS NUEVOS


	congressmanTop3 = countVotesAndSort(ctx)
	electable = {}
	electableArray = []
	firstInspectorId = 0
	

	gotFirst = 0

	for top in congressmanTop3:
		inspectorsIds = []

		lmd = getListMembersData(top['congressman_id'])
		
		for lmd_roles in lmd:		
			if lmd_roles['role_name'] == 'First Inspector':
				firstInspectorId = lmd_roles['candidate_member_id']

			if lmd_roles['role_name'] == 'Inspector':
				inspectorsIds.append(lmd_roles['candidate_member_id'])

		electable = {
			'congressmanId' : top['congressman_id'],
			'firstInspectorId' : firstInspectorId,
			'inspectorIds' : inspectorsIds,
			'votes' : top['votes'],
			'listName' : top['list_name'],
			'listNumber' : top['list_id']
		}

		print(electable)



		msg = f'''<speak>
		Con {electable['votes']} votos, la lista <break time="0.1s"/> {electable['listNumber']} <break time="0.1s"/> {electable['listName']} <break time="0.1s"/>  de el ahora Congressman, {ctx.guild.get_member(electable['congressmanId']).name} <break time="0.4s"/> ha sido elécta.<break time="1s"/> 
		</speak>'''

		filenameWithPath = pollySynthesize(msg, voiceId="Miguel", engine='standard', textType='ssml', forceName='electionsEnd')
		voiceCoso = await playAudio(filenameWithPath, channel, False, voiceCoso)

		while voiceCoso.is_playing():
			await asyncio.sleep(.1)

		memberGetsCongressman =  ctx.guild.get_member(electable['congressmanId'])
		await memberGetsCongressman.add_roles(congressmanRole)

		#HARDCODED, si hay mas de dos inspectors gg
		nameOfInspectorOne = ctx.guild.get_member(electable['inspectorIds'][0]).name
		nameOfInspectorTwo = ctx.guild.get_member(electable['inspectorIds'][1]).name

		if gotFirst == 0 and electable['firstInspectorId']:
			msg = f'<speak>Esta lista ha propuesto un First Inspector, y al ser la que más votos ha obtenido, démosle la bienvenida al First Inspector <break time="0.1s"/> {ctx.guild.get_member(electable["firstInspectorId"]).name} <break time="0.5s"/></speak>'
			memberGetsFirstInspector = ctx.guild.get_member(electable['firstInspectorId'])
			filenameWithPath = pollySynthesize(msg, voiceId="Miguel", engine='standard', textType='ssml', forceName='electionsEnd')
			voiceCoso = await playAudio(filenameWithPath, channel, False, voiceCoso)
			while voiceCoso.is_playing():
				await asyncio.sleep(.1)
			await memberGetsFirstInspector.add_roles(firstInspectorRole)
			gotFirst = 1

		msg = f'<speak>También, démosle la bienvenida al inspector <break time="0.1s"/> {nameOfInspectorOne} <break time="0.1s"/> y al Inspector <break time="0.1s"/> {nameOfInspectorTwo}, ambos pertenecientes a esta lista <break time="0.1s"/></speak>'

		filenameWithPath = pollySynthesize(msg, voiceId="Miguel", engine='standard', textType='ssml', forceName='electionsEnd')
		voiceCoso = await playAudio(filenameWithPath, channel, False, voiceCoso)

		while voiceCoso.is_playing():
			await asyncio.sleep(.1)

		memberGetsInspector = ctx.guild.get_member(electable['inspectorIds'][0])
		await memberGetsInspector.add_roles(inspectorRole)
		memberGetsInspector = ctx.guild.get_member(electable['inspectorIds'][1])
		await memberGetsInspector.add_roles(inspectorRole)
		
	msg = "<speak>Esta ceremonia ha terminado. Esta se repetirán en un año aproximadamente. Espero que hayan elegido sabiamente, o prepárense para sufrir las consecuencias.</speak>"
	filenameWithPath = pollySynthesize(msg, voiceId="Miguel", engine='standard', textType='ssml', forceName='electionsEnd')
	voiceCoso = await playAudio(filenameWithPath, channel, False, voiceCoso)

	await disconnectVoiceObject(voiceCoso)

async def playAudio(filenameWithPath, channel, autoStop = True, vc = None):
	try:            
		if not vc:
			vc = await channel.connect()
		vc.play(discord.FFmpegPCMAudio(filenameWithPath), after=lambda e: vc.stop())
		while vc.is_playing():
			await asyncio.sleep(.1)
		if autoStop:
			await vc.disconnect()
		return vc
	except Exception as e: 
		print(f"An exception has ocurred on elections end sound playing: {e}")


#LETSGO
clear()
discordBot.run(TOKEN)