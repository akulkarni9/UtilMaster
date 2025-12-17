from langchain_core.tools import BaseTool
from docx2pdf import convert
import os
import sys

class WordToPDFTool(BaseTool):
    name: str = "word_to_pdf_tool"
    description: str = "Converts a Word document (.docx) to PDF."

    def _run(self, file_path: str):
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found."
        
        # Strict validation: only accept .docx files
        if not file_path.lower().endswith('.docx'):
            return f"Error: This tool only converts Word documents (.docx). The file '{os.path.basename(file_path)}' appears to be a different format. Please use the appropriate tool for this file type."

        try:
            # Output path: same name, .pdf extension
            output_path = os.path.splitext(file_path)[0] + ".pdf"
            
            # Note: docx2pdf requires Microsoft Word installed on Mac/Windows
            # If running in a container or w/o Word, this will fail.
            convert(file_path, output_path)
            
            filename = os.path.basename(output_path)
            # Assuming server is running on localhost:8000
            download_url = f"http://localhost:8000/uploads/{filename}"
            
            return f"Success: Converted to PDF. [Download PDF]({download_url})"
        except Exception as e:
            return f"Error converting to PDF: {str(e)}. Ensure Microsoft Word is installed."

    def _arun(self, file_path: str):
        raise NotImplementedError("Async not implemented")
