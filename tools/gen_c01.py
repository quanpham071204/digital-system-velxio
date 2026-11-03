#!/usr/bin/env python3
"""C01: hai full adder từ hai half adder và OR; kiểm tra từ netlist."""
import itertools
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

p = Project("C01 - Cong 2 bit")
p.power(40, 740)
a0 = p.switch("A0", 160, 100)
b0 = p.switch("B0", 160, 220)
a1 = p.switch("A1", 160, 340)
b1 = p.switch("B1", 160, 460)
cin = p.switch("Cin", 160, 580)
x = p.ic("86", "xor", 480, 180)
a = p.ic("08", "and", 760, 180)
o = p.ic("32", "or", 1040, 180)

def gate(ic, n, left, right):
    p.wire(left, (ic, f"{n}A"))
    p.wire(right, (ic, f"{n}B"))
    return (ic, f"{n}Y")

def fa(bit, left, right, carry):
    # HA1: propagate và generate; HA2: sum và carry; OR ghép carry.
    prop = gate(x, 2 * bit + 1, left, right)
    gen = gate(a, 2 * bit + 1, left, right)
    total = gate(x, 2 * bit + 2, prop, carry)
    carry2 = gate(a, 2 * bit + 2, prop, carry)
    return total, gate(o, bit + 1, gen, carry2)

s0, c1 = fa(0, a0, b0, cin)
s1, cout = fa(1, a1, b1, c1)
for n in (3, 4):
    p.to_gnd((o, f"{n}A")); p.to_gnd((o, f"{n}B"))
for pin, name, y, color in ((s0, "s0", 80, "green"), (s1, "s1", 220, "yellow"), (cout, "cout", 360, "red")):
    p.led(pin, "led_" + name, 1350, y, name.upper(), color)

# Truy ngược từng chân đầu vào qua chính p.wires và các loại IC trong p.comps.
# Kết quả từ cổng lái điện trở LED, không dùng lại biểu thức FA để tự kiểm.
incoming = {}
for wire in p.wires:
    dst = (wire["end"]["componentId"], wire["end"]["pinName"])
    src = (wire["start"]["componentId"], wire["start"]["pinName"])
    if dst == p.gnd:
        continue
    if dst in incoming:
        raise ValueError(f"Hai dây cùng lái {dst}")
    incoming[dst] = src
kinds = {c["id"]: c["metadataId"] for c in p.comps}

def evaluate(pin, inputs, active=None):
    active = set() if active is None else active
    if pin in active:
        raise ValueError(f"Vòng lặp tại {pin}")
    active = active | {pin}
    if pin in inputs:
        return inputs[pin]
    if pin in incoming:
        return evaluate(incoming[pin], inputs, active)
    cid, port = pin
    if port.endswith("Y") and kinds[cid] in ("ic-74hc86", "ic-74hc08", "ic-74hc32"):
        n = port[:-1]
        left = evaluate((cid, n + "A"), inputs, active)
        right = evaluate((cid, n + "B"), inputs, active)
        return {"ic-74hc86": lambda: left ^ right, "ic-74hc08": lambda: left & right,
                "ic-74hc32": lambda: left | right}[kinds[cid]]()
    raise ValueError(f"Chân không được lái: {pin}")

for A, B, C in itertools.product(range(4), range(4), range(2)):
    inputs = {a0: A & 1, a1: A >> 1, b0: B & 1, b1: B >> 1, cin: C}
    bits = [evaluate(("r_led_" + name, "1"), inputs) for name in ("s0", "s1", "cout")]
    actual = sum(value << i for i, value in enumerate(bits))
    if actual != A + B + C:
        raise AssertionError((A, B, C, actual))
print("32/32 khớp")
p.save(sys.argv[1])


