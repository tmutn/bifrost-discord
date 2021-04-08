#Check if the user is administrator on the server
def isAdministrator(member):
	if member.guild_permissions.administrator:
		return True
	else:
		return False

#Send a DM to everyone that can receive a DM. Exception will avoid bots
async def dmEveryone(ctx, message, discordBot):
	for member in ctx.guild.members:
		if member != discordBot.user:
			try:
				await member.send(message)
				print(f"GOES!: {member}")
			except:
				print(f"EXCEPT!: {member}")
				pass

#Obtain the role object after pinging a role
def	getPingedRole(ctx, pingedRole):
	charactersToRemove = "<>@!&"
	idPingedRole = pingedRole
	for character in charactersToRemove:
		idPingedRole = idPingedRole.replace(character, '')
	try:
		idPingedRole = int(idPingedRole)
	except:
		print("The pinged role could not be obtained")
		return None	
	for role in ctx.guild.roles:
		if role.id ==  idPingedRole:
			return role
	return None

#Obtain the member object after pinging a member
def	getPingedMember(ctx, pingedMember):
	charactersToRemove = "<>@!&"
	idPingedMember = pingedMember
	for character in charactersToRemove:
		idPingedMember = idPingedMember.replace(character, '')
	try:
		idPingedMember = int(idPingedMember)
	except:
		print("The pinged member could not be obtained")
		return None	
	for member in ctx.guild.members:
		if member.id ==  idPingedMember:
			return member
	return None