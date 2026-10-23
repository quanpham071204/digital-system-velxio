#!/usr/bin/env python3
"""Sinh project Velxio cho B03: chỉ dùng NOR (74HC02) dựng NOT, OR, AND, NAND, XNOR.

Mạch đối ngẫu của B02, mỗi chức năng một IC:
  u1: NOT (1 NOR) + OR (2 NOR)   u2: AND (3 NOR)
  u3: NAND (4 NOR)               u4: XNOR (4 NOR, phương án tối thiểu)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B03 - NOR la cong van nang")
p.power(40, 420)
A = p.switch("A", 170, 160, "#ffcc00")
B = p.switch("B", 170, 320, "#33cc66")

def unused(u, g):
    p.to_gnd((u, f"{g}A")); p.to_gnd((u, f"{g}B"))

def nor(u, g, a, b):
    p.wire(a, (u, f"{g}A")); p.wire(b, (u, f"{g}B"))
    return (u, f"{g}Y")

X0, DX = 480, 380
# u1: NOT A, OR = NOT(NOR)
u = p.ic("02", "u1", X0, 120)
notA = nor(u, 1, A, A)
o = nor(u, 2, A, B)
orY = nor(u, 3, o, o)
unused(u, 4)
p.led(notA, "lednot", X0 + 130, 60, "NOT A (1 NOR)", "blue")
p.led(orY, "ledor", X0 + 130, 150, "OR (2 NOR)", "orange")

# u2: AND = NOR(NOT A, NOT B)
u = p.ic("02", "u2", X0 + DX, 120)
na = nor(u, 1, A, A); nb = nor(u, 2, B, B)
andY = nor(u, 3, na, nb)
unused(u, 4)
p.led(andY, "ledand", X0 + DX + 130, 100, "AND (3 NOR)", "yellow")

# u3: NAND = NOT(AND)
u = p.ic("02", "u3", X0, 420)
na = nor(u, 1, A, A); nb = nor(u, 2, B, B)
a_ = nor(u, 3, na, nb)
nandY = nor(u, 4, a_, a_)
p.led(nandY, "lednand", X0 + 130, 400, "NAND (4 NOR)", "red")

# u4: XNOR với 4 NOR
u = p.ic("02", "u4", X0 + DX, 420)
n1 = nor(u, 1, A, B)
n2 = nor(u, 2, A, n1)
n3 = nor(u, 3, B, n1)
xnorY = nor(u, 4, n2, n3)
p.led(xnorY, "ledxnor", X0 + DX + 130, 400, "XNOR (4 NOR)", "white")

p.save(sys.argv[1])
