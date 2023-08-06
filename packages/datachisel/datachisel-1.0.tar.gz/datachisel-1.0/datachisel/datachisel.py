items = []
values = []
fl = ''

def make(name):
	file = open(name+".f", 'x')
	file.close()

def load(name):
	try:
		global fl
		file = open(name + ".f", 'r')
		rawlines = file.readlines()
		for i in rawlines:
			splititems = i.split(':')
			items.append(splititems[0])
			values.append(splititems[1])
			fl = name
	except:
		print(Exception)

def add(rname, val):
	try:
		global fl
		if fl == '' or None:
			raise Exception('no file was loaded')
		file = open(fl+".f", 'a')
		file.write(f'\n{rname}:{val}')
		
	except:
		print(Exception)

def edit(name, val):
	global fl
	if fl == '' or None:
		raise Exception('no file was loaded')
	try:
		for item in items:
			if item == name:
				index = items.index(item)
		file = open(fl+'.f', 'r')
		lines = file.readlines()
		lines[index] = f'{name}:{val}\n'
		file.close()
		file = open(fl+'.f', 'w')
		file.writelines(lines)
		file.close()
	except:
		print('an exception occured while editing the line')

def delete(name):
	global fl
	if fl == '' or None:
		raise Exception('no file was loaded')
	try:
		for item in items:
			if item == name:
				index = items.index(item)
		file = open(fl+'.f', 'r')
		lines = file.readlines()
		lines[index] = ''
		file.close()
		file = open(fl+'.f', 'w')
		file.writelines(lines)
		file.close()
	except:
		print('an exception occured while editing the line')

def flush():
	global fl
	f = open(fl+".f", 'a')
	f.truncate(0)