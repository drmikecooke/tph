# dependency
from serial import Serial

# from package
from .humanise import csvRecord

from time import gmtime,sleep,time
from pathlib import Path
from glob import glob

def addrBytes(x):return x.to_bytes(2,'little')
def little(bs):return int.from_bytes(bs,'little')

location=Path("~/Documents/tph/binary").expanduser()

def getData(dev,command):
	dev.write(command)
	sleep(0.1)
	return dev.read(dev.in_waiting)
	
def fileTPH():
	if not glob("/dev/ttyACM*"):
		print("No mubit attached")
		exit(1)
	mubit=Serial(glob("/dev/ttyACM*")[0],115200,timeout=1)
	print("Microbit opened.")
	bepoch=getData(mubit,b'T') # repoch bytes
	if len(bepoch)!=4:
		print("Yelp!")
		exit(1)
	repoch=little(bepoch)
	epoch0=time()-repoch
	hour0=round(epoch0/3600)
	bpath=location/Path(f"{int(epoch0)}.bin")
	print("Binary path:",bpath)
	print('Epoch0:',epoch0,"Hour0:",hour0)
	records=little(getData(mubit,b'N'))//16
	print("Records:",records)
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
