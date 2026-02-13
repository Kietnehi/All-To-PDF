# 🚀 Quick Start Guide - PDF Extraction

## Bước 1: Cài đặt Dependencies

Mở terminal/command prompt và chạy:

```bash
pip install -r requirements.txt
```

## Bước 2: Khởi động Server

```bash
python app.py
```

Hoặc:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Bạn sẽ thấy:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Bước 3: Truy cập Web Interface

Mở trình duyệt và vào: **http://localhost:8000**

## Bước 4: Test Extraction

### Option 1: Sử dụng Web UI

1. Click tab **"Extract from PDF"** (tab thứ 3)
2. Kéo thả file PDF hoặc click để chọn
3. Click nút **"Trích xuất & Tải về ZIP"**
4. Đợi xử lý (10-60 giây)
5. File ZIP tự động tải về

### Option 2: Sử dụng Script Test

1. Đặt file PDF vào thư mục project (ví dụ: `test.pdf`)
2. Mở file `test_extraction.py` và sửa:
   ```python
   TEST_PDF = "test.pdf"  # Tên file PDF của bạn
   ```
3. Chạy:
   ```bash
   python test_extraction.py
   ```

## Bước 5: Kiểm tra Kết quả

Giải nén file ZIP, bạn sẽ thấy:

```
extracted_xxxxx/
├── text/
│   ├── extracted_text.md      ✅ Markdown format
│   └── extracted_text.txt     ✅ Plain text
├── tables/
│   ├── table_1.csv            ✅ CSV format
│   ├── table_1.xlsx           ✅ Excel format
│   └── ...
├── images/
│   ├── image_1_page_X.png     ✅ PNG images
│   └── ...
└── summary.txt                ✅ Tóm tắt
```

## 🎯 Test Cases

### Test 1: PDF Văn bản đơn giản
- Upload một file PDF chỉ có text
- Kiểm tra `text/extracted_text.txt`

### Test 2: PDF có Bảng
- Upload PDF có tables (ví dụ: báo cáo Excel xuất ra PDF)
- Kiểm tra `tables/` folder
- Mở file `.xlsx` bằng Excel

### Test 3: PDF có Hình ảnh
- Upload PDF có images/diagrams
- Kiểm tra `images/` folder
- Xem các file PNG

## ⚡ API Testing với curl

### Windows PowerShell:
```powershell
curl.exe -X POST "http://localhost:8000/extract-pdf" `
  -F "file=@test.pdf" `
  -o extracted.zip
```

### Windows CMD:
```cmd
curl -X POST "http://localhost:8000/extract-pdf" ^
  -F "file=@test.pdf" ^
  -o extracted.zip
```

### Linux/MacOS:
```bash
curl -X POST "http://localhost:8000/extract-pdf" \
  -F "file=@test.pdf" \
  -o extracted.zip
```

## 🐛 Troubleshooting

### Lỗi: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'docling'
```
**Giải pháp:**
```bash
pip install docling pandas openpyxl
```

### Lỗi: Server không khởi động
```
ERROR:    [Errno 10048] error while attempting to bind on address...
```
**Nguyên nhân:** Port 8000 đang được sử dụng

**Giải pháp:**
```bash
# Đổi sang port khác
uvicorn app:app --port 8001
```

### Extraction quá lâu
- **Nếu PDF > 50MB**: Sẽ mất 1-2 phút
- **Nếu > 5 phút**: Kill và thử lại với PDF nhỏ hơn

### Không extract được tables
- **Nguyên nhân**: Bảng có thể là hình ảnh (scanned PDF)
- **Giải pháp**: Cần bật OCR (xem EXTRACTION_GUIDE.md)

## 📊 Expected Performance

| PDF Type | Size | Time | Output |
|----------|------|------|--------|
| Text only | 5 MB | ~10s | Text files |
| With tables | 10 MB | ~20s | Text + CSV/Excel |
| With images | 15 MB | ~30s | Text + CSV + PNG |
| Complex | 30 MB | ~60s | Full extraction |

## ✅ Checklist

- [ ] Cài đặt dependencies thành công
- [ ] Server khởi động OK
- [ ] Truy cập được web UI
- [ ] Upload PDF thành công
- [ ] Tải về ZIP file
- [ ] Giải nén và kiểm tra nội dung
- [ ] Text files readable
- [ ] Tables mở được bằng Excel
- [ ] Images hiển thị OK

## 🎓 Next Steps

1. Đọc chi tiết: [EXTRACTION_GUIDE.md](EXTRACTION_GUIDE.md)
2. Xem API docs: http://localhost:8000/docs
3. Customize code trong `app.py`
4. Deploy lên server (nếu cần)

## 💡 Tips

- Test với PDF nhỏ trước (~1-5 MB)
- Kiểm tra `summary.txt` đầu tiên
- CSV có thể mở bằng Notepad để xem raw data
- Excel files đẹp hơn CSV cho viewing

---

**Happy Extracting! 🎉**

Nếu có vấn đề, tạo issue trên GitHub hoặc xem logs trong terminal.
