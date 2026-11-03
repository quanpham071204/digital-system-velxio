import itertools,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import route_for_demo
from vlx_extra import Circuit
p=Project('C07 - Dem len xuong'); p.power(40,650)
clk=p.switch('CLK',160,100); u=p.switch('U',160,240,value=1)
q=[p.ff('t',f'ff{i}',1000,100+140*i,clk)[0] for i in range(3)]
counter=0
def gate(kind,*pins):
    global counter
    n=counter; counter+=1
    return p.gate(kind,f'g{n}',350+150*(n//5),80+110*(n%5),*pins)
def alland(*xs):
    value=xs[0]
    for v in xs[1:]: value=gate('and',value,v)
    return value
nu=gate('not',u); nq=[gate('not',x) for x in q]
t1=gate('or',alland(u,q[0]),alland(nu,nq[0]))
t2=gate('or',alland(u,q[0],q[1]),alland(nu,nq[0],nq[1]))
over=gate('or',alland(u,*q),alland(nu,*nq))
for i,t in enumerate((p.vcc,t1,t2)): p.wire(t,(f'ff{i}','T'))
for i,src in enumerate((*q,over)): p.led(src,f'led_{"q"+str(i) if i<3 else "over"}',1400,100+140*i,f'Q{i}' if i<3 else 'OVER','green')
path=sys.argv[1]; route_for_demo(p)
p.save(path)
def state(n): return {f'ff{i}':(n>>i)&1 for i in range(3)}
for n,U,(old,new) in itertools.product(range(8),(0,1),((0,1),(1,1),(1,0))):
    c=Circuit(path,inputs={'CLK':new,'U':U},state=state(n))
    assert c.leds()['led_over']==int((U and n==7) or (not U and n==0))
    assert all(c.read((f'ff{i}','CLK'))==new for i in range(3))
    expected=(n+(1 if U else -1))%8 if (old,new)==(0,1) else n
    assert c.step({'CLK':old,'U':U})==state(expected),(n,U,old,new)
    # Changing U without an edge cannot change Q; next rising edge uses the new direction.
    c=Circuit(path,inputs={'CLK':0,'U':1-U},state=state(n))
    assert c.step({'CLK':0,'U':U})==state(n)
    c=Circuit(path,inputs={'CLK':1,'U':1-U},state=state(n))
    assert c.step({'CLK':0,'U':1-U})==state((n+(-1 if U else 1))%8)
print('Saved VLX: 48/48 clock cases, terminal OVER, direction changes verified')
for U in (1,0):
    st=state(0); seq=[0]
    for _ in range(8):
        st=Circuit(path,inputs={'CLK':1,'U':U},state=st).step({'CLK':0,'U':U})
        seq.append(sum(st[f'ff{i}']<<i for i in range(3)))
    print(('up' if U else 'down')+':',seq)
print('Basic gates:',counter)
