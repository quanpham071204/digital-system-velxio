#!/usr/bin/env python3
"""Sinh project Velxio cho B09: khảo sát JK Flip-Flop (Nhóm 2).

J, K, CLK là công tắc gạt (clock tay); LED Q, Q̄ và LED báo mức CLK.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from vlx import Project

p = Project("B09 - Khao sat JK Flip-Flop")
p.power(40, 520)
J = p.switch("J", 160, 80, "#ffcc00")
K = p.switch("K", 160, 230, "#33cc66")
CLK = p.switch("CLK", 160, 380, "#66ccff")
Q, Qb = p.ff("jk", "ff", 480, 200, CLK, J=J, K=K)
p.led(CLK, "led_clk", 640, 360, "CLK", "blue")
p.led(Q, "led_q", 640, 140, "Q", "red")
p.led(Qb, "led_qb", 640, 240, "Q̄", "white")
p.save(sys.argv[1])
