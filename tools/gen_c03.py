import itertools, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import route_for_demo
from vlx_extra import Circuit
p=Project('C03 - MUX DEMUX')
p.power(40,800)
switches={n:p.switch(n,160,100+76*i) for i,n in enumerate(('I0','I1','I2','I3','S0','S1','A','B','C'))}
ics={}
for kind,count,x in [('04',1,450),('08',5,700),('32',2,1100)]:
    ics[kind]=[p.ic(kind,f'ic{kind}_{i}',x+(240*(i//3) if kind=='08' else 0),100+230*(i%3)) for i in range(count)]
used={'04':0,'08':0,'32':0}
def gate(kind,*inputs):
    index=used[kind]; used[kind]+=1
    width=6 if kind=='04' else 4
    ic=ics[kind][index//width]; n=index%width+1
    for pin,src in zip(('A','B'),inputs): p.wire(src,(ic,f'{n}{pin}'))
    return (ic,f'{n}Y')
def decoder(s1,s0):
    n1=gate('04',s1); n0=gate('04',s0)
    return [gate('08',u,v) for u,v in ((n1,n0),(n1,s0),(s1,n0),(s1,s0))]
def mux(sel,ins):
    terms=[gate('08',sel[i],ins[i]) for i in range(4)]
    return gate('32',gate('32',terms[0],terms[1]),gate('32',terms[2],terms[3]))
sel=decoder(switches['S1'],switches['S0'])
y=mux(sel,[switches[f'I{i}'] for i in range(4)])
outs=[gate('08',y,s) for s in sel]
sel2=decoder(switches['A'],switches['B'])
f=mux(sel2,[p.gnd,switches['C'],switches['C'],p.vcc])
for pin,name,ypos in [(y,'y',100),*[(v,f'd{i}',220+120*i) for i,v in enumerate(outs)],(f,'f',720)]:
    p.led(pin,'led_'+name,1550,ypos,name.upper(),'green')
for kind,blocks in ics.items():
    width=6 if kind=='04' else 4
    for index in range(used[kind],len(blocks)*width):
        ic=blocks[index//width]; n=index%width+1
        p.to_gnd((ic,f'{n}A'))
        if kind!='04': p.to_gnd((ic,f'{n}B'))
path=sys.argv[1]; route_for_demo(p)
p.save(path)
for bits in itertools.product((0,1),repeat=6):
    ins=dict(zip(('I0','I1','I2','I3','S0','S1'),bits))
    leds=Circuit(path,inputs=ins).leds(); selected=ins['S1']*2+ins['S0']; expected=bits[selected]
    assert leds['led_y']==expected,(bits,leds)
    assert [leds[f'led_d{i}'] for i in range(4)]==[expected if i==selected else 0 for i in range(4)],(bits,leds)
print('Main MUX/DEMUX: 64/64; unselected outputs = 0')
for a,b,c in itertools.product((0,1),repeat=3):
    led=Circuit(path,inputs={'A':a,'B':b,'C':c}).leds()['led_f']
    assert led==int(a+b+c>=2),(a,b,c,led)
print('Majority MUX: 8/8')
print('Gates used:',used)

