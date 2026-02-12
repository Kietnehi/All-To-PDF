import os
import subprocess
import shutil
import re
import asyncio
import nest_asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

# Cho phép chạy vòng lặp lồng nhau (đặc biệt quan trọng cho Colab/Jupyter)
nest_asyncio.apply()

def get_libreoffice_path():
    """Tự động tìm đường dẫn LibreOffice tùy theo hệ điều hành"""
    if os.name == 'nt': # Windows
        paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
        ]
        for p in paths:
            if os.path.exists(p): return p
        return None
    else: # Linux/Mac
        return shutil.which('libreoffice')

async def auto_scroll(page):
    """Script điều khiển trình duyệt cuộn trang để kích hoạt tải ảnh (Lazy Load)"""
    print("--- Đang cuộn trang để tải toàn bộ hình ảnh... ---")
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 100; // Khoảng cách cuộn mỗi lần
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100); // Tốc độ cuộn (ms)
            });
        }
    """)

async def convert_web_to_pdf(url):
    """Chuyển URL sang PDF với tính năng Auto-scroll để không mất hình"""
    # Tạo tên file an toàn từ URL
    clean_name = re.sub(r'[\\/*?:"<>|]', '_', url.split('//')[-1])[:50]
    output_path = f"{clean_name}.pdf"
    
    print(f"\n[WEB -> PDF]: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # 1. Truy cập trang web (đợi cấu trúc chính tải xong)
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2. Cuộn trang để kích hoạt Lazy Loading ảnh
            await auto_scroll(page)
            
            # Đợi thêm 2 giây để các ảnh cuối cùng kịp render
            await asyncio.sleep(2)
            
            # 3. Xuất PDF khổ A4
            await page.pdf(path=output_path, format="A4", print_background=True)
            await browser.close()
        print(f"V THÀNH CÔNG: {output_path}")
    except Exception as e:
        print(f"X Lỗi xử lý Web: {e}")

async def convert_file_to_pdf(input_path):
    """Chuyển đổi file cục bộ (Word, Excel, PPT, Ảnh)"""
    input_path = os.path.abspath(input_path)
    ext = Path(input_path).suffix.lower()
    output_folder = os.path.dirname(input_path)
    output_path = str(Path(input_path).with_suffix(".pdf"))

    print(f"\n[FILE -> PDF]: {os.path.basename(input_path)}")

    try:
        # Xử lý Ảnh bằng Pillow
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
            image = Image.open(input_path)
            # Chuyển về RGB để PDF lưu được (xử lý cả ảnh PNG trong suốt)
            if image.mode in ("RGBA", "P", "LA"):
                image = image.convert("RGB")
            image.save(output_path, "PDF", resolution=100.0)
            print(f"V THÀNH CÔNG (Ảnh)")

        # Xử lý Văn bản bằng LibreOffice
        else:
            libo = get_libreoffice_path()
            if not libo:
                print("X LỖI: Không tìm thấy LibreOffice!")
                return

            process = await asyncio.create_subprocess_exec(
                libo, '--headless', '--convert-to', 'pdf', 
                input_path, '--outdir', output_folder,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            print(f"V THÀNH CÔNG (Document)")

    except Exception as e:
        print(f"X Lỗi hệ thống: {e}")

async def main():
    # DANH SÁCH THỬ NGHIỆM
    test_list = [
        # "https://vnexpress.net",
        # "https://www.google.com",
        "test_word.docx", 
        "test_excel.xlsx", 
        "test_ppt.pptx",
        "C:\\Users\\ADMIN\\Downloads\\05-containerization_report.docx",
        "hinh_anh.jpg"
    ]
    
    print("--- BẮT ĐẦU CHUYỂN ĐỔI VẠN NĂNG (BẢN FIX MẤT HÌNH) ---")
    for item in test_list:
        if item.startswith(('http://', 'https://')):
            await convert_web_to_pdf(item)
        elif os.path.exists(item):
            if Path(item).suffix.lower() == '.pdf':
                continue
            await convert_file_to_pdf(item)
        else:
            print(f"\n[!] Bỏ qua: {item} (Không tồn tại)")
            
    print("\n--- TẤT CẢ ĐÃ HOÀN TẤT ---")

# Chạy chương trình
if __name__ == "__main__":
    asyncio.run(main())