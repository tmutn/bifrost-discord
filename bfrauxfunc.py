import random
import sqlite3
from sqlite3 import Error

#executeSqlite
def execute_sqlite(script):
	rows = []
	result = []
	data = {}
	data_array = []
	name_array = []
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
				name_array.append(name)
			for row in rows:
				i=0
				for value in row:
					data[name_array[i]]=value
					i=+1
				data_array.append(data)
				data = {}			
			return data_array
		if row_count:
			return True
		else:
			return False
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

