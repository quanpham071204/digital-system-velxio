#!/usr/bin/env python3
"""Giản đồ thời gian lý thuyết của bộ đếm gợn 3 bit B10 (Velxio không có trễ).

Mỗi tầng: FF đảo sau t_FF kể từ cạnh lên của clock tầng đó; clock tầng sau đi
qua bộ chọn AND–OR (2 cổng, 2·t_G). Vẽ chuyển 3 -> 4 và 7 -> 0 (đếm lên), kèm
ngõ ra bộ giải mã trạng thái "000" để thấy glitch.
Cách dùng: python3 tools/plot_b10_ripple.py img/B10c_ripple_delay.png
"""
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

T_FF, T_G = 20, 10          # ns, giả định (bậc độ lớn 74HC ở 4,5 V)
T_CLK = 300                 # ns, chu kỳ clock vẽ minh họa
STAGE = T_FF + 2 * T_G      # trễ từ cạnh clock tầng i đến cạnh clock tầng i+1

def simulate(start, edges):
    """Trả về danh sách (t, state) theo thời gian cho chuỗi cạnh clock."""
    ev, q = [(0, start)], start
    for t0 in edges:
        t, i = t0, 0
        while i < 3:
            t += T_FF
            old = (q >> i) & 1
            q ^= 1 << i
            ev.append((t, q))
            if old == 1:              # Q_i rơi 1->0  =>  Q̄_i lên  => tầng sau có cạnh lên
                t += 2 * T_G
                i += 1
            else:
                break
    return ev

edges = [100, 100 + T_CLK, 100 + 2 * T_CLK, 100 + 3 * T_CLK, 100 + 4 * T_CLK]
ev = simulate(3, edges)        # 3 -> 4 -> 5 -> 6 -> 7 -> 0
t_end = edges[-1] + T_CLK
def wave(bit=None, decode=None):
    xs, ys = [], []
    for k, (t, s) in enumerate(ev):
        t2 = ev[k + 1][0] if k + 1 < len(ev) else t_end
        v = ((s >> bit) & 1) if bit is not None else int(s == decode)
        xs += [t, t2]; ys += [v, v]
    return xs, ys

fig, axs = plt.subplots(6, 1, figsize=(10, 6.2), sharex=True)
cx, cy = [0], [0]
for e in edges:
    cx += [e, e, e + T_CLK / 2, e + T_CLK / 2]; cy += [0, 1, 1, 0]
cx.append(t_end); cy.append(0)
axs[0].plot(cx, cy, color='tab:blue'); axs[0].set_ylabel('CLK', rotation=0, ha='right')
for k, b in enumerate((0, 1, 2)):
    x, y = wave(bit=b)
    axs[1 + k].plot(x, y, color='tab:green'); axs[1 + k].set_ylabel(f'Q{b}', rotation=0, ha='right')
x, y = wave(decode=0)
axs[4].plot(x, y, color='tab:red'); axs[4].set_ylabel('giải mã\n"000"', rotation=0, ha='right')
x, y = wave(decode=2)
axs[5].plot(x, y, color='tab:orange'); axs[5].set_ylabel('giải mã\n"010"', rotation=0, ha='right')
for a in axs:
    a.set_ylim(-0.2, 1.3); a.set_yticks([]); a.grid(alpha=.3)
axs[-1].set_xlabel('t (ns)')
fig.suptitle(f'B10c – Bộ đếm gợn lý thuyết: t_FF = {T_FF} ns, t_cổng = {T_G} ns (giả định), đếm 3 → 4 → … → 7 → 0')
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=130)
for t, s in ev:
    print(f"t = {t:4d} ns  Q2Q1Q0 = {s:03b} ({s})")
