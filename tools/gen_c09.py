import itertools,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import Circuit,route_for_demo
p=Project('C09 - LFSR 4 bit'); p.power(40,800)
clk,load,alt=[p.switch(n,160,y) for n,y in zip(('CLK','LOAD','ALT'),(100,240,380))]
ff=[p.ff('d',f'ff{i}',1000,100+140*i,clk) for i in range(4)]
q=[v[0] for v in ff]; nq=[v[1] for v in ff]
idx=0
def g(kind,*xs):
    global idx
    n=idx; idx+=1
    return p.gate(kind,f'g{n}',400+150*(n//5),80+110*(n%5),*xs)
def AND(a,b): return g('and',a,b)
def OR(a,b): return g('or',a,b)
def NOT(a): return g('not',a)
def alland(xs):
    out=xs[0]
    for x in xs[1:]: out=AND(out,x)
    return out
nalt=NOT(alt); nl=NOT(load)
tap=OR(AND(nalt,q[2]),AND(alt,q[1]))
xor=OR(AND(q[3],NOT(tap)),AND(nq[3],tap))
zero=alland(nq)
d0=OR(load,AND(nl,OR(xor,zero)))
for i,d in enumerate([d0]+[AND(nl,q[i]) for i in range(3)]): p.wire(d,(f'ff{i}','D'))
for i,src in enumerate(q): p.led(src,f'led_q{i}',1400,100+140*i,f'Q{i}','green')
route_for_demo(p); path=sys.argv[1]; p.save(path)
def state(n): return {f'ff{i}':(n>>i)&1 for i in range(4)}
def number(s): return sum(s[f'ff{i}']<<i for i in range(4))
def step(n,A,L):
    inputs={'CLK':1,'ALT':A,'LOAD':L}
    c=Circuit(path,inputs=inputs,state=state(n))
    assert all(c.read((f'ff{i}','CLK'))==1 for i in range(4))
    return number(c.step({**inputs,'CLK':0}))
for n,A,L in itertools.product(range(16),(0,1),(0,1)):
    feedback=((n>>3)^(n>>(1 if A else 2)))&1
    expected=1 if L else ((n<<1)&15)|(feedback or n==0)
    assert step(n,A,L)==expected,(n,A,L,expected)
print('Saved VLX: 64/64 state/ALT/LOAD cases')
for A in (0,1):
    seq=[1]; n=step(1,A,0)
    while n not in seq:
        seq.append(n); n=step(n,A,0)
    assert n==1
    assert len(seq)==(15 if A==0 else 6),(A,seq)
    print('ALT',A,'period',len(seq),'sequence',' -> '.join(''.join(str((v>>i)&1) for i in range(4)) for v in seq+[n]))
assert step(0,0,0)==1 and step(0,1,0)==1
print('0000 -> 1000 for both taps; 15-cycle excludes zero')
