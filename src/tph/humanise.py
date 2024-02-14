from pathlib import Path
from time import gmtime
from .TPHlrgb import corrected

dataFormat='\n{:02n},{:2.1f},{:4.1f},{:2.1f},{},{},{},{}'
head="t/h,T/°C,P/hPa,H/%RH,L,R,G,B"

location=Path("/home/mike/Documents/github/tph-data")
source=location/Path("binary")
drain=location/Path("humanised")

def records(path):
	with path.open("rb") as f:
		record=f.read(16)
		bhour=0
		while record:
			yield bhour,record
			record=f.read(16)
			bhour+=1
			
def csvRecord(ehour,record):
	gm=gmtime(ehour*3600)[:4] # get human form of epoch hour
	csv=drain/Path('{}/{:02n}/{:02n}.csv'.format(*gm[:3]))
	data=[gm[3]]+list(corrected(record).values())
	line=dataFormat.format(*data)
	if not csv.exists():line=head+line # put header on new file
	csv.parent.mkdir(parents=True, exist_ok=True) # create directories if necessary
	csv.open("a").write(line)

def csvBuild():
	for bfile in source.glob("*.bin"):
		epoch0=int(bfile.name.split('.')[0])
		bhour0=round(epoch0/3600)
		for bhour,record in records(bfile):
			csvRecord(bhour0+bhour,record)
