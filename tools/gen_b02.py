#!/usr/bin/env python3
"""Sinh project Velxio cho B02: chỉ dùng NAND (74HC00) dựng NOT, AND, OR, NOR, XOR.

Mỗi cổng dựng trên một IC riêng để dễ đếm số NAND:
  U1: NOT (1 NAND) + AND (2 NAND)   U2: OR (3 NAND)
  U3: NOR (4 NAND)                   U4: XOR (4 NAND, phương án tối thiểu)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B02 - NAND la cong van nang")
p.power(40, 420)
A = p.switch("A", 170, 160, "#ffcc00")
B = p.switch("B", 170, 320, "#33cc66")

def unused(u, g):
    p.to_gnd((u, f"{g}A")); p.to_gnd((u, f"{g}B"))

def nand(u, g, a, b):
    p.wire(a, (u, f"{g}A")); p.wire(b, (u, f"{g}B"))
    return (u, f"{g}Y")

X0, DX = 480, 380
# U1: NOT A, AND
u = p.ic("00", "u1", X0, 120)
notA = nand(u, 1, A, A)
n = nand(u, 2, A, B)
andY = nand(u, 3, n, n)
unused(u, 4)
p.led(notA, "ledNOT", X0 + 130, 60, "NOT A (1 NAND)", "blue")
p.led(andY, "ledAND", X0 + 130, 150, "AND (2 NAND)", "yellow")

# U2: OR = NAND(NOT A, NOT B)
u = p.ic("00", "u2", X0 + DX, 120)
na = nand(u, 1, A, A); nb = nand(u, 2, B, B)
orY = nand(u, 3, na, nb)
unused(u, 4)
p.led(orY, "ledOR", X0 + DX + 130, 100, "OR (3 NAND)", "orange")

# U3: NOR = NOT(OR)
u = p.ic("00", "u3", X0, 420)
na = nand(u, 1, A, A); nb = nand(u, 2, B, B)
o = nand(u, 3, na, nb)
norY = nand(u, 4, o, o)
p.led(norY, "ledNOR", X0 + 130, 400, "NOR (4 NAND)", "green")

# U4: XOR với 4 NAND
u = p.ic("00", "u4", X0 + DX, 420)
n1 = nand(u, 1, A, B)
n2 = nand(u, 2, A, n1)
n3 = nand(u, 3, B, n1)
xorY = nand(u, 4, n2, n3)
p.led(xorY, "ledXOR", X0 + DX + 130, 400, "XOR (4 NAND)", "white")

p.save(sys.argv[1])
