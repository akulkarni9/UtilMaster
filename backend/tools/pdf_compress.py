from langchain_core.tools import BaseTool
from pydantic import Field
from pypdf import PdfReader, PdfWriter
import os

class PDFCompressTool(BaseTool):
    name: str = "pdf_compress_tool"
    description: str = "Compresses a PDF file by removing duplication and optimizing images (basic)."

    def _run(self, file_path: str):
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found."
        
        # Strict validation: only accept PDF files
        if not file_path.lower().endswith('.pdf'):
            return f"Error: This tool only compresses PDF files. The file '{os.path.basename(file_path)}' is not a PDF. Please convert it to PDF first if needed."

        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()

            # Add all pages to writer first
            for page in reader.pages:
                writer.add_page(page)
            
            # Compress the entire PDF in writer
            for page in writer.pages:
                page.compress_content_streams()
            
            # Simple metadata optimization
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            output_path = os.path.splitext(file_path)[0] + "_compressed.pdf"
            
            with open(output_path, "wb") as f:
                writer.write(f)
                
            original_size = os.path.getsize(file_path)
            new_size = os.path.getsize(output_path)
            reduction = ((original_size - new_size) / original_size) * 100
            
            filename = os.path.basename(output_path)
            # Assuming server is running on localhost:8000
            download_url = f"http://localhost:8000/uploads/{filename}"
            
            return f"Success: Compressed. Size reduced by {reduction:.1f}%. [Download Compressed PDF]({download_url})"
        except Exception as e:
            return f"Error compressing PDF: {str(e)}"

    def _arun(self, file_path: str):
        raise NotImplementedError("Async not implemented")
