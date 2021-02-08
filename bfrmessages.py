import os
from dotenv import load_dotenv
from google.cloud import vision
from bfrauxfunc import disgrace

#Google API setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="client_secrets.json"
gcv_client = vision.ImageAnnotatorClient()

#React to a user's messages randomly
async def react_to_message(message, *arg):
	if "Hajime" in str(message.author):
		reason = "Juan escribió algo"
		if disgrace(1,3, reason):
			await message.add_reaction('♍')

#Use Google Computervision API to identify the theme of shared images
async def react_to_embedded_img(message, discordBot):
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