import random

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