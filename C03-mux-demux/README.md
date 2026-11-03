<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C03 — MUX 4:1 và DEMUX 1:4

## Mục tiêu

Dùng các IC Nhóm 1 74HC04, 74HC08, 74HC32 tạo MUX 4:1 và DEMUX 1:4 dùng chung hai bit chọn. Đầu ra Y của MUX được nối trực tiếp đến đầu vào dữ liệu DEMUX. Mạch phụ là một MUX riêng thực hiện hàm majority ba biến.

```text
I0, I1, I2, I3 → [MUX 4:1] ── Y ──→ [DEMUX 1:4] → D0, D1, D2, D3
                     ↑                       ↑
                     └───── S1, S0 ──────────┘
A, B → bộ chọn MUX phụ; các đầu vào 0, C, C, 1 → F
```

## Biểu thức và cấu tạo

Đặt `E0 = ¬S1·¬S0`, `E1 = ¬S1·S0`, `E2 = S1·¬S0`, `E3 = S1·S0`. Khi đó `Y = I0·E0 + I1·E1 + I2·E2 + I3·E3` và `Dk = Y·Ek`, với k từ 0 đến 3. Các đầu ra không được chọn bằng 0, kể cả khi Y=1.

Mạch phụ dùng `S1=A`, `S0=B`, `I0=0`, `I1=C`, `I2=C`, `I3=1`; do đó `F=AB+AC+BC`, bằng 1 khi ít nhất hai trong ba biến bằng 1. Mạch có 1 IC 74HC04 (dùng 4/6 cổng NOT), 5 IC 74HC08 (20/20 cổng AND), 2 IC 74HC32 (6/8 cổng OR). Mạch phụ có bộ giải mã và các cổng MUX riêng. Đầu vào cổng dư nối GND.

Mỗi công tắc có điện trở kéo xuống 10 kΩ; các LED Y, D0–D3, F có điện trở 330 Ω nối tiếp. Công tắc từ trên xuống: I0, I1, I2, I3, S0, S1, A, B, C.

<div style="page-break-before: always"></div>

## Bảng chọn MUX và DEMUX

| S1 | S0 | Y | D0 | D1 | D2 | D3 |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 0 | I0 | Y | 0 | 0 | 0 |
| 0 | 1 | I1 | 0 | Y | 0 | 0 |
| 1 | 0 | I2 | 0 | 0 | Y | 0 |
| 1 | 1 | I3 | 0 | 0 | 0 | Y |

## Bảng majority

| A | B | C | F |
|:-:|:-:|:-:|:-:|
| 0 | 0 | 0 | 0 |
| 0 | 0 | 1 | 0 |
| 0 | 1 | 0 | 0 |
| 0 | 1 | 1 | 1 |
| 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | 1 |
| 1 | 1 | 0 | 1 |
| 1 | 1 | 1 | 1 |

## Kiểm chứng và thực tế

Mở `C03-mux-demux.vlx` trong Velxio. Tạo lại và kiểm tra bằng `python tools/gen_c03.py C03-mux-demux/C03-mux-demux.vlx` từ thư mục repo. Script lưu file, dùng `vlx_extra.Circuit` đọc lại và kiểm tra đủ 64 tổ hợp bốn đầu vào dữ liệu và hai bit chọn, bao gồm từng đầu ra DEMUX không chọn bằng 0; mạch majority được kiểm 8 tổ hợp. Kiểm tra Boolean này không thay thế mô phỏng Velxio.

Trong project Velxio, VCC của IC được cấp nội bộ; khi lắp thật phải cấp đúng VCC/GND, đặt tụ decoupling sát IC, nối mức xác định cho cổng dư và tính dòng LED theo datasheet. Chưa chạy Velxio và chưa quay video cho mạch này; chưa đo phần cứng.
