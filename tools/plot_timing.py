#!/usr/bin/env python3
"""Vẽ giản đồ thời gian từ chuỗi trạng thái đo được trong Velxio.

Đầu vào: file JSON {"title": ..., "steps": [nhãn bước, ...],
                    "signals": {"tên": [0/1 mỗi bước], ...}}
Mỗi bước là một lần gạt công tắc (clock tay), nên trục ngang là thứ tự bước.
Cách dùng: python3 tools/plot_timing.py data.json out.png
"""
import json, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

spec = json.load(open(sys.argv[1]))
sig = spec["signals"]
n = len(spec["steps"])
fig, ax = plt.subplots(figsize=(max(7, 0.55 * n + 2), 0.75 * len(sig) + 1.4))
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
for k, (name, vals) in enumerate(sig.items()):
    base = (len(sig) - 1 - k) * 1.5
    xs, ys = [], []
    for i, v in enumerate(vals):
        xs += [i, i + 1]; ys += [base + v, base + v]
    ax.plot(xs, ys, lw=2, color=colors[k % len(colors)])
    ax.text(-0.3, base + 0.4, name, ha='right', va='center', fontsize=10)
for i in range(n + 1):
    ax.axvline(i, color='#ddd', lw=0.6, zorder=0)
for i, lab in enumerate(spec["steps"]):
    ax.text(i + 0.5, -0.9, lab, ha='center', va='top', fontsize=7.5, rotation=0)
ax.set_xlim(-0.2, n + 0.2); ax.set_ylim(-1.8, len(sig) * 1.5)
ax.axis('off')
ax.set_title(spec.get("title", ""), fontsize=11)
fig.tight_layout()
fig.savefig(sys.argv[2], dpi=130)
