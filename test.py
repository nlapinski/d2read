import d2mem

for thing in dir(d2mem):
	print(thing)

for thing in dir(d2mem.enums):
	print("enum ->:" + str(thing))