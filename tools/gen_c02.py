import itertools, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project
from vlx_extra import route_for_demo
p = Project('C02 - Cong tru 2 bit')
p.power(40, 740)
a0,b0,a1,b1,m = [p.switch(n,160,y) for n,y in zip(('A0','B0','A1','B1','M'),(100,220,340,460,580))]
x = p.ic('86','xor',480,180)
x2 = p.ic('86','xor2',700,180)
a = p.ic('08','and',950,180)
o = p.ic('32','or',1200,180)
def gate(ic,n,l,r):
    p.wire(l,(ic,str(n)+'A')); p.wire(r,(ic,str(n)+'B'))
    return (ic,str(n)+'Y')
b0x = gate(x,1,b0,m); b1x = gate(x,2,b1,m)
def fa(bit,left,right,carry):
    prop=gate(x,3+bit,left,right)
    gen=gate(a,1+2*bit,left,right)
    total=gate(x2,1+bit,prop,carry)
    carry2=gate(a,2+2*bit,prop,carry)
    return total,gate(o,1+bit,gen,carry2)
s0,c1=fa(0,a0,b0x,m)
s1,cout=fa(1,a1,b1x,c1)
over=gate(x2,3,c1,cout)
for ic,nums in ((x2,(4,)),(o,(3,4))):
    for n in nums:
        p.to_gnd((ic,str(n)+'A')); p.to_gnd((ic,str(n)+'B'))
for pin,name,y,color in ((s0,'s0',80,'green'),(s1,'s1',220,'yellow'),(cout,'cout',360,'red'),(over,'overflow',500,'red')):
    p.led(pin,'led_'+name,1500,y,name.upper(),color)
path=sys.argv[1]
route_for_demo(p)
p.save(path)
with open(path,encoding='utf-8') as f: data=json.load(f)
incoming={}
for w in data['wires']:
    dst=(w['end']['componentId'],w['end']['pinName']); src=(w['start']['componentId'],w['start']['pinName'])
    if dst==('src','GND'): continue
    if dst in incoming: raise ValueError(f'Multiple drivers: {dst}')
    incoming[dst]=src
kinds={c['id']:c['metadataId'] for c in data['components']}
def ev(pin,inputs,active=frozenset()):
    if pin in active: raise ValueError(f'Loop: {pin}')
    active=active|{pin}
    if pin in inputs: return inputs[pin]
    if pin in incoming: return ev(incoming[pin],inputs,active)
    cid,port=pin
    if port.endswith('Y') and kinds[cid] in ('ic-74hc86','ic-74hc08','ic-74hc32'):
        n=port[:-1]; l=ev((cid,n+'A'),inputs,active); r=ev((cid,n+'B'),inputs,active)
        return {'ic-74hc86':lambda:l^r,'ic-74hc08':lambda:l&r,'ic-74hc32':lambda:l|r}[kinds[cid]]()
    raise ValueError(f'Undriven: {pin}')
for A,B,M in itertools.product(range(4),range(4),range(2)):
    inputs={a0:A&1,a1:A>>1,b0:B&1,b1:B>>1,m:M}
    got=[ev(('r_led_'+n,'1'),inputs) for n in ('s0','s1','cout','overflow')]
    unsigned=A+(B if not M else (B^3))+M
    signed=lambda v:v if v<2 else v-4
    result=signed(A)+(signed(B) if not M else -signed(B))
    expected=[unsigned&1,(unsigned>>1)&1,(unsigned>>2)&1,int(not -2<=result<=1)]
    if got!=expected: raise AssertionError((A,B,M,got,expected))
print('Saved VLX: 32/32 combinations passed; signed subtraction overflow = 4/16')
