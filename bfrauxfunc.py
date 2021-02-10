import random
import sqlite3
from sqlite3 import Error

#executeSqlite
def executeSqlite(script):
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		cursorObj.execute(script)
		condb.commit()
	except Error as err:
		return err
	finally:
		condb.close()

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

