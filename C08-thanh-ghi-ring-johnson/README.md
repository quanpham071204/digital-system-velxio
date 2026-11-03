<style>
h2, h3 { break-after: avoid; page-break-after: avoid; }
table { break-inside: avoid; page-break-inside: avoid; }
</style>

# C08 — Thanh ghi SIPO, vòng và Johnson

## Thiết kế

Bốn D flip-flop Nhóm 2 dùng chung clock. `D1=Q0`, `D2=Q1`, `D3=Q2` khi LOAD=0. Mode chọn dữ liệu D0: JOHN=1 chọn ¬Q3 (ưu tiên cả 01 và 11); khi JOHN=0, RING=1 chọn Q3, còn RING=0 chọn DATA. Thứ tự mã trạng thái trong tài liệu là **Q0Q1Q2Q3**, Q0 ở bên trái.

| RING | JOHN | Chế độ khi LOAD=0 |
|:-:|:-:|---|
| 0 | 0 | SIPO: DATA → Q0 |
| 1 | 0 | Ring: Q3 → Q0 |
| 0 | 1 | Johnson: ¬Q3 → Q0 |
| 1 | 1 | Dự phòng, hoạt động như Johnson |

LOAD=1 ưu tiên các mode: cạnh lên nạp Q0Q1Q2Q3=1000. Gọi `X=¬JOHN·(¬RING·DATA + RING·Q3)+JOHN·¬Q3`, các phương trình thực tế là `D0=LOAD+¬LOAD·X`, `D1=¬LOAD·Q0`, `D2=¬LOAD·Q1`, `D3=¬LOAD·Q2`.

```text
DATA, Q3, ¬Q3 → [chọn mode] → [LOAD] → D0 → FF0 → Q0 → D1 → FF1 → Q1
                                                 → D2 → FF2 → Q2 → D3 → FF3 → Q3
CLK ───────────────────────────────→ chung bốn FF
Q0..Q3 và Q̄0..Q̄3 → [giải mã Johnson] → J0..J7
```

LOAD là nạp **đồng bộ**, cần cạnh clock. FF rời của Velxio không cung cấp chân PRE/CLR, do đó tiêu chí PRE/CLR không thể đáp ứng trực tiếp; LOAD có chức năng nạp nhưng không tương đương PRE/CLR bất đồng bộ hoặc khởi tạo ngay khi cấp nguồn. LED Q và J có điện trở 330 Ω, công tắc có pull-down 10 kΩ.

<div style="page-break-before: always"></div>

## Sơ đồ trạng thái

Với SIPO, cạnh lên chuyển `Q0Q1Q2Q3 → DATA,Q0,Q1,Q2`. Bảng sau biểu diễn đầy đủ 16 trạng thái và hai cạnh có thể chọn theo DATA:

| Hiện tại | DATA=0 | DATA=1 |
|:---:|:---:|:---:|
| 0000 | 0000 | 1000 |
| 1000 | 0100 | 1100 |
| 0100 | 0010 | 1010 |
| 1100 | 0110 | 1110 |
| 0010 | 0001 | 1001 |
| 1010 | 0101 | 1101 |
| 0110 | 0011 | 1011 |
| 1110 | 0111 | 1111 |
| 0001 | 0000 | 1000 |
| 1001 | 0100 | 1100 |
| 0101 | 0010 | 1010 |
| 1101 | 0110 | 1110 |
| 0011 | 0001 | 1001 |
| 1011 | 0101 | 1101 |
| 0111 | 0011 | 1011 |
| 1111 | 0111 | 1111 |

Ring từ seed LOAD=1000 (LOAD phải về 0 trước cạnh kế tiếp):

`1000 → 0100 → 0010 → 0001 → 1000`

Johnson từ 0000:

`0000 → 1000 → 1100 → 1110 → 1111 → 0111 → 0011 → 0001 → 0000`

Từ seed 1000, Johnson nằm trên cùng chu kỳ tám trạng thái. Các trạng thái ngoài chu kỳ có thể tạo vòng khác; không giả định tự phục hồi về chu kỳ hợp lệ.

<div style="page-break-before: always"></div>

## Giải mã Johnson

Tám đầu ra đều dùng một AND hai ngõ vào; dấu ¬ lấy từ Qbar của FF.

| Trạng thái Q0Q1Q2Q3 | LED sáng | Biểu thức |
|:---:|:---:|---|
| 0000 | J0 | ¬Q0·¬Q3 |
| 1000 | J1 | Q0·¬Q1 |
| 1100 | J2 | Q1·¬Q2 |
| 1110 | J3 | Q2·¬Q3 |
| 1111 | J4 | Q0·Q3 |
| 0111 | J5 | ¬Q0·Q1 |
| 0011 | J6 | ¬Q1·Q2 |
| 0001 | J7 | ¬Q2·Q3 |

Giải mã one-hot chỉ được bảo đảm trên tám trạng thái hợp lệ nêu trên; trạng thái khác có thể làm nhiều LED sáng.

## Kiểm chứng và thực tế

Chạy `python tools/gen_c08.py C08-thanh-ghi-ring-johnson/C08-thanh-ghi-ring-johnson.vlx` từ thư mục repo. Script lưu rồi đọc file bằng `vlx_extra.Circuit`, kiểm 16 trạng thái × 4 mode × 2 DATA × 2 LOAD = 256 trường hợp cạnh lên, kiểm cả tám đầu giải mã trong từng trường hợp và in chu kỳ ring bốn bước cùng Johnson tám bước. Mô hình cấp trạng thái không chứng minh khởi động phần cứng. Khi lắp thật cần mạch khởi tạo, chống dội clock, thời gian setup/hold và xét glitch khi giải mã. Chưa chạy Velxio hoặc quay video.
