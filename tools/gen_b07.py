#!/usr/bin/env python3
"""Sinh project Velxio cho B07: bộ so sánh độ lớn 2 bit (Nhóm 2: AND, OR, NOT, NOR rời).

  G (A>B) = A1·B1' + A1·A0·B0' + A0·B1'·B0'
  L (A<B) = A1'·B1 + A1'·A0'·B0 + A0'·B1·B0
  E (A=B) = NOR(G, L)
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B07 - So sanh do lon 2 bit")
p.power(40, 820)
A1 = p.switch("A1", 160, 80, "#ffcc00")
A0 = p.switch("A0", 160, 230, "#ffcc00")
B1 = p.switch("B1", 160, 450, "#33cc66")
B0 = p.switch("B0", 160, 600, "#33cc66")

# Cổng đảo
nA1 = p.gate("not", "n_a1", 420, 60, A1)
nA0 = p.gate("not", "n_a0", 420, 210, A0)
nB1 = p.gate("not", "n_b1", 420, 430, B1)
nB0 = p.gate("not", "n_b0", 420, 580, B0)

g = lambda kind, cid, x, y, a, b: p.gate(kind, cid, x, y, a, b)
# A > B
g1 = g("and", "g1", 600, 40, A1, nB1)                       # A1·B1'
g2a = g("and", "g2a", 600, 120, A1, A0)
g2 = g("and", "g2", 760, 120, g2a, nB0)                     # A1·A0·B0'
g3a = g("and", "g3a", 600, 200, A0, nB1)
g3 = g("and", "g3", 760, 200, g3a, nB0)                     # A0·B1'·B0'
go = g("or", "go1", 920, 80, g1, g2)
G = g("or", "go2", 1080, 140, go, g3)
# A < B
l1 = g("and", "l1", 600, 460, nA1, B1)                      # A1'·B1
l2a = g("and", "l2a", 600, 540, nA1, nA0)
l2 = g("and", "l2", 760, 540, l2a, B0)                      # A1'·A0'·B0
l3a = g("and", "l3a", 600, 620, B1, B0)
l3 = g("and", "l3", 760, 620, l3a, nA0)                     # A0'·B1·B0
lo = g("or", "lo1", 920, 500, l1, l2)
L = g("or", "lo2", 1080, 560, lo, l3)
# A = B
E = g("nor", "eq", 1240, 350, G, L)

p.led(G, "led_gt", 1400, 120, "A > B", "red")
p.led(E, "led_eq", 1400, 330, "A = B", "green")
p.led(L, "led_lt", 1400, 540, "A < B", "blue")
p.save(sys.argv[1])
