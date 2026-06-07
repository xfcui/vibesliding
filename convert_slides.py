import os
import subprocess
import sys
import fitz

def run_applescript(script_content):
    """Run AppleScript and return the output or raise an exception on error."""
    process = subprocess.Popen(
        ['osascript', '-e', script_content],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"AppleScript error: {stderr.strip()}")
    return stdout.strip()

def convert_pptx_to_pdf(pptx_path, pdf_path):
    """Convert PPTX to PDF using Microsoft PowerPoint via AppleScript."""
    abs_pptx = os.path.abspath(pptx_path)
    abs_pdf = os.path.abspath(pdf_path)
    
    # Escape double quotes for AppleScript
    escaped_pptx = abs_pptx.replace('"', '\\"')
    escaped_pdf = abs_pdf.replace('"', '\\"')
    
    script = f'''
    tell application "Microsoft PowerPoint"
        try
            open POSIX file "{escaped_pptx}"
            set activePres to active presentation
            save activePres in POSIX file "{escaped_pdf}" as save as PDF
            close activePres saving no
        on error errMsg
            try
                close active presentation saving no
            end try
            error errMsg
        end try
    end tell
    '''
    print(f"Converting '{pptx_path}' to '{pdf_path}' via PowerPoint AppleScript...")
    run_applescript(script)
    print("PDF conversion completed successfully.")

def convert_pdf_to_images(pdf_path, output_dir):
    """Convert PDF pages to PNG images using PyMuPDF."""
    print(f"Converting PDF '{pdf_path}' to PNG images in '{output_dir}'...")
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    print(f"Total pages/slides to convert: {num_pages}")
    
    for i, page in enumerate(doc):
        # Using 150 DPI for high quality rendering
        pix = page.get_pixmap(dpi=150)
        # Format filename as slide_01.png, slide_02.png, etc.
        filename = f"slide_{i+1:02d}.png"
        filepath = os.path.join(output_dir, filename)
        pix.save(filepath)
        print(f"Saved: {filepath}")
        
    print(f"Successfully converted {num_pages} slides to PNG images.")

def main():
    pptx_path = "input/范文-联合基金2409.pptx"
    pdf_path = "input/temp.pdf"
    output_dir = "slides"
    
    if not os.path.exists(pptx_path) and not os.path.exists(pdf_path):
        print(f"Error: Neither input file '{pptx_path}' nor '{pdf_path}' exists.")
        sys.exit(1)
        
    try:
        # If temp.pdf does not exist, generate it from PPTX
        if not os.path.exists(pdf_path):
            convert_pptx_to_pdf(pptx_path, pdf_path)
        else:
            print(f"Using existing PDF file '{pdf_path}'.")
            
        convert_pdf_to_images(pdf_path, output_dir)
        
        # Do not clean up temporary PDF as requested by the user
        print(f"Keeping PDF file at '{pdf_path}' as requested.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
