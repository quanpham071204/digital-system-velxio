import itertools, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import Circuit, route_for_demo
p=Project('C04 - Giai ma')
p.power(40,600)
a,b,e=[p.switch(n,160,100+120*i) for i,n in enumerate(('A','B','E'))]
blocks={'00':[p.ic('00','ic00_0',480,80),p.ic('00','ic00_1',480,320)],'02':[p.ic('02','ic02_0',760,200)]}
used={'00':0,'02':0}
def gate(kind,*args):
    n=used[kind]; used[kind]+=1; w=4
    ic=blocks[kind][n//w]; idx=n%w+1
    for pin,src in zip(('A','B'),args): p.wire(src,(ic,f'{idx}{pin}'))
    return (ic,f'{idx}Y')
na=gate('00',a,a); nb=gate('00',b,b); ne=gate('00',e,e)
# NAND outputs n1/n2 are shared by decoder terms and seven-segment outputs a/d and c.
n0=gate('00',na,nb); n1=gate('00',na,b); n2=gate('00',a,nb); n3=gate('00',a,b)
seg_f=gate('00',n0,n0)
dec=[gate('02',n,ne) for n in (n0,n1,n2,n3)]
segments={'a':n1,'b':p.vcc,'c':n2,'d':n1,'e':nb,'f':seg_f,'g':a}
for i,src in enumerate(dec): p.led(src,f'led_d{i}',1100,100+130*i,f'D{i}','green')
# Velxio's SPICE path does not drive the 7segment display, so show each
# segment as a separate LED in the familiar 8-shaped arrangement.
segment_positions={
    'a':(1600,100), 'b':(1700,220), 'c':(1700,460), 'd':(1600,580),
    'e':(1500,460), 'f':(1500,220), 'g':(1600,340),
}
for name,src in segments.items():
    led_x,led_y=segment_positions[name]
    p.led(src,f'led_seg{name}',led_x-110,led_y,name,'red')
for kind,ics in blocks.items():
    w=4
    for n in range(used[kind],len(ics)*w):
        ic=ics[n//w]; idx=n%w+1
        p.to_gnd((ic,f'{idx}A'))
        p.to_gnd((ic,f'{idx}B'))
route_for_demo(p)
path=sys.argv[1]; p.save(path)
patterns=('1111110','0110000','1101101','1111001')
for A,B,E in itertools.product((0,1),repeat=3):
    circuit=Circuit(path,inputs={'A':A,'B':B,'E':E}); leds=circuit.leds(); num=2*A+B
    expected=[int(E and i==num) for i in range(4)]
    assert [leds[f'led_d{i}'] for i in range(4)]==expected,(A,B,E,leds)
    assert ''.join(str(leds[f'led_seg{s}']) for s in 'abcdefg')==patterns[num],(A,B,E,leds)
print('Saved VLX: 8/8 A,B,E combinations passed; decoder and seven segment LEDs')
print('Gates used:',used)
