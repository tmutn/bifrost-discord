import random
import sqlite3
from sqlite3 import Error

#executeSqlite
def execute_sqlite(script):
	rows = []
	data = {}
	data_array = []
	row_count = 0
	try:
		condb = sqlite3.connect('bifrost.db')
		cursorObj = condb.cursor()
		row_count = cursorObj.execute(script).rowcount
		
		condb.commit()
		rows = cursorObj.fetchall()
	except Error as err:
		return err
	finally:
		if rows:
			names = list(map(lambda x: x[0], cursorObj.description))
			for name in names:
				data[name]=None
			for row in rows:
				i=0
				for key in data:
					data[key] = row[i]
					print(f"{key} = {row[i]}")
					i+=1					
				data_array.append(data.copy())
		if data_array:
			return data_array
		elif row_count < 1:
			return False
		else:
			return True
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

