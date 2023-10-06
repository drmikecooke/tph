from json import load
from struct import unpack

little=lambda bs:int.from_bytes(bs,'little')
big=lambda bs:int.from_bytes(bs,'big')
rootPath='/'.join(__file__.split('/')[:-1])
with open(f'{rootPath}/comp.json','rt') as file:
    dig=load(file)
    
def getRaw(logBytes):
    raw={}
    raw['press']=big(logBytes[:3])>>4
    raw['temp']=big(logBytes[3:6])>>4
    raw['hum']=big(logBytes[6:8])
    raw['light']=[little(logBytes[i:i+2]) for i in range(8,16,2)]
    return raw

def T(raw): # in degC/100
    global t_fine
    temp=raw['temp']
    dtemp=temp-dig['T1']*16
    i1=dtemp*dig['T2']
    i2=dtemp*dtemp*dig['T3']
    var1=(dtemp*dig['T2']) >> 14
    var2=(dtemp*dtemp*dig['T3']) >> 34
    t_fine=var1+var2
    return ((t_fine*5+128)>>8)/100,t_fine

def P(raw, t_fine): # in hPa
    var1=t_fine-128000
    var2=var1*var1*dig['P6']
    var2=var2+((var1*dig['P5'])<<17)
    var2 = var2+(dig['P4']<<35)
    var1 = ((var1 * var1 * dig['P3'])>>8) + ((var1 * dig['P2'])<<12)
    var1 = (((1<<47)+var1))*(dig['P1'])>>33
    if (var1 == 0):
        return 0; # avoid exception caused by division by zero
    p = 1048576-raw['press']
    p = (((p<<31)-var2)*3125)//var1
    var1 = ((dig['P9']) * (p>>13) * (p>>13)) >> 25;
    var2 = (dig['P8']*p) >> 19;
    p = ((p + var1 + var2) >> 8) + ((dig['P7'])<<4);
    return (p>>8)/100;

def H(raw,t_fine):
    v_x1_u32r = t_fine-76800
    v_x1_u32r = (((((raw['hum']<<14)-((dig['H4']) << 20)-(dig['H5']*v_x1_u32r))+16384)>>15)*\
                 (((((((v_x1_u32r*dig['H6'])>>10)*\
                      (((v_x1_u32r*dig['H3'])>>11)+32768))>>10)+2097152)*dig['H2']+8192)>>14))
    v_x1_u32r = (v_x1_u32r-(((((v_x1_u32r>>15)*(v_x1_u32r>>15))>>7)*dig['H1'])>>4))
    v_x1_u32r = 0 if v_x1_u32r < 0 else v_x1_u32r
    v_x1_u32r = 419430400 if v_x1_u32r > 419430400 else v_x1_u32r
    return (v_x1_u32r>>12)/1024

def corrected(logBytes):
    raw=getRaw(logBytes)
    correct={}
    correct['temp'],t_fine=T(raw)
    correct['press']=P(raw,t_fine)
    correct['hum']=H(raw,t_fine)
    correct['light']=raw['light'][0]
    correct['red']=round(raw['light'][1]*255/raw['light'][0]) if raw['light'][0]>0 else 0
    correct['green']=round(raw['light'][2]*255/raw['light'][0]) if raw['light'][0]>0 else 0
    correct['blue']=round(raw['light'][3]*255/raw['light'][0]) if raw['light'][0]>0 else 0
    return correct