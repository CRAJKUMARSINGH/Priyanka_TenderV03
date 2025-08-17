import os
import subprocess
from typing import Dict, Optional, Tuple, Union, BinaryIO
import tempfile
import weasyprint
from weasyprint.text.fonts import FontConfiguration
import streamlit as st

class PDFMerger:
    """
    Utility class for converting HTML and LaTeX documents to PDF format.
    Handles both HTML-to-PDF and LaTeX-to-PDF conversion with proper error handling.
    """
    
    def __init__(self):
        # Check for available PDF generation tools
        self.weasyprint_available = self._check_weasyprint()
        self.latex_available = self._check_latex()
        
        # Configure WeasyPrint with better defaults
        self.weasyprint_config = {
            'encoding': 'utf-8',
            'image_dpi': 300,
            'optimize_size': ('fonts', 'images'),
            'font_config': FontConfiguration()
        }
    
    def _check_weasyprint(self) -> bool:
        """Check if WeasyPrint is available and properly configured."""
        try:
            import weasyprint
            # Try a simple test render
            weasyprint.HTML(string='<html><body>Test</body></html>').write_pdf(
                target=None, **self.weasyprint_config)
            return True
        except Exception as e:
            st.warning(f"WeasyPrint initialization warning: {str(e)}")
            return False
    
    def _check_latex(self) -> bool:
        """Check if LaTeX is installed and working."""
        try:
            # Try running pdflatex with --version
            result = subprocess.run(
                ['pdflatex', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,,
                hel=T# Add dtfsnWws combdy
    Args:
        html_docs: Dictionary with document names as keys and HTML content as values
        
    Returns:
            Dictionary with document names as keys and PDF bytes as values
        """
        pdf_docs = {}
        
        if not self.weasyprint_available:
            st.error("""
            ❌ WeasyPrint is not available for HTML to PDF conversion.
            Please install it with: pip install weasyprint
            """)
            return {}
        
        try:
            for doc_name, html_content in html_docs.items():
                try:
                    # Create a temporary file for the HTML content
                    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w', encoding='utf-8') as f:
                        f.write(html_content)
                        html_path = f.name
                    
                    try:
                            filename=html_path,
                            encoding='utf-8'
                        ).write_pdf(**self.weasyprint_config)
                        
                        pdf_docs[doc_name] = pdf_bytes
                        st.success(f"✅ Generated PDF from {doc_name}.html")
                        
                    except Exception as e:
                        st.error(f"❌ Error converting {doc_name} to PDF: {str(e)}")
                        # Create an error PDF
                        error_pdf = self._create_error_pdf(f"Error generating {doc_name}", str(e))
                        pdf_docs[f"{doc_name}_error"] = error_pdf
                        
                except Exception as e:
                    st.error(f"❌ Error processing {doc_name}: {str(e)}")
                    continue
                    
                finally:
                    # Clean up temporary file
                    try:
                        if os.path.exists(html_path):
                            os.unlink(html_path)
                    except Exception:
                        pass
            
            return pdf_docs
            
        except Exception as e:
            st.error(f"❌ Fatal error in HTML to PDF conversion: {str(e)}")
            return {}
    
    def convert_latex_to_pdf(self, latex_docs: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert LaTeX documents to PDF using pdflatex/xelatex.
        
        Args:
            latex_docs: Dictionary with document names as keys and LaTeX content as values
            
        Returns:
            Dictionary with document names as keys and PDF bytes as values
        """
        if not self.latex_available:
            st.warning("""
            ⚠️ LaTeX is not available for PDF generation.
            Please install a TeX distribution like MiKTeX or TeX Live.
            """)
            return {}
        
        pdf_docs = {}
        temp_dir = tempfile.mkdtemp()
        
        try:
            for doc_name, latex_content in latex_docs.items():
                try:
                    # Create a temporary .tex file
                    tex_filename = os.path.join(temp_dir, f"{doc_name}.tex")
                    with open(tex_filename, 'w', encoding='utf-8') as f:
                        f.write(latex_content)
                    
                    # Run LaTeX compilation
                    result = subprocess.run(
                        ['pdflatex', '-interaction=nonstopmode', tex_filename],
                        cwd=temp_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True  # Added for Windows compatibility
                    )
                    
                    if result.returncode != 0:
                        st.error(f"❌ LaTeX compilation failed for {doc_name}:")
                        st.text(result.stderr)
                        continue
                    
                    # Read the generated PDF
                    pdf_filename = os.path.join(temp_dir, f"{doc_name}.pdf")
                    if os.pa=True,
                        shellth.ee  # Addxd for Windows compatibilityists(pdf_filename):
                        with open(pdf_filename, 'rb') as f:
                            pdf_docs[doc_name] = f.read()
                        st.success(f"✅ Generated PDF from {doc_name}.tex")
                    else:
                        st.error(f"❌ PDF not generated for {doc_name}")
                        
                except Exception as e:
                    st.error(f"❌ Error processing {doc_name}: {str(e)}")
                    continue
            
            return pdf_docs
            
        except Exception as e:
            st.error(f"❌ Fatal error in LaTeX to PDF conversion: {str(e)}")
            return {}
            
        finally:
            # Clean up temporary files
            try:
                for f in os.listdir(temp_dir):
                    os.unlink(os.path.join(temp_dir, f))
                os.rmdir(temp_dir)
            except Exception:
                pass
    
    def _create_error_pdf(self, title: str, message: str) -> bytes:
        """Create a PDF with an error message."""
        html = f"""
        <html>
            <head>
                <title>Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; }}
                    h1 {{ color: #d32f2f; }}
                    pre {{ 
                        background: #f5f5f5; 
                        padding: 15px; 
                        border-radius: 4px;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                    }}
                </style>
            </head>
            <body>
                <h1>{title}</h1>
                <p>An error occurred while generating this document:</p>
                <pre>{message}</pre>
            </body>
        </html>
        """
        
        try:
            return weasyprint.HTML(string=html).write_pdf(**self.weasyprint_config)
        except Exception:
            # Fallback to a minimal PDF if WeasyPrint fails
            try:
                import io
                from reportlab.pdfgen import canvas
                
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer)
                p.drawString(100, 700, f"Error: {title}")
                
                # Handle long messages by splitting into lines
                y = 680
                for line in message.split('\n'):
                    if y < 50:  # New page if we're near the bottom
                        p.showPage()
                        y = 750
                    p.drawString(100, y, line)
                    y -= 15
                
                p.save()
                buffer.seek(0)
                return buffer.read()
                
            except Exception:
                # Return an empty PDF as last resort
                return b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 612 792]/Contents 5 0 R>>endobj 4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica/Encoding/WinAnsiEncoding>>endobj 5 0 obj<</Length 44>>stream BT/F1 12 Tf 50 700 Td(Error generating PDF) Tj ET endstream endobj xref 0 6 0000000000 65535 f 0000000015 00000 n 0000000069 00000 n 0000000119 00000 n 0000000223 00000 n 0000000346 00000 n trailer <</Size 6/Root 1 0 R>> startxref 595 %%EOF'
