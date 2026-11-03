<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C04 — Giải mã 2 sang 4 và LED 7 đoạn

## Thiết kế

Hai công tắc A, B mã hóa số 0–3 (A là bit cao). Decoder có Enable E, mức 1 cho phép; E=0 thì D0–D3 đều bằng 0. Nhánh LED 7 đoạn hiển thị độc lập với E. Mạch chỉ dùng IC Nhóm 1: 74HC00 và 74HC02.

```text
A, B ──→ [giải mã 2→4] ──→ D0, D1, D2, D3
E ─────→       ↑
A, B ──→ [logic 7 đoạn] ──→ a,b,c,d,e,f,g → 7 LED rời
```

`D0=E·¬A·¬B`, `D1=E·¬A·B`, `D2=E·A·¬B`, `D3=E·A·B`. Các đoạn sáng mức 1: `a=d=A+¬B`, `b=1`, `c=¬A+B`, `e=¬B`, `f=¬A·¬B`, `g=A`. Các biểu thức chỉ áp dụng cho 0–3.

Dùng 2 IC 74HC00 (8/8 NAND) và 1 IC 74HC02 (4/4 NOR), tổng 12 cổng hoạt động. Ba NAND đảo A, B, E; bốn NAND tạo các tiền-term của decoder. Hai tiền-term còn dùng trực tiếp cho đoạn a/d và c; NAND thứ tám đảo tiền-term của D0 để tạo đoạn f. Bốn NOR ghép các tiền-term với ¬E thành D0–D3. Thiết kế giảm từ bốn IC xuống ba; chưa chứng minh tối ưu toàn cục. Mỗi công tắc có pull-down 10 kΩ; mỗi LED D0–D3 và mỗi LED đoạn a–g có một điện trở 330 Ω.

```text
      a
    ─────
 f │     │ b
    ──g──
 e │     │ c
    ─────
      d
```

<div style="page-break-before: always"></div>

## Bảng decoder

| E | A | B | D0 | D1 | D2 | D3 |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | X | X | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | 0 | 1 | 0 | 0 |
| 1 | 1 | 0 | 0 | 0 | 1 | 0 |
| 1 | 1 | 1 | 0 | 0 | 0 | 1 |

## Bảng LED 7 đoạn

1 là sáng. E không ảnh hưởng phần hiển thị. Bảy LED rời được đặt thành hình số 8: a trên, b trên-phải, c dưới-phải, d dưới, e dưới-trái, f trên-trái, g giữa; nhãn trên sơ đồ là a–g.

| A | B | Số | a | b | c | d | e | f | g |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| 0 | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 1 | 0 | 2 | 1 | 1 | 0 | 1 | 1 | 0 | 1 |
| 1 | 1 | 3 | 1 | 1 | 1 | 1 | 0 | 0 | 1 |

## Kiểm chứng và thực tế

Mở `C04-giai-ma.vlx` trong Velxio. Chạy `python tools/gen_c04.py C04-giai-ma/C04-giai-ma.vlx` từ thư mục repo: script lưu rồi đọc lại file qua `vlx_extra.Circuit`, đối chiếu 8 tổ hợp A, B, E cho cả bốn đầu decoder và trạng thái của bảy LED đoạn.

> Trong đường mô phỏng SPICE đã kiểm tra, linh kiện `7segment` không được ánh xạ từ điện áp các chân sang trạng thái sáng; thành phần này vẫn tối dù các tín hiệu a–g đúng. Bảng ánh xạ SPICE của Velxio không có mapper `7segment` ([componentToSpice.ts](https://github.com/davidmonterocrespo24/velxio/blob/master/frontend/src/simulation/spice/componentToSpice.ts)); do đó bài dùng bảy LED rời có điện trở 330 Ω thay cho màn hình 7-segment. Kiểm tra này xác nhận trạng thái logic trong evaluator và giao diện Velxio, không phải thử nghiệm phần cứng.

Trong Velxio IC được cấp VCC nội bộ; mạch thật cần nối đúng nguồn và GND, tụ decoupling sát IC, mức xác định cho cổng dư, và tính điện trở theo điện áp thuận LED, dòng cho phép của IC và datasheet. Có thể mở rộng lên 3 bit 0–7 bằng thêm ngõ vào và thiết kế lại các biểu thức cho tám mẫu; mạch hiện tại không thực hiện phần mở rộng.
