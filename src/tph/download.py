# dependency
from serial import Serial

# from package
from .humanise import csvRecord

from time import gmtime,sleep,time
from pathlib import Path
from glob import glob

def addrBytes(x):return x.to_bytes(2,'little')
def little(bs):return int.from_bytes(bs,'little')

location=Path("/home/mike/Documents/github/tph-data/binary")

def checkdata(condition,message):
	if condition:
		print("Yelp!:",message)
		exit(1)

def getData(dev,command):
	dev.write(command)
	sleep(0.1)
	return dev.read(dev.in_waiting)
	
def fileTPH():
	checkdata(not glob("/dev/ttyACM*"),"no mubit attached")
	mubit=Serial(glob("/dev/ttyACM*")[0],115200,timeout=1)
	print("Microbit opened.")
	bepoch=getData(mubit,b'T') # get device epoch bytes
	checkdata(len(bepoch)!=4,"no binary epoch")
	repoch=little(bepoch)
	epoch0=time()-repoch #
	hour0=round(epoch0/3600)
	bpath=location/Path(f"{int(epoch0)}.bin")
	print("Binary path:",bpath)
	print('Epoch0:',epoch0,"Hour0:",hour0)
	records=little(getData(mubit,b'N'))//16
	print("Records:",records)
	checkdata(records==0,"no records")
	binary=b''
	for n in range(records):
		record=getData(mubit,b'B'+addrBytes(n*16)+b'\x10')
		while len(record)!=16:
			record=getData(mubit,b'B'+addrBytes(n*16)+b'\x10')
		print(n,record,len(record))
		binary+=record
		csvRecord(hour0+n,record)
	bpath.write_bytes(binary)
	print("Reset:",getData(mubit,b'R'))
	mubit.close()
	print("Microbit closed.")
