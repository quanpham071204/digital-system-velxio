# 30 Bài Thử Thách Digital System – Velxio

Sinh viên: Phạm Anh Quân – 2353011 – HCMUT

Mỗi bài nằm trong một thư mục riêng, gồm:

```
Bxx-ten-bai/
├── README.md        # báo cáo: lý thuyết, thiết kế, kết quả, khác biệt mô phỏng/thực tế
├── Bxx-ten-bai.vlx  # project Velxio (File → Open project)
└── img/             # ảnh chụp canvas, giản đồ thời gian
tools/
└── gen_bxx.py       # script sinh file .vlx (tái tạo mạch tự động)
```

## Tiến độ

| Bài | Nhóm | Trạng thái |
|---|---|---|
| B01 – Kiểm tra IC 74HC | 1 | ✅ Mạch + báo cáo (thiếu ảnh chụp) |
| B02 – B10 | | ⬜ |
| C01 – C10 | | ⬜ |
| A01 – A10 (chọn 2–3) | | ⬜ |

## Mở project

1. Vào https://velxio.dev/editor/
2. **File → Open project…** → chọn file `.vlx`.
3. Click vào công tắc trên canvas để đổi ngõ vào.

## Tạo lại file .vlx

```bash
python3 tools/gen_b01.py B01-kiem-tra-IC/B01-kiem-tra-IC.vlx
```

## Lưu ý Velxio

- Không nối dây vào chân `VCC` của IC 74HC (Velxio tự cấp 5 V, nối thêm sẽ gây lỗi SPICE "singular matrix").
- Signal Generator không làm clock cho Flip-Flop được (SPICE không phát hiện cạnh). Dùng công tắc/nút nhấn làm clock tay.
- Flip-Flop của Velxio không có chân PRE/CLR.
- 74HC02 trong Velxio dùng sơ đồ chân giống 74HC00.
