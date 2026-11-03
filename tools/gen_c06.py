import argparse, itertools, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import route_for_demo
from vlx_extra import Circuit
parser=argparse.ArgumentParser(); parser.add_argument('path'); parser.add_argument('--N',type=int,choices=(5,6,7),default=6); args=parser.parse_args(); N=args.N
p=Project(f'C06 - Dem dong bo mod {N}'); p.power(40,600); clk=p.switch('CLK',160,100)
q=[p.ff('d',f'ff{i}',1000,100+140*i,clk)[0] for i in range(3)]
count=0
def gate(kind,*pins):
    global count
    n=count; count+=1
    return p.gate(kind,f'g{n}',350+(n//5)*150,80+(n%5)*115,*pins)
notq=[gate('not',v) for v in q]
def and_all(xs):
    value=xs[0]
    for x in xs[1:]: value=gate('and',value,x)
    return value
def or_all(xs):
    value=xs[0]
    for x in xs[1:]: value=gate('or',value,x)
    return value
for bit in range(3):
    terms=[]
    for n in range(8):
        nxt=n+1 if n<N-1 else 0
        if (nxt>>bit)&1: terms.append(and_all([q[i] if (n>>i)&1 else notq[i] for i in range(3)]))
    p.wire(or_all(terms),(f'ff{bit}','D'))
    p.led(q[bit],f'led_q{bit}',1400,100+140*bit,f'Q{bit}','green')
route_for_demo(p)
p.save(args.path)
def state(n): return {f'ff{i}':(n>>i)&1 for i in range(3)}
for n,(old,new) in itertools.product(range(8),((0,1),(1,1),(1,0))):
    c=Circuit(args.path,inputs={'CLK':new},state=state(n))
    assert all(c.read((f'ff{i}','CLK'))==new for i in range(3))
    nxt=n+1 if old==0 and new==1 and n<N-1 else 0 if old==0 and new==1 else n
    assert c.step({'CLK':old})==state(nxt),(n,old,new,nxt)
seq=[0]; st=state(0)
for _ in range(N):
    st=Circuit(args.path,inputs={'CLK':1},state=st).step({'CLK':0})
    seq.append(sum(st[f'ff{i}']<<i for i in range(3)))
assert seq==list(range(N))+[0]
print(f'N={N}: 24/24 transitions; sequence {seq}; {count} basic gates')
