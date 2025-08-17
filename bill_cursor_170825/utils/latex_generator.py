import os
import subprocess
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateError
import streamlit as st
from datetime import datetime

class LaTeXGenerator:
    """
    Utility class for generating LaTeX documents with Jinja2 templating.
    Handles template rendering and LaTeX compilation.
    """
    
    def __init__(self):
        self.template_dir = "templates/latex"
        self.output_dir = "rendered_latex"
        
        # LaTeX document templates mapping
        self.document_templates = {
            'first_page': 'first_page.tex',
            'deviation_statement': 'deviation_statement.tex',
            'note_sheet': 'note_sheet.tex', 
            'extra_items': 'extra_items.tex',
            'certificate_ii': 'certificate_ii.tex',
            'certificate_iii': 'certificate_iii.tex'
        }
        
        # Ensure template and output directories exist
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Jinja2 environment for LaTeX
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        
        # Add custom filters
        self.env.filters['rupees'] = self._format_rupees
        self.env.filters['date'] = self._format_date
    
    def _format_rupees(self, value: float) -> str:
        """Format number as Indian Rupees."""
        try:
            return f"₹{value:,.2f}"
        except (ValueError, TypeError):
            return f"₹0.00"
    
    def _format_date(self, date_str: str, fmt: str = "%Y-%m-%d") -> str:
        """Format date string to specified format."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime(fmt)
        except (ValueError, TypeError):
            return date_str or ""
    
    def _get_template_path(self, template_name: str) -> str:
        """Get the full path to a template file."""
        return os.path.join(self.template_dir, template_name)
    
    def _get_output_path(self, template_name: str) -> str:
        """Get the full path for the rendered output file."""
        return os.path.join(self.output_dir, template_name)
    
    def render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """
        Render a single LaTeX template with the provided data.
        
        Args:
            template_name: Name of the template file
            data: Dictionary containing template variables
            
        Returns:
            Rendered LaTeX content as string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(data=data)
        except TemplateError as e:
            st.error(f"Error rendering template {template_name}: {str(e)}")
            raise
    
    def render_all_templates(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Render all LaTeX templates with the provided data.
        
        Args:
            data: Dictionary containing template variables
            
        Returns:
            Dictionary mapping template names to their rendered content
        """
        rendered = {}
        for name, template_file in self.document_templates.items():
            try:
                if not os.path.exists(self._get_template_path(template_file)):
                    st.warning(f"Template {template_file} not found, skipping...")
                    continue
                    
                content = self.render_template(template_file, data)
                output_path = self._get_output_path(template_file)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                rendered[name] = output_path
                st.success(f"Rendered {template_file}")
                
            except Exception as e:
                st.error(f"Failed to render {template_file}: {str(e)}")
                continue
                
        return rendered
    
    def compile_latex(self, tex_file: str) -> Optional[str]:
        """
        Compile a LaTeX file to PDF using xelatex.
        
        Args:
            tex_file: Path to the .tex file to compile
            
        Returns:
            Path to the generated PDF if successful, None otherwise
        """
        try:
            # Run xelatex twice to resolve references
            for _ in range(2):
                result = subprocess.run(
                    ['xelatex', '-interaction=nonstopmode', tex_file],
                    cwd=os.path.dirname(tex_file),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode != 0:
                    st.error(f"LaTeX compilation failed for {os.path.basename(tex_file)}:")
                    st.text(result.stderr)
                    return None
            
            pdf_file = os.path.splitext(tex_file)[0] + '.pdf'
            return pdf_file if os.path.exists(pdf_file) else None
            
        except Exception as e:
            st.error(f"Error compiling LaTeX: {str(e)}")
            return None
    
    def process_all_documents(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Process all LaTeX documents: render templates and compile to PDF.
        
        Args:
            data: Dictionary containing template variables
            
        Returns:
            Dictionary mapping document names to their PDF paths
        """
        pdf_paths = {}
        
        # First render all templates
        rendered_files = self.render_all_templates(data)
        
        # Then compile each rendered template
        for name, tex_file in rendered_files.items():
            pdf_path = self.compile_latex(tex_file)
            if pdf_path:
                pdf_paths[name] = pdf_path
        
        return pdf_paths
