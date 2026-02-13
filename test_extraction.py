"""
Test script for PDF extraction feature
Works on Windows without requiring additional dependencies
"""

import requests
import os
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000"
TEST_PDF = "test_document.pdf"  # Replace with your PDF file path
OUTPUT_ZIP = "extracted_result.zip"

def test_extraction():
    """Test the PDF extraction endpoint"""
    
    # Check if server is running
    try:
        response = requests.get(API_URL)
        print("✓ Server is running")
    except requests.exceptions.ConnectionError:
        print("✗ Error: Server is not running!")
        print("  Please start the server with: python app.py")
        return
    
    # Check if test PDF exists
    if not os.path.exists(TEST_PDF):
        print(f"✗ Error: Test PDF not found: {TEST_PDF}")
        print(f"  Please place a PDF file in this directory or update TEST_PDF variable")
        return
    
    print(f"\n📄 Testing with: {TEST_PDF}")
    print(f"📦 File size: {os.path.getsize(TEST_PDF) / 1024:.2f} KB")
    
    # Make API request
    print("\n⏳ Uploading and extracting... (this may take 10-60 seconds)")
    
    try:
        with open(TEST_PDF, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{API_URL}/extract-pdf",
                files=files,
                timeout=120  # 2 minutes timeout
            )
        
        if response.ok:
            # Save ZIP file
            with open(OUTPUT_ZIP, 'wb') as out:
                out.write(response.content)
            
            # Get summary from headers
            summary = response.headers.get('X-Extraction-Summary', 'N/A')
            
            print("\n✅ EXTRACTION SUCCESSFUL!")
            print(f"\n📊 Summary: {summary}")
            print(f"\n💾 Result saved to: {OUTPUT_ZIP}")
            print(f"📦 ZIP size: {os.path.getsize(OUTPUT_ZIP) / 1024:.2f} KB")
            
            print("\n✨ Next steps:")
            print("  1. Extract the ZIP file")
            print("  2. Check 'summary.txt' for overview")
            print("  3. Open 'text/' folder for extracted text")
            print("  4. Open 'tables/' folder for CSV/Excel files")
            print("  5. Open 'images/' folder for extracted images")
            
        else:
            print(f"\n✗ EXTRACTION FAILED!")
            print(f"Status code: {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text
            print(f"Error: {error_detail}")
            
    except requests.exceptions.Timeout:
        print("\n✗ Request timeout! File might be too large or processing is slow.")
    except Exception as e:
        print(f"\n✗ Error: {e}")

def test_url_convert():
    """Quick test for URL to PDF conversion"""
    print("\n" + "="*60)
    print("Testing URL to PDF conversion...")
    print("="*60)
    
    test_url = "https://example.com"
    
    try:
        response = requests.post(
            f"{API_URL}/convert-url",
            data={'url': test_url},
            timeout=60
        )
        
        if response.ok:
            output_pdf = "test_url_output.pdf"
            with open(output_pdf, 'wb') as f:
                f.write(response.content)
            print(f"✅ URL conversion successful: {output_pdf}")
        else:
            print(f"✗ URL conversion failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("PDF EXTRACTION TEST")
    print("=" * 60)
    
    test_extraction()
    
    # Uncomment to test URL conversion too
    # test_url_convert()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
