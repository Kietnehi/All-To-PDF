# 📄 All-to-PDF Converter (Multi-Platform)

Công cụ chuyển đổi Website, Hình ảnh và Tài liệu Office (Word, Excel, PPT) sang PDF chất lượng cao. Hỗ trợ chạy trên cả **Windows** và **Linux** (Native hoặc Docker).

## 🌟 Tính năng nổi bật
- **Đa nền tảng**: Tự động nhận diện OS để chọn engine chuyển đổi tốt nhất.
- **Windows Optimized**: Sử dụng trực tiếp Microsoft Office (Word, Excel, PowerPoint) nếu máy có sẵn.
- **Linux/Docker Ready**: Tích hợp LibreOffice cho các môi trường server hoặc container.
- **Website to PDF**: Tự động cuộn trang (Auto-scroll) để xử lý Lazy Loading ảnh, đảm bảo không mất hình.
- **Giao diện Web**: Xây dựng trên FastAPI & Bootstrap 5, hỗ trợ kéo thả file và hiển thị trạng thái xử lý.

---

## 🚀 Hướng dẫn Cài đặt & Chạy

### Cách 1: Chạy bằng Docker (Khuyên dùng - Nhanh nhất)
Bạn không cần cài đặt Python hay LibreOffice trên máy thật. Docker sẽ tự động đóng gói tất cả.
```bash
docker-compose up --build
```
Sau đó truy cập: `http://localhost:8000`

### Cách 2: Chạy trực tiếp trên máy (Native)

**1. Cài đặt Python Dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**2. Yêu cầu hệ thống:**
- **Windows**: Ưu tiên cài sẵn Microsoft Office. Nếu không có, hãy cài LibreOffice.
- **Linux**: Cài đặt LibreOffice (`sudo apt install libreoffice`).

**3. Khởi động:**
```bash
python app.py
```
Truy cập: `http://localhost:8000`

---

## 🔍 Cơ chế hoạt động theo OS

| Thành phần | Windows (Native) | Linux / Docker |
| :--- | :--- | :--- |
| **Website** | Playwright (Chromium) | Playwright (Chromium) |
| **Office Docs** | **Microsoft Office** (via pywin32) | **LibreOffice** (soffice) |
| **Hình ảnh** | Pillow (PIL) | Pillow (PIL) |

---

## 🛠 Cấu trúc dự án
- `app.py`: Server FastAPI & Logic chuyển đổi thông minh.
- `templates/index.html`: Giao diện người dùng Web.
- `Dockerfile` & `docker-compose.yml`: Cấu hình container hóa.
- `uploads/` & `outputs/`: Thư mục tạm (Tự động dọn dẹp sau 60 giây).

---

## ⚠️ Lưu ý quan trọng
- **Browser**: Nếu chạy lần đầu báo lỗi thiếu trình duyệt, hãy chạy `playwright install chromium`.
- **Dọn dẹp**: Hệ thống tự động xóa file upload và file PDF kết quả sau 1 phút để bảo mật và tiết kiệm dung lượng.
- **Docker**: Bản Docker đã cài sẵn LibreOffice bên trong, rất tiện lợi cho việc deploy lên Server Linux.

---

## 🔗 Author

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=120&section=header"/>

<p align="center">
  <a href="https://github.com/Kietnehi">
    <img src="https://github.com/Kietnehi.png" width="140" height="140" style="border-radius: 50%; border: 4px solid #A371F7;" alt="Avatar Trương Phú Kiệt"/>
  </a>
</p>

<h3>🚀 Trương Phú Kiệt</h3>

<a href="https://github.com/Kietnehi">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=236AD3&background=00000000&center=true&vCenter=true&width=435&lines=Student+@+Sai+Gon+University;Fullstack+Dev+%26+AI+Researcher;All+To+PDF" alt="Typing SVG" />
</a>

<br/><br/>

<p align="center">
  <img src="https://img.shields.io/badge/SGU-Sai_Gon_University-0056D2?style=flat-square&logo=google-scholar&logoColor=white" alt="SGU"/>
  <img src="https://img.shields.io/badge/Base-Ho_Chi_Minh_City-FF4B4B?style=flat-square&logo=google-maps&logoColor=white" alt="HCMC"/>
</p>

<p align="center">
  <a href="https://github.com/Kietnehi?tab=followers">
    <img src="https://img.shields.io/github/followers/Kietnehi?label=Followers&style=flat-square&logo=github"/>
  </a>
  <a href="https://github.com/Kietnehi">
    <img src="https://img.shields.io/github/stars/Kietnehi?label=Stars&style=flat-square&logo=github"/>
  </a>
</p>


<h3>🛠 Tech Stack</h3>
<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=docker,python,react,nodejs,mongodb,git,fastapi,pytorch&theme=light" alt="My Skills"/>
  </a>
</p>

<br/>

<h3>🌟 AI Model Demos & Experiments</h3>
<p align="center">
  <a href="https://github.com/Kietnehi/n8n_quick_tunnels">
    <img src="https://img.shields.io/github/stars/Kietnehi/n8n_quick_tunnels?style=for-the-badge&color=yellow" alt="Stars"/>
    <img src="https://img.shields.io/github/forks/Kietnehi/n8n_quick_tunnels?style=for-the-badge&color=orange" alt="Forks"/>
    <img src="https://img.shields.io/github/issues/Kietnehi/n8n_quick_tunnels?style=for-the-badge&color=red" alt="Issues"/>
  </a>
</p>

<p align="center">
  <img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=dark" alt="Daily Quote"/>
</p>
<p align="center">
<i>Thank you for stopping by! Don’t forget to give this repo a <b>⭐️ Star</b> if you find it useful.</i>
</p>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=80&section=footer"/>

</div>

---