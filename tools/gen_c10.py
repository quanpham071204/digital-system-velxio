import itertools,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import Circuit,route_for_demo
p=Project('C10 - Phat hien 1011'); p.power(40,800)
clk,x,reset=[p.switch(n,160,y) for n,y in zip(('CLK','X','RESET'),(100,240,380))]
ff=[p.ff('d',f'ff{i}',1000,100+140*i,clk) for i in range(3)]
q0,q1,z=[v[0] for v in ff]; nq0=ff[0][1]
idx=0
def g(kind,*pins):
    global idx
    n=idx; idx+=1
    return p.gate(kind,f'g{n}',400+150*(n//5),80+110*(n%5),*pins)
def AND(a,b): return g('and',a,b)
def OR(a,b): return g('or',a,b)
def NOT(a): return g('not',a)
nr=NOT(reset); nx=NOT(x)
d0=AND(nr,x)
d1=AND(nr,OR(AND(nx,q0),AND(AND(x,q1),nq0)))
dz=AND(nr,AND(AND(q1,q0),x))
for i,d in enumerate((d0,d1,dz)): p.wire(d,(f'ff{i}','D'))
for i,(src,name) in enumerate(((q0,'q0'),(q1,'q1'),(z,'z'))): p.led(src,'led_'+name,1400,(100,240,400)[i],name.upper(),'green')
route_for_demo(p); path=sys.argv[1]; p.save(path)
def st(n,z=0): return {'ff0':n&1,'ff1':(n>>1)&1,'ff2':z}
trans=((0,1),(2,1),(0,3),(2,1))
for n,X,R,Z,(old,new) in itertools.product(range(4),(0,1),(0,1),(0,1),((0,1),(1,1),(1,0))):
    c=Circuit(path,inputs={'CLK':new,'X':X,'RESET':R},state=st(n,Z))
    assert all(c.read((f'ff{i}','CLK'))==new for i in range(3))
    expected=st(0,0) if (old,new)==(0,1) and R else st(trans[n][X],int(n==3 and X==1)) if (old,new)==(0,1) else st(n,Z)
    assert c.step({'CLK':old,'X':X,'RESET':R})==expected,(n,X,R,Z,old,new,expected)
print('Saved VLX: 4 states x X x RESET x previous Z x 3 clocks = 96/96')
for stream in ('1011','1011011','00011101011'):
    state=st(0); hits=[]
    for i,bit in enumerate(stream,1):
        X=int(bit); state=Circuit(path,inputs={'CLK':1,'X':X,'RESET':0},state=state).step({'CLK':0,'X':X,'RESET':0})
        if state['ff2']: hits.append(i)
    reference=[i for i in range(1,len(stream)+1) if stream[max(0,i-4):i]=='1011']
    assert hits==reference,(stream,hits,reference)
    print(stream,'hits',hits)
print('Synchronous RESET and hold with no rising edge verified')
