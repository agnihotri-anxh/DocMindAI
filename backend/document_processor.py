import PyPDF2
import io

class DocumentProcessor:
    def extract_pdf_text(self, pdf_content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"Processing PDF with {len(pdf_reader.pages)} pages")
            
            text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {i+1} ---\n{page_text}\n"
                print(f"Extracted {len(page_text)} characters from page {i+1}")
            
            total_chars = len(text)
            print(f"Total extracted text: {total_chars} characters")
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return f"Error processing PDF: {str(e)}"

    def extract_txt_text(self, txt_content: bytes) -> str:
        try:
            text = txt_content.decode('utf-8')
            print(f"Extracted {len(text)} characters from TXT file")
            return text
        except Exception:
            try:
                text = txt_content.decode('latin-1', errors='ignore')
                print(f"Extracted {len(text)} characters from TXT file (latin-1 encoding)")
                return text
            except Exception as e:
                print(f"Error extracting TXT text: {str(e)}")
                return f"Error processing TXT file: {str(e)}" 