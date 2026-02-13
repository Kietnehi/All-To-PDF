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
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
import zipfile
import httpx

# Unstructured imports (optional, will check if available)
try:
    from unstructured.partition.pdf import partition_pdf
    import pytesseract
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    pytesseract = None
    print("[!] Unstructured library not available. Install with: pip install unstructured[all-docs]")

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
EXTRACTED_DIR = Path("extracted")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
EXTRACTED_DIR.mkdir(exist_ok=True)

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
        # Check if URL is a direct PDF file
        if url.lower().endswith('.pdf') or '/pdf/' in url.lower():
            print(f"[*] Detected PDF URL, downloading directly...")
            async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Check content type to confirm it's a PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"[V] PDF downloaded successfully to {output_path}")
                    return True
                else:
                    print(f"[!] URL doesn't return PDF content, falling back to browser rendering...")
        
        # Regular webpage to PDF conversion
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

def extract_from_pdf(pdf_path, extract_id):
    """
    Extract text, tables, and images from PDF using docling.
    Works on Windows without requiring poppler/tesseract installation.
    """
    try:
        pdf_path = Path(pdf_path)
        output_base = EXTRACTED_DIR / extract_id
        output_base.mkdir(exist_ok=True)
        
        # Setup directories
        text_dir = output_base / "text"
        tables_dir = output_base / "tables"
        images_dir = output_base / "images"
        text_dir.mkdir(exist_ok=True)
        tables_dir.mkdir(exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        
        # Configure docling pipeline
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False  # Faster for digital PDFs
        pipeline_options.do_table_structure = True
        pipeline_options.generate_picture_images = True
        
        # Initialize converter
        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        
        print(f"[*] Extracting from: {pdf_path}")
        result = doc_converter.convert(str(pdf_path))
        doc = result.document
        
        # Extract text to markdown
        md_content = doc.export_to_markdown()
        text_file = text_dir / "extracted_text.md"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[✓] Text saved: {text_file}")
        
        # Extract text to plain text using export_to_text() method
        try:
            plain_text = doc.export_to_text()
        except AttributeError:
            # Fallback: derive plain text from markdown by removing markdown syntax
            plain_text = re.sub(r'[#*`\[\]()]', '', md_content)
        
        txt_file = text_dir / "extracted_text.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(plain_text)
        print(f"[✓] Plain text saved: {txt_file}")
        
        # Extract tables to CSV
        table_count = 0
        if hasattr(doc, 'tables') and doc.tables:
            for i, table in enumerate(doc.tables):
                try:
                    df = table.export_to_dataframe(doc)
                    if not df.empty:
                        csv_path = tables_dir / f"table_{i+1}.csv"
                        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
                        
                        # Also save as Excel for better viewing
                        excel_path = tables_dir / f"table_{i+1}.xlsx"
                        df.to_excel(excel_path, index=False, engine='openpyxl')
                        table_count += 1
                        print(f"[✓] Table {i+1} saved")
                except Exception as e:
                    print(f"[!] Error extracting table {i+1}: {e}")
        
        # Extract images
        image_count = 0
        if hasattr(doc, 'pictures') and doc.pictures:
            for i, picture in enumerate(doc.pictures):
                try:
                    image = picture.get_image(doc)
                    if image:
                        page_no = picture.prov[0].page_no if picture.prov else 0
                        img_filename = f"image_{i+1}_page_{page_no}.png"
                        img_path = images_dir / img_filename
                        image.save(img_path, "PNG")
                        image_count += 1
                        print(f"[✓] Image {i+1} saved")
                except Exception as e:
                    print(f"[!] Error extracting image {i+1}: {e}")
        
        # Create summary file
        summary = {
            "pdf_filename": pdf_path.name,
            "extracted_at": extract_id,
            "text_files": 2,
            "tables_count": table_count,
            "images_count": image_count,
            "output_structure": {
                "text": ["extracted_text.md", "extracted_text.txt"],
                "tables": [f"table_{i+1}.csv / .xlsx" for i in range(table_count)],
                "images": [f"image_{i+1}_page_X.png" for i in range(image_count)]
            }
        }
        
        summary_file = output_base / "summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("PDF EXTRACTION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Source PDF: {summary['pdf_filename']}\n")
            f.write(f"Extraction ID: {summary['extracted_at']}\n\n")
            f.write(f"📄 Text Files: {summary['text_files']}\n")
            f.write(f"📊 Tables Extracted: {summary['tables_count']}\n")
            f.write(f"🖼️  Images Extracted: {summary['images_count']}\n\n")
            f.write("Directory Structure:\n")
            f.write(f"  text/     -> Markdown & plain text\n")
            f.write(f"  tables/   -> CSV & Excel files\n")
            f.write(f"  images/   -> PNG images\n")
        
        print(f"[✓] Summary saved: {summary_file}")
        
        return {
            "success": True,
            "extract_id": extract_id,
            "summary": summary,
            "output_path": str(output_base)
        }
        
    except Exception as e:
        print(f"[✗] Extraction error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def extract_from_pdf_unstructured(pdf_path, extract_id):
    """
    Extract text, tables, and images from PDF using Unstructured library.
    Alternative to docling with different extraction capabilities.
    """
    if not UNSTRUCTURED_AVAILABLE:
        return {
            "success": False,
            "error": "Unstructured library not installed. Run: pip install unstructured[all-docs]"
        }
    
    try:
        pdf_path = Path(pdf_path)
        output_base = EXTRACTED_DIR / extract_id
        output_base.mkdir(exist_ok=True)
        
        # Setup directories
        text_dir = output_base / "text"
        tables_dir = output_base / "tables"
        images_dir = output_base / "images"
        text_dir.mkdir(exist_ok=True)
        tables_dir.mkdir(exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        
        print(f"[*] Extracting from: {pdf_path} (using Unstructured)")
        
        # Check if Tesseract is available
        tesseract_available = False
        tesseract_cmd = None
        try:
            import subprocess
            
            # Common Tesseract installation paths on Windows
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Tesseract-OCR\tesseract.exe",
                "tesseract"  # Try PATH
            ]
            
            # Try each possible path
            for path in possible_paths:
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, timeout=5, shell=False)
                    if result.returncode == 0:
                        tesseract_available = True
                        tesseract_cmd = path
                        print(f"[✓] Tesseract OCR detected at: {path}")
                        print(f"    Version: {result.stdout.decode().split()[1]}")
                        break
                except (FileNotFoundError, OSError):
                    continue
            
            if not tesseract_available:
                print("[!] Tesseract not found - using auto strategy (limited extraction)")
                print("[💡] Install Tesseract for full features: See TESSERACT_INSTALL.md")
        except Exception as e:
            print(f"[!] Error checking Tesseract: {e}")
            print("[!] Using auto strategy (limited extraction)")
        
        # Extract using unstructured
        try:
            if tesseract_available:
                # Set tesseract path for pytesseract (used by unstructured internally)
                if pytesseract and tesseract_cmd:
                    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
                    print(f"[*] Configured pytesseract with: {tesseract_cmd}")
                    
                    # Also set TESSDATA_PREFIX if needed
                    tessdata_dir = str(Path(tesseract_cmd).parent / 'tessdata')
                    if Path(tessdata_dir).exists():
                        os.environ['TESSDATA_PREFIX'] = tessdata_dir
                        print(f"[*] Set TESSDATA_PREFIX: {tessdata_dir}")
                
                # Full hi-res extraction with OCR support (like in notebook)
                elements = partition_pdf(
                    filename=str(pdf_path),
                    strategy="hi_res",
                    hi_res_model_name="yolox",
                    infer_table_structure=True,
                    extract_images_in_pdf=True,
                    extract_image_block_output_dir=str(images_dir),
                )
            else:
                # Use auto strategy without OCR for better results than fast
                elements = partition_pdf(
                    filename=str(pdf_path),
                    strategy="auto",  # Better than fast, works without OCR
                    infer_table_structure=True,
                    extract_images_in_pdf=True,
                    extract_image_block_output_dir=str(images_dir),
                )
        except Exception as e:
            print(f"[!] Primary extraction failed: {e}")
            print(f"[*] Trying basic strategy...")
            # Last resort: basic extraction
            elements = partition_pdf(
                filename=str(pdf_path),
                infer_table_structure=True,
            )
        
        # Extract text
        text_elements = [el for el in elements if el.category in ["Title", "NarrativeText", "ListItem", "Text"]]
        
        # Save as markdown-style
        md_content = []
        for el in elements:
            if el.category == "Title":
                md_content.append(f"# {el.text}\n")
            elif el.category == "NarrativeText":
                md_content.append(f"{el.text}\n")
            elif el.category == "ListItem":
                md_content.append(f"- {el.text}")
            elif el.category == "Text":
                md_content.append(f"{el.text}\n")
        
        md_text = "\n".join(md_content)
        text_file = text_dir / "extracted_text.md"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"[✓] Text saved: {text_file}")
        
        # Save as plain text
        plain_text = "\n\n".join([el.text for el in text_elements])
        txt_file = text_dir / "extracted_text.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(plain_text)
        print(f"[✓] Plain text saved: {txt_file}")
        
        # Extract tables
        table_elements = [el for el in elements if el.category == "Table"]
        table_count = 0
        
        for i, table in enumerate(table_elements):
            try:
                # Get HTML table structure
                if hasattr(table.metadata, 'text_as_html') and table.metadata.text_as_html:
                    html_content = table.metadata.text_as_html
                    
                    # Try to convert HTML to DataFrame
                    try:
                        import io
                        df = pd.read_html(io.StringIO(html_content))[0]
                        
                        if not df.empty:
                            csv_path = tables_dir / f"table_{i+1}.csv"
                            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
                            
                            # Also save as Excel
                            excel_path = tables_dir / f"table_{i+1}.xlsx"
                            df.to_excel(excel_path, index=False, engine='openpyxl')
                            
                            # Save HTML version too
                            html_path = tables_dir / f"table_{i+1}.html"
                            with open(html_path, "w", encoding="utf-8") as f:
                                f.write(html_content)
                            
                            table_count += 1
                            print(f"[✓] Table {i+1} saved (CSV, Excel, HTML)")
                    except Exception as e:
                        # If HTML parsing fails, save raw HTML only
                        html_path = tables_dir / f"table_{i+1}.html"
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(html_content)
                        table_count += 1
                        print(f"[✓] Table {i+1} saved (HTML only): {e}")
            except Exception as e:
                print(f"[!] Error extracting table {i+1}: {e}")
        
        # Count extracted images
        image_count = 0
        if images_dir.exists():
            image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg"))
            image_count = len(image_files)
            print(f"[✓] {image_count} images extracted")
        
        # Create summary
        extraction_strategy = "Hi-Res (with Tesseract)" if tesseract_available else "Auto (without Tesseract)"
        summary = {
            "pdf_filename": pdf_path.name,
            "extracted_at": extract_id,
            "extraction_method": "Unstructured",
            "strategy": extraction_strategy,
            "text_files": 2,
            "tables_count": table_count,
            "images_count": image_count,
            "output_structure": {
                "text": ["extracted_text.md", "extracted_text.txt"],
                "tables": [f"table_{i+1}.csv / .xlsx / .html" for i in range(table_count)],
                "images": f"{image_count} PNG/JPG files"
            }
        }
        
        summary_file = output_base / "summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("PDF EXTRACTION SUMMARY (Unstructured Method)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Source PDF: {summary['pdf_filename']}\n")
            f.write(f"Extraction ID: {summary['extracted_at']}\n")
            f.write(f"Method: {summary['extraction_method']}\n")
            f.write(f"Strategy: {summary['strategy']}\n\n")
            if not tesseract_available:
                f.write("⚠️  LIMITED EXTRACTION MODE\n")
                f.write("For better results, install Tesseract OCR:\n")
                f.write("See TESSERACT_INSTALL.md for instructions\n\n")
            f.write(f"📄 Text Files: {summary['text_files']}\n")
            f.write(f"📊 Tables Extracted: {summary['tables_count']}\n")
            f.write(f"🖼️  Images Extracted: {summary['images_count']}\n\n")
            f.write("Directory Structure:\n")
            f.write(f"  text/     -> Markdown & plain text\n")
            f.write(f"  tables/   -> CSV, Excel & HTML files\n")
            f.write(f"  images/   -> PNG/JPG images\n")
        
        print(f"[✓] Summary saved: {summary_file}")
        
        return {
            "success": True,
            "extract_id": extract_id,
            "summary": summary,
            "output_path": str(output_base)
        }
        
    except Exception as e:
        print(f"[✗] Extraction error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


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

@app.post("/extract-pdf")
async def extract_pdf(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    view_mode: str = Form("download"),
    method: str = Form("docling")
):
    """
    Extract text, tables, and images from uploaded PDF file.
    Returns either a ZIP file or JSON with extract_id for viewing.
    
    Parameters:
    - file: PDF file to extract
    - view_mode: "view" or "download"
    - method: "docling" or "unstructured" (extraction method)
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Check if unstructured method is requested but not available
    if method == "unstructured" and not UNSTRUCTURED_AVAILABLE:
        raise HTTPException(
            status_code=400, 
            detail="Unstructured library not installed. Please install with: pip install unstructured[all-docs]"
        )
    
    extract_id = str(uuid.uuid4())
    input_path = UPLOAD_DIR / f"{extract_id}_{file.filename}"
    
    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run extraction in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    
    # Choose extraction method
    if method == "unstructured":
        result = await loop.run_in_executor(None, extract_from_pdf_unstructured, str(input_path), extract_id)
    else:  # default to docling
        result = await loop.run_in_executor(None, extract_from_pdf, str(input_path), extract_id)
    
    if not result["success"]:
        background_tasks.add_task(cleanup_files, str(input_path))
        raise HTTPException(status_code=500, detail=f"Extraction failed: {result.get('error', 'Unknown error')}")
    
    # If view mode, return JSON with extract_id
    if view_mode == "view":
        # Schedule cleanup after 10 minutes for view mode
        async def cleanup_extraction():
            await asyncio.sleep(600)  # Keep for 10 minutes
            try:
                if input_path.exists():
                    os.remove(input_path)
            except Exception as e:
                print(f"Cleanup error: {e}")
        
        background_tasks.add_task(cleanup_extraction)
        
        return JSONResponse({
            "success": True,
            "extract_id": extract_id,
            "summary": result["summary"],
            "view_url": f"/view-extraction/{extract_id}"
        })
    
    # Otherwise, create and return ZIP file (original behavior)
    output_base = Path(result["output_path"])
    zip_filename = f"extracted_{extract_id}.zip"
    zip_path = EXTRACTED_DIR / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_base):
            for file_name in files:
                file_path = Path(root) / file_name
                arcname = file_path.relative_to(output_base)
                zipf.write(file_path, arcname)
    
    # Schedule cleanup
    async def cleanup_extraction():
        await asyncio.sleep(120)  # Keep for 2 minutes
        try:
            if input_path.exists():
                os.remove(input_path)
            if output_base.exists():
                shutil.rmtree(output_base)
            if zip_path.exists():
                os.remove(zip_path)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    background_tasks.add_task(cleanup_extraction)
    
    # Return ZIP file
    original_name = Path(file.filename).stem
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', original_name)
    return FileResponse(
        zip_path, 
        filename=f"{safe_name}_extracted.zip", 
        media_type='application/zip',
        headers={
            "X-Extraction-Summary": f"Text:2,Tables:{result['summary']['tables_count']},Images:{result['summary']['images_count']}"
        }
    )

@app.get("/extraction-info/{extract_id}")
async def get_extraction_info(extract_id: str):
    """Get information about an extraction result."""
    output_base = EXTRACTED_DIR / extract_id
    summary_file = output_base / "summary.txt"
    
    if not summary_file.exists():
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    with open(summary_file, "r", encoding="utf-8") as f:
        summary_text = f.read()
    
    return JSONResponse({
        "extract_id": extract_id,
        "summary": summary_text,
        "available": True
    })

@app.get("/view-extraction/{extract_id}", response_class=HTMLResponse)
async def view_extraction(request: Request, extract_id: str):
    """View extraction results in browser."""
    output_base = EXTRACTED_DIR / extract_id
    
    if not output_base.exists():
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    # Get summary info
    summary_file = output_base / "summary.txt"
    summary_text = ""
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_text = f.read()
    
    # List tables (CSV and HTML) and images
    tables_dir = output_base / "tables"
    images_dir = output_base / "images"
    
    tables = []
    if tables_dir.exists():
        # Get CSV files
        csv_files = sorted([f.name for f in tables_dir.glob("*.csv")])
        # Get HTML files only if no CSV with same base name exists
        html_files = sorted([f.name for f in tables_dir.glob("*.html")])
        
        # Combine, prioritize CSV over HTML for same table
        seen_bases = set()
        for csv in csv_files:
            tables.append(csv)
            seen_bases.add(csv.rsplit('.', 1)[0])
        
        for html in html_files:
            base = html.rsplit('.', 1)[0]
            if base not in seen_bases:
                tables.append(html)
    
    images = []
    if images_dir.exists():
        images = sorted([f.name for f in images_dir.glob("*.png")]) + \
                 sorted([f.name for f in images_dir.glob("*.jpg")]) + \
                 sorted([f.name for f in images_dir.glob("*.jpeg")])
    
    return templates.TemplateResponse("view_extraction.html", {
        "request": request,
        "extract_id": extract_id,
        "summary": summary_text,
        "tables": tables,
        "images": images
    })

@app.get("/get-extracted-text/{extract_id}")
async def get_extracted_text(extract_id: str, format: str = "md"):
    """Get extracted text in markdown or plain text format."""
    output_base = EXTRACTED_DIR / extract_id
    text_dir = output_base / "text"
    
    if format == "md":
        text_file = text_dir / "extracted_text.md"
    else:
        text_file = text_dir / "extracted_text.txt"
    
    if not text_file.exists():
        raise HTTPException(status_code=404, detail="Text file not found")
    
    with open(text_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    return JSONResponse({"content": content, "format": format})

@app.get("/serve-table/{extract_id}/{filename}")
async def serve_table(extract_id: str, filename: str):
    """Serve table CSV or HTML file."""
    output_base = EXTRACTED_DIR / extract_id
    table_file = output_base / "tables" / filename
    
    if not table_file.exists():
        raise HTTPException(status_code=404, detail="Table file not found")
    
    # Determine media type
    if filename.endswith('.html'):
        return FileResponse(table_file, media_type="text/html", filename=filename)
    elif filename.endswith('.csv'):
        return FileResponse(table_file, media_type="text/csv", filename=filename)
    else:
        return FileResponse(table_file, filename=filename)

@app.get("/serve-image/{extract_id}/{filename}")
async def serve_image(extract_id: str, filename: str):
    """Serve extracted image file."""
    output_base = EXTRACTED_DIR / extract_id
    image_file = output_base / "images" / filename
    
    if not image_file.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_file, media_type="image/png")

@app.get("/download-extraction-zip/{extract_id}")
async def download_extraction_zip(extract_id: str, background_tasks: BackgroundTasks):
    """Download extraction results as ZIP file."""
    output_base = EXTRACTED_DIR / extract_id
    
    if not output_base.exists():
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    # Create ZIP file
    zip_filename = f"extracted_{extract_id}.zip"
    zip_path = EXTRACTED_DIR / zip_filename
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_base):
            for file_name in files:
                file_path = Path(root) / file_name
                arcname = file_path.relative_to(output_base)
                zipf.write(file_path, arcname)
    
    # Schedule cleanup
    async def cleanup_zip():
        await asyncio.sleep(60)  # Keep for 1 minute
        try:
            if zip_path.exists():
                os.remove(zip_path)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    background_tasks.add_task(cleanup_zip)
    
    return FileResponse(
        zip_path,
        filename=f"extraction_{extract_id}.zip",
        media_type='application/zip'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
