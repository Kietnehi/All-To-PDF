import os
import shutil
import re
import asyncio
import uuid
import nest_asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# Windows-only import
if os.name == 'nt':
    try:
        import win32com.client
        import pythoncom
    except ImportError:
        pass

nest_asyncio.apply()

app = FastAPI()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory="templates")

def get_libreoffice_path():
    if os.name == 'nt':
        paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
        ]
        for p in paths:
            if os.path.exists(p): return p
        return None
    else:
        # Standard path for LibreOffice on Linux
        return shutil.which('libreoffice') or shutil.which('soffice')

async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 100;
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)

async def convert_web_to_pdf(url, output_path):
    print(f"[*] Converting URL: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=['--no-sandbox']) # Sandbox disabled for Docker
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await auto_scroll(page)
            await asyncio.sleep(2)
            await page.pdf(path=str(output_path), format="A4", print_background=True)
            await browser.close()
        return True
    except Exception as e:
        print(f"[X] Web Error: {e}")
        return False

def windows_office_to_pdf(input_path, output_path, ext):
    pythoncom.CoInitialize()
    try:
        input_path = str(Path(input_path).absolute())
        output_path = str(Path(output_path).absolute())
        if ext in ['.doc', '.docx']:
            word = win32com.client.DispatchEx("Word.Application")
            doc = word.Documents.Open(input_path)
            doc.SaveAs(output_path, FileFormat=17)
            doc.Close(); word.Quit()
            return True
        elif ext in ['.xls', '.xlsx']:
            excel = win32com.client.DispatchEx("Excel.Application")
            wb = excel.Workbooks.Open(input_path)
            wb.ExportAsFixedFormat(0, output_path)
            wb.Close(False); excel.Quit()
            return True
        elif ext in ['.ppt', '.pptx']:
            ppt = win32com.client.DispatchEx("PowerPoint.Application")
            pres = ppt.Presentations.Open(input_path, WithWindow=False)
            pres.SaveAs(output_path, 32)
            pres.Close(); ppt.Quit()
            return True
    except Exception as e: print(f"Office Error: {e}")
    finally: pythoncom.CoUninitialize()
    return False

async def convert_file_to_pdf(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)
    ext = input_path.suffix.lower()
    try:
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
            image = Image.open(input_path)
            if image.mode in ("RGBA", "P", "LA"): image = image.convert("RGB")
            image.save(output_path, "PDF", resolution=100.0)
            return True
        
        # Windows logic
        if os.name == 'nt':
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, windows_office_to_pdf, str(input_path), str(output_path), ext)
        
        # Linux/Docker logic (LibreOffice)
        else:
            libo = get_libreoffice_path()
            if not libo:
                print("[X] Error: LibreOffice not found in PATH")
                return False
            
            print(f"[*] Running LibreOffice: {libo} for {input_path}")
            process = await asyncio.create_subprocess_exec(
                libo, '--headless', '--convert-to', 'pdf', 
                str(input_path), '--outdir', str(OUTPUT_DIR),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if stdout: print(f"[LibO Out]: {stdout.decode()}")
            if stderr: print(f"[LibO Err]: {stderr.decode()}")

            gen = OUTPUT_DIR / (input_path.stem + ".pdf")
            if gen.exists():
                if gen != output_path:
                    if output_path.exists(): os.remove(output_path)
                    os.rename(gen, output_path)
                print(f"[V] Successfully converted to: {output_path}")
                return True
            else:
                print(f"[X] LibreOffice failed to generate PDF. Check logs above.")
                return False
    except Exception as e:
        print(f"System Error: {e}")
        return False

async def cleanup_files(input_p=None, output_p=None):
    await asyncio.sleep(60)
    try:
        if input_p and os.path.exists(input_p): os.remove(input_p)
        if output_p and os.path.exists(output_p): os.remove(output_p)
    except: pass

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert-url")
async def convert_url(background_tasks: BackgroundTasks, url: str = Form(...)):
    file_id = str(uuid.uuid4())
    output_path = OUTPUT_DIR / f"{file_id}.pdf"
    success = await convert_web_to_pdf(url, output_path)
    if success:
        background_tasks.add_task(cleanup_files, None, str(output_path))
        # Clean URL filename
        safe_filename = re.sub(r'[\\/*?:"<>|]', '_', url.split('//')[-1])[:50]
        if not safe_filename.endswith('.pdf'): safe_filename += '.pdf'
        return FileResponse(output_path, filename=safe_filename, media_type='application/pdf')
    raise HTTPException(status_code=500, detail="Conversion failed")

@app.post("/convert-file")
async def convert_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
    output_path = OUTPUT_DIR / f"{file_id}.pdf"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    success = await convert_file_to_pdf(str(input_path), str(output_path))
    background_tasks.add_task(cleanup_files, str(input_path), str(output_path))
    if success:
        # Clean original filename
        original_name = Path(file.filename).stem
        safe_name = re.sub(r'[\\/*?:"<>|]', '_', original_name)
        return FileResponse(output_path, filename=f"{safe_name}.pdf", media_type='application/pdf')
    raise HTTPException(status_code=500, detail="Conversion failed (Docker uses LibreOffice)")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
