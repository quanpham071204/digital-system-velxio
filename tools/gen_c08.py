import itertools, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import route_for_demo
from vlx_extra import Circuit
p=Project('C08 - SIPO Ring Johnson'); p.power(40,800)
clk,data,ring,john,load=[p.switch(n,160,y) for n,y in zip(('CLK','DATA','RING','JOHN','LOAD'),(100,220,340,460,580))]
ff=[p.ff('d',f'ff{i}',1000,100+140*i,clk) for i in range(4)]
q=[v[0] for v in ff]; nq=[v[1] for v in ff]
idx=0
def gate(kind,*pins):
    global idx
    n=idx; idx+=1
    return p.gate(kind,f'g{n}',400+150*(n//5),50+120*(n%5),*pins)
def AND(a,b): return gate('and',a,b)
def OR(a,b): return gate('or',a,b)
def NOT(a): return gate('not',a)
nr=NOT(ring); nj=NOT(john); nl=NOT(load)
select=OR(AND(nj,OR(AND(nr,data),AND(ring,q[3]))),AND(john,nq[3]))
d0=OR(load,AND(nl,select)); ds=[d0]+[AND(nl,q[i]) for i in range(3)]
for i,d in enumerate(ds): p.wire(d,(f'ff{i}','D'))
dec=[AND(x,y) for x,y in ((nq[0],nq[3]),(q[0],nq[1]),(q[1],nq[2]),(q[2],nq[3]),(q[0],q[3]),(nq[0],q[1]),(nq[1],q[2]),(nq[2],q[3]))]
for i,src in enumerate(q): p.led(src,f'led_q{i}',1300,80+i*140,f'Q{i}','green')
for i,src in enumerate(dec): p.led(src,f'led_j{i}',1500+(i//4)*150,80+(i%4)*140,f'J{i}','yellow')
path=sys.argv[1]; route_for_demo(p)
p.save(path)
def state(n): return {f'ff{i}':(n>>i)&1 for i in range(4)}
def readnum(s): return sum(s[f'ff{i}']<<i for i in range(4))
for n,R,J,D,L in itertools.product(range(16),(0,1),(0,1),(0,1),(0,1)):
    inputs={'CLK':1,'DATA':D,'RING':R,'JOHN':J,'LOAD':L}
    c=Circuit(path,inputs=inputs,state=state(n))
    a=[(n>>i)&1 for i in range(4)]; expected_dec=[(1-a[0])*(1-a[3]),a[0]*(1-a[1]),a[1]*(1-a[2]),a[2]*(1-a[3]),a[0]*a[3],(1-a[0])*a[1],(1-a[1])*a[2],(1-a[2])*a[3]]
    assert [c.leds()[f'led_j{i}'] for i in range(8)]==expected_dec
    d0=(1-a[3]) if J else a[3] if R else D
    exp=1 if L else ((n<<1)&15)|d0
    assert readnum(c.step({**inputs,'CLK':0}))==exp,(n,R,J,D,L,exp)
print('Saved VLX: 256/256 state/mode/DATA/LOAD rising-edge cases; decoder outputs checked')
def cycle(start,R,J,count):
    n=start; seq=[n]
    for _ in range(count):
        inputs={'CLK':1,'DATA':0,'RING':R,'JOHN':J,'LOAD':0}
        n=readnum(Circuit(path,inputs=inputs,state=state(n)).step({**inputs,'CLK':0})); seq.append(n)
    return [''.join(str((v>>i)&1) for i in range(4)) for v in seq]
print('RING:', ' -> '.join(cycle(1,1,0,4)))
print('JOHNSON:', ' -> '.join(cycle(0,0,1,8)))

