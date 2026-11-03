<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C10 — Phát hiện chuỗi 1011 có chồng lấp

## Mạch Mealy bốn trạng thái

FSM lưu tiền tố dài nhất của 1011 cũng là hậu tố chuỗi đã nhận: S0=00 rỗng, S1=01 đã thấy `1`, S2=10 đã thấy `10`, S3=11 đã thấy `101`. Khi S3 và X=1, mẫu 1011 hoàn thành. FSM cho phép chồng lấp, ví dụ 1011011 có kết quả tại bit 4 và 7.

Sơ đồ Mealy, nhãn cạnh `X/Zmealy`:

```text
S0 ──0/0→ S0   S0 ──1/0→ S1
S1 ──0/0→ S2   S1 ──1/0→ S1
S2 ──0/0→ S0   S2 ──1/0→ S3
S3 ──0/0→ S2   S3 ──1/1→ S1
```

| Hiện tại | X=0: tiếp/Zmealy | X=1: tiếp/Zmealy |
|:---:|:---:|:---:|
| S0 (00) | S0 / 0 | S1 / 0 |
| S1 (01) | S2 / 0 | S1 / 0 |
| S2 (10) | S0 / 0 | S3 / 0 |
| S3 (11) | S2 / 0 | S1 / 1 |

Mạch dùng hai D-FF trạng thái Q1,Q0 và một D-FF **đăng ký đầu ra** Z. FF thứ ba không thay đổi số trạng thái của FSM Mealy cơ sở. Với R=RESET đồng bộ:

- `D0 = ¬R·X`
- `D1 = ¬R·(¬X·Q0 + X·Q1·¬Q0)`
- `DZ = ¬R·Q1·Q0·X`

Tất cả logic chỉ dùng AND/OR/NOT Nhóm 2. RESET=1 tại cạnh lên đưa trạng thái và Z về 0. CLK, X, RESET là các công tắc từ trên xuống; LED lần lượt Q0, Q1, Z. Mỗi công tắc có pull-down 10 kΩ, mỗi LED có điện trở 330 Ω.

```text
X, Q1, Q0, RESET → [logic trạng thái] → D0,D1 → hai FF trạng thái → Q0,Q1
X, Q1, Q0, RESET → [logic phát hiện] → DZ → FF đầu ra → Z
CLK ────────────────────────────────→ chung ba FF
```

Zmealy là điều kiện tổ hợp S3·X **trước cạnh**. LED Z là giá trị đăng ký: cập nhật sau cạnh lấy mẫu bit cuối và giữ đến cạnh tiếp theo. Vì vậy Z vẫn sáng giữa hai cạnh không có nghĩa có thêm lần phát hiện; mỗi lần đếm kết quả phải lấy mẫu theo cạnh. Nếu bit kế tiếp không kết thúc mẫu, Z về 0 tại cạnh đó.

<div style="page-break-before: always"></div>

## Đối chiếu Moore năm trạng thái

A=rỗng, B=`1`, C=`10`, D=`101`, E=`1011`; chỉ E có đầu ra 1. Các cạnh ghi X:

```text
A ──0→ A    A ──1→ B
B ──0→ C    B ──1→ B
C ──0→ A    C ──1→ D
D ──0→ C    D ──1→ E
E ──0→ C    E ──1→ B
```

| Moore | X=0 | X=1 | Z |
|:---:|:---:|:---:|:-:|
| A | A | B | 0 |
| B | C | B | 0 |
| C | A | D | 0 |
| D | C | E | 0 |
| E | C | B | 1 |

Mạch đã tạo là Mealy có đăng ký đầu ra; sơ đồ Moore dùng để đối chiếu, không phải mạch thứ hai trong file.

## Kiểm chứng và thực tế

Từ thư mục repo chạy `python tools/gen_c10.py C10-phat-hien-1011/C10-phat-hien-1011.vlx`. Script lưu và đọc lại qua `vlx_extra.Circuit`, kiểm 4 trạng thái × 2 X × 2 RESET × 2 giá trị Z cũ × 3 chuyển clock = 96 trường hợp, bao gồm giữ khi không có cạnh lên. Đối chiếu cửa sổ trượt: `1011` phát hiện bit 4, `1011011` ở bit 4 và 7, `00011101011` ở bit 11.

RESET là đồng bộ, phải giữ đến một cạnh lên để xác lập trạng thái; không giả định giá trị khởi động của FF. Mạch thật cần chống dội clock, đảm bảo X/RESET thỏa setup và hold; trễ cổng và skew không được đo trong kiểm thử logic. Chưa chạy Velxio hoặc quay video.
