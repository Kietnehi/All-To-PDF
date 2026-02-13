# 📄 Hướng Dẫn Sử Dụng Tính Năng Extract PDF

## 🎯 Tổng Quan

Tính năng **Extract from PDF** cho phép bạn tự động trích xuất nội dung từ file PDF bao gồm:

- 📝 **Text**: Nội dung văn bản dạng Markdown và Plain Text
- 📊 **Tables**: Bảng biểu xuất ra CSV và Excel (.xlsx)
- 🖼️ **Images**: Hình ảnh, sơ đồ xuất ra PNG

## 🚀 Cài Đặt

### Bước 1: Cài đặt thư viện Python

```bash
pip install -r requirements.txt
```

Các thư viện mới được thêm:
- `docling`: Thư viện trích xuất nội dung PDF (tương thích Windows)
- `pandas`: Xử lý dữ liệu bảng
- `openpyxl`: Xuất file Excel

### Bước 2: Chạy ứng dụng

```bash
python app.py
```

Hoặc sử dụng uvicorn:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Truy cập: http://localhost:8000

## 📖 Cách Sử Dụng

### 1. Truy cập Tab "Extract from PDF"

- Mở trình duyệt và vào http://localhost:8000
- Click vào tab **"Extract from PDF"** (biểu tượng file-export)

### 2. Upload File PDF

- **Cách 1**: Kéo thả file PDF vào khu vực drop zone
- **Cách 2**: Click vào drop zone và chọn file PDF

⚠️ **Lưu ý**: Chỉ hỗ trợ file PDF (.pdf)

### 3. Trích Xuất

- Click nút **"Trích xuất & Tải về ZIP"**
- Đợi quá trình xử lý (có thể mất 10-60 giây tùy kích thước file)
- File ZIP sẽ tự động tải về

### 4. Mở Kết Quả

File ZIP chứa cấu trúc thư mục:

```
extracted_xxxxx.zip
├── text/
│   ├── extracted_text.md      (Nội dung Markdown)
│   └── extracted_text.txt     (Plain text)
├── tables/
│   ├── table_1.csv            (Bảng 1 - CSV)
│   ├── table_1.xlsx           (Bảng 1 - Excel)
│   ├── table_2.csv
│   └── table_2.xlsx
├── images/
│   ├── image_1_page_3.png     (Hình từ trang 3)
│   └── image_2_page_5.png
└── summary.txt                (Tóm tắt kết quả)
```

## 🔧 API Endpoints

### POST /extract-pdf

Trích xuất nội dung từ PDF

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
- Success: ZIP file chứa nội dung được trích xuất
- Headers: `X-Extraction-Summary` (thống kê nhanh)

**Example với curl:**

```bash
curl -X POST "http://localhost:8000/extract-pdf" \
  -F "file=@document.pdf" \
  -o extracted.zip
```

**Example với Python:**

```python
import requests

with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/extract-pdf', files=files)
    
    if response.ok:
        with open('extracted.zip', 'wb') as out:
            out.write(response.content)
        print("Extraction successful!")
    else:
        print(f"Error: {response.text}")
```

### GET /extraction-info/{extract_id}

Lấy thông tin về kết quả trích xuất

**Response:**

```json
{
  "extract_id": "uuid-string",
  "summary": "... nội dung summary.txt ...",
  "available": true
}
```

## 🌟 Tính Năng Nổi Bật

### ✅ Tương Thích Windows

- **KHÔNG CẦN** cài đặt Poppler, Tesseract, hay các công cụ phức tạp
- Sử dụng thư viện `docling` thuần Python
- Hoạt động ngay trên Windows, Linux, macOS

### ⚡ Xử Lý Thông Minh

- Tự động phát hiện và trích xuất bảng với cấu trúc phức tạp
- Nhận diện hình ảnh, sơ đồ trong PDF
- Bảo toàn format văn bản (Markdown)

### 🎨 Kết Quả Đa Dạng

- **Text**: 2 formats (Markdown + Plain text)
- **Tables**: 2 formats (CSV + Excel) để dễ mở bằng Excel
- **Images**: PNG chất lượng cao

### 🔄 Auto Cleanup

- File tự động xóa sau 2 phút để tiết kiệm dung lượng
- Upload và output được quản lý tự động

## ⚙️ Configuration

### Tùy Chỉnh Pipeline (trong app.py)

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False              # True nếu PDF là ảnh scan
pipeline_options.do_table_structure = True   # Phân tích cấu trúc bảng
pipeline_options.generate_picture_images = True  # Trích xuất hình ảnh
```

### Tùy Chỉnh Cleanup Time

Trong route `/extract-pdf`, thay đổi:

```python
await asyncio.sleep(120)  # 120 giây = 2 phút
```

## 🧪 Test với Sample PDFs

Thử nghiệm với các loại PDF:

1. **PDF văn bản thuần**: Papers, ebooks, báo cáo
2. **PDF có bảng**: Báo cáo tài chính, data tables
3. **PDF có hình ảnh**: Presentations, brochures
4. **PDF phức hợp**: Kết hợp text, tables, images

## 🐛 Troubleshooting

### Lỗi: "Extraction failed"

**Nguyên nhân:**
- File PDF bị hỏng hoặc mã hóa
- PDF quá lớn (>100MB)

**Giải pháp:**
- Kiểm tra file PDF có mở được không
- Thử với file nhỏ hơn

### Không trích xuất được bảng

**Nguyên nhân:**
- Bảng là hình ảnh (scan) chứ không phải text-based

**Giải pháp:**
- Bật OCR: `pipeline_options.do_ocr = True`
- Lưu ý: OCR cần cài Tesseract (phức tạp trên Windows)

### Hình ảnh bị mờ

**Nguyên nhân:**
- Độ phân giải PDF thấp

**Giải pháo:**
- Không thể cải thiện nếu PDF gốc chất lượng thấp
- Thử tìm PDF chất lượng cao hơn

## 📊 Performance

| PDF Size | Processing Time | Memory Usage |
|----------|----------------|--------------|
| 1-5 MB   | 5-10 seconds   | ~200 MB      |
| 5-20 MB  | 10-30 seconds  | ~500 MB      |
| 20-50 MB | 30-60 seconds  | ~1 GB        |

## 🔐 Security Notes

- File tự động xóa sau 2 phút
- Không lưu trữ permanent
- Chạy local, không gửi data ra ngoài

## 📚 Resources

- [Docling Documentation](https://github.com/DS4SD/docling)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/)

## 💡 Tips & Tricks

1. **Để ý summary.txt**: Hiển thị thống kê tổng quan
2. **Excel vs CSV**: Mở Excel files để xem bảng đẹp hơn
3. **Markdown text**: Mở bằng VS Code hoặc Typora để xem format
4. **Batch processing**: Sử dụng API endpoint để xử lý nhiều files

## 🎓 Example Use Cases

- 📊 **Nghiên cứu**: Trích xuất data từ research papers
- 💼 **Business**: Extract tables từ báo cáo tài chính
- 📖 **Education**: Lấy nội dung từ ebooks, slide bài giảng
- 🖼️ **Design**: Extract illustrations từ brochures

---

**Made with ❤️ using Docling + FastAPI**
