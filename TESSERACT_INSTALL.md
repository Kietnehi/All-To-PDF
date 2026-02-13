# 🔍 Tesseract OCR Installation Guide

## Why Install Tesseract?

Installing Tesseract unlocks **full power** of the Unstructured extraction method:

| Feature | Without Tesseract | With Tesseract |
|---------|-------------------|----------------|
| **Text Extraction** | ✅ Basic | ✅ Advanced |
| **Tables** | ⚠️ Limited | ✅ Full Structure (HTML) |
| **Images** | ❌ Few/None | ✅ All Extracted |
| **Layout Detection** | ⚠️ Auto Strategy | ✅ Hi-Res YOLOX Model |

---

## 🪟 Windows Installation (5 minutes)

### Step 1: Download Tesseract

Visit: **https://github.com/UB-Mannheim/tesseract/wiki**

Click on the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.exe`)

### Step 2: Install

1. Run the downloaded `.exe` file
2. **Important**: Note the installation path (default: `C:\Program Files\Tesseract-OCR`)
3. Complete the installation

### Step 3: Add to PATH

**Method A: Automatic (Recommended)**
1. Press `Win + X` → Select "System"
2. Click "Advanced system settings" → "Environment Variables"
3. Under "System variables", find and select "Path" → Click "Edit"
4. Click "New" → Add: `C:\Program Files\Tesseract-OCR`
5. Click "OK" on all windows

**Method B: PowerShell (Quick)**
```powershell
# Run as Administrator
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Tesseract-OCR", "Machine")
```

### Step 4: Verify Installation

Open a **NEW** terminal (important!) and run:

```bash
tesseract --version
```

You should see:
```
tesseract 5.3.3
 leptonica-1.83.0
```

✅ **Done!** Now restart your Python app and Unstructured will automatically use hi-res extraction.

---

## 🐧 Linux Installation (1 minute)

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install tesseract-ocr -y
tesseract --version
```

### CentOS/RHEL:
```bash
sudo yum install tesseract -y
tesseract --version
```

### Arch Linux:
```bash
sudo pacman -S tesseract
tesseract --version
```

---

## 🐳 Docker

Tesseract is **already included** in the Docker image. No action needed!

---

## 🧪 Testing in the App

1. **Restart** the Python app: `python app.py`
2. Go to "Extract from PDF" tab
3. Select **"Unstructured"** method
4. Upload a PDF

**Check the terminal logs:**

```
[✓] Tesseract OCR detected - using hi-res strategy
```

If you see this, Tesseract is working! 🎉

---

## ❓ Troubleshooting

### "Tesseract not found" after installation

**Solution 1:** Restart terminal/computer
- PATH changes require a fresh terminal session

**Solution 2:** Check installation path
```bash
# Windows - Find where Tesseract is installed
dir "C:\Program Files\Tesseract-OCR\tesseract.exe"

# Or search:
where tesseract
```

**Solution 3:** Manual PATH verification
1. Open new Command Prompt
2. Run: `echo %PATH%`
3. Verify `Tesseract-OCR` appears in the output

### Still not working?

Try absolute path in Windows:
```bash
"C:\Program Files\Tesseract-OCR\tesseract.exe" --version
```

If this works but `tesseract --version` doesn't, your PATH is not set correctly. Repeat Step 3.

---

## 💡 Pro Tips

1. **Language Packs**: For non-English PDFs, download additional language packs during installation
2. **Version**: Latest version (5.3+) works best with Unstructured
3. **Performance**: First run downloads YOLOX model (~217MB), subsequent runs are faster

---

## 📊 Comparison: With vs Without Tesseract

### Example: Scientific Paper (Attention Is All You Need)

**Without Tesseract (auto strategy):**
```
[!] Tesseract not found - using auto strategy
✅ Text: ~80% accuracy
⚠️  Tables: 0 extracted
❌ Images: 0 extracted
```

**With Tesseract (hi-res strategy):**
```
[✓] Tesseract OCR detected - using hi-res strategy
✅ Text: ~95% accuracy (structured)
✅ Tables: 3 extracted (HTML + CSV + Excel)
✅ Images: 7 figures extracted
```

---

## 🔄 Already Using Docling?

You don't **need** Tesseract if you're happy with Docling!

- **Docling**: Best for digital PDFs, no dependencies, fast
- **Unstructured + Tesseract**: Best for complex layouts, scanned documents, maximum extraction

Choose based on your needs! 🚀
