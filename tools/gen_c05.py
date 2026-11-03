import itertools, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from vlx import Project
from vlx_extra import route_for_demo
from vlx_extra import Circuit
p=Project('C05 - Dem dong bo JK')
p.power(40,600)
clk=p.switch('CLK',160,100)
e=p.switch('E',160,240,value=1)
q=[]
for i,y in enumerate((100,240,380)):
    q.append(p.ff('jk',f'ff{i}',650,y,clk))
t1=p.gate('and','and1',420,270,e,q[0][0])
t2=p.gate('and','and2',420,400,t1,q[1][0])
for i,t in enumerate((e,t1,t2)):
    p.wire(t,(f'ff{i}','J')); p.wire(t,(f'ff{i}','K'))
    p.led(q[i][0],f'led_q{i}',1200,100+140*i,f'Q{i}','green')
path=sys.argv[1]; route_for_demo(p)
p.save(path)
def st(n): return {f'ff{i}':(n>>i)&1 for i in range(3)}
for n,E,prev,cur in itertools.product(range(8),(0,1),((0,1),(1,1),(1,0)),(0,)):
    old,new=prev
    c=Circuit(path,inputs={'CLK':new,'E':E},state=st(n))
    for i in range(3): assert c.read((f'ff{i}','CLK'))==new
    actual=c.step({'CLK':old,'E':E})
    expected=(n+1)%8 if old==0 and new==1 and E else n
    assert actual==st(expected),(n,E,old,new,actual,expected)
print('Saved VLX: 8 states x 2 E x 3 clock transitions = 48/48; common clock verified')
state=st(0); seq=[0]
for _ in range(8):
    state=Circuit(path,inputs={'CLK':1,'E':1},state=state).step({'CLK':0,'E':1})
    seq.append(sum(state[f'ff{i}']<<i for i in range(3)))
print('Sequence:', ' -> '.join(map(str,seq)), '; E=0 holds all 8 states')
