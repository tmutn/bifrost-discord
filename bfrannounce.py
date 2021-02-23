import os
import boto3
from dotenv import load_dotenv

from bfrauxfunc import *

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
ANNOUNCERMP3PATH = os.getenv('ANNOUNCER_MP3_PATH')
ID_ROLES_TO_BE_ANNOUNCED = []

def initialize_roles_to_announce():
	global ID_ROLES_TO_BE_ANNOUNCED
	query_roles_to_announce = execute_sqlite(f"SELECT * from announceable_role")
	announceable_roles = []
	if query_roles_to_announce:
		for role in query_roles_to_announce:
			announceable_roles.append(role['role_id'])
	ID_ROLES_TO_BE_ANNOUNCED = announceable_roles

#Text synthetization
def polly_synthesize(text, voiceId='Takumi', engine='standard', textType ='text', forceName = False):
	
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


#Reduce AWS API calls by checking if file sound bit already exists
	filepath = f'{ANNOUNCERMP3PATH}/{filename}-voiceID={voiceId}.mp3'
	if forceName:
		filepath = f'{ANNOUNCERMP3PATH}/{forceName}.mp3'

	if os.path.isfile(f'{ANNOUNCERMP3PATH}/{filename}-voiceID={voiceId}.mp3') and not forceName:  
		return filepath
		
	elif os.path.isfile(f'{ANNOUNCERMP3PATH}/{filename}-voiceID={voiceId}.mp3') is not True:  
		file = open(filepath, 'wb')
		print(f"Generando archivo : {file}")
		file.write(response['AudioStream'].read())
		file.close()

		return filepath
	return None

def find_intro_mp3_polly(text):
	return glob.glob(f"{ANNOUNCERMP3PATH}/{text}.mp3")

#Create announcer string using role and name of user
def create_announcement_string(member, guild):
	role = highest_announceable_role_of_user(member, guild)
	member_name = member.name
	if role:
		return f"{role} {member_name} has joined"
	else:
		return None

#Get the highest announceable in this server role that the member has
def highest_announceable_role_of_user(member, guild):
	announceable_roles = get_announceable_roles(guild)
	roles_of_member_by_hierarchy = [role.id for role in member.roles][::-1]
	for role in roles_of_member_by_hierarchy:
		if role in announceable_roles:
			return member.guild.get_role(role)
	return None


#Obtain all the roles that belong to this guild and should be announced
def get_announceable_roles(discordGuild):
	print(ID_ROLES_TO_BE_ANNOUNCED)
	announceable_roles = []
	for guild in discordGuild:
		for role in guild.roles:
			if role.id in ID_ROLES_TO_BE_ANNOUNCED:
				announceable_roles.append(role.id)
	return announceable_roles

#Early disconnect a voice object
async def disconnect_voice_object(vc):
	try:            
		await vc.disconnect()
	except Exception as e: 
		print(f"Could not stop voice object because: {e}")

#Play audio in a voice channel
async def play_audio_in_channel(filenameWithPath, channel, autoStop = True, vc = None):
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



