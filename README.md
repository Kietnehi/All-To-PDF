# 📄 All-to-PDF Converter (Multi-Platform)

A tool for converting Websites, Images, and Office Documents (Word, Excel, PPT) to high-quality PDF. Runs on both **Windows** and **Linux** (Native or Docker).

![Demo All To PDF](output.gif)

## 🌟 Key Features
- **Cross-Platform**: Automatically detects the OS to select the best conversion engine.
- **Windows Optimized**: Directly uses Microsoft Office (Word, Excel, PowerPoint) if available on the machine.
- **Linux/Docker Ready**: Integrates LibreOffice for server or container environments.
- **Website to PDF**: Auto-scrolls the page to handle lazy-loading images, ensuring no image is missing.
- **Web Interface**: Built with FastAPI & Bootstrap 5, supports drag-and-drop file upload and displays processing status.

---

## 📸 Screenshots

### 🌐 Web to PDF - Website to PDF Conversion Interface
An interface that allows users to enter any website URL to convert it to PDF. Supports auto-scrolling to load all content, including lazy-loaded images. The interface shows the processing progress and allows downloading the resulting PDF file.
![Web to PDF Interface](image/web_to_pdf.png)

### 📁 File to PDF - File to PDF Conversion Interface
A simple and intuitive drag-and-drop file interface. Supports converting multiple Office document formats such as Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx), and various image formats to high-quality PDF. Users can drag and drop or click to select the files for conversion.
![File to PDF Interface](image/file_to_pdf.png)

### 🐳 Docker Logs - Logs when running Docker
An illustration of the application startup process using Docker Compose. The container is automatically built with all necessary dependencies (Python, LibreOffice, Playwright, Chromium). Logs show the FastAPI server running and ready to accept requests on port 8000.
![Docker Logs](image/logs_docker.png)

---

## 🚀 Installation & Running Guide

### Method 1: Run with Docker (Recommended - Fastest)
You don't need to install Python or LibreOffice on your host machine. Docker will automatically package everything.
```bash
docker-compose up --build
```
Then access: `http://localhost:8000`

### Method 2: Run Natively on Machine

**1. Install Python Dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**2. System Requirements:**
- **Windows**: Microsoft Office installed is preferred. If not available, install LibreOffice.
- **Linux**: Install LibreOffice (`sudo apt install libreoffice`).

**3. Start the application:**
```bash
python app.py
```
Access: `http://localhost:8000`

---

## 🔍 OS-based Operating Mechanism

| Component | Windows (Native) | Linux / Docker |
| :--- | :--- | :--- |
| **Website** | Playwright (Chromium) | Playwright (Chromium) |
| **Office Docs** | **Microsoft Office** (via pywin32) | **LibreOffice** (soffice) |
| **Images** | Pillow (PIL) | Pillow (PIL) |

---

## 🛠 Project Structure
- `app.py`: FastAPI server & Intelligent conversion logic.
- `templates/index.html`: Web user interface.
- `Dockerfile` & `docker-compose.yml`: Containerization configuration.
- `uploads/` & `outputs/`: Temporary directories (automatically cleaned after 60 seconds).

---

## ⚠️ Important Notes
- **Browser**: If you encounter a missing browser error on the first run, execute `playwright install chromium`.
- **Cleanup**: The system automatically deletes uploaded files and resulting PDFs after 1 minute for security and storage efficiency.
- **Docker**: The Docker image comes with LibreOffice pre-installed, making it very convenient for deployment on Linux servers.

---

## 🔗 Author

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=120&section=header"/>

<p align="center">
  <a href="https://github.com/Kietnehi">
    <img src="https://github.com/Kietnehi.png" width="140" height="140" style="border-radius: 50%; border: 4px solid #A371F7;" alt="Avatar Truong Phu Kiet"/>
  </a>
</p>

<h3>🚀 Truong Phu Kiet</h3>

<a href="https://github.com/Kietnehi">
  <img src="https://readme-typing-svg.herokuapp.com?font=JetBrains+Mono&weight=500&size=22&pause=800&color=36BCF7&center=true&vCenter=true&width=500&lines=Welcome+to+my+GitHub!;I'm+an+AI+Lover;AI+Research+Enthusiast;Building+All+To+PDF" alt="Typing SVG" />
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

<h3>🌟 All To PDF Converter</h3>
<p align="center">
  <a href="https://github.com/Kietnehi/All-To-PDF">
    <img src="https://img.shields.io/github/stars/Kietnehi/All-To-PDF?style=for-the-badge&color=yellow" alt="Stars"/>
    <img src="https://img.shields.io/github/forks/Kietnehi/All-To-PDF?style=for-the-badge&color=orange" alt="Forks"/>
    <img src="https://img.shields.io/github/issues/Kietnehi/All-To-PDF?style=for-the-badge&color=red" alt="Issues"/>
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