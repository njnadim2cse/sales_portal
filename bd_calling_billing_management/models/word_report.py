from odoo import models, api, _
from odoo.exceptions import UserError
import io
import base64
import logging

_logger = logging.getLogger(__name__)

class IrActionsReportWord(models.Model):
    _inherit = 'ir.actions.report'
    
    @api.model
    def _render_word(self, docids, data=None):
        """
        Render report as Word document
        This converts PDF to Word format
        """
        try:
            # Import pdf2docx
            from pdf2docx import Converter
            
            # First generate PDF using existing template
            pdf_content, _ = self._render_qweb_pdf(docids, data=data)
            
            # Convert PDF to Word
            pdf_file = io.BytesIO(pdf_content)
            docx_file = io.BytesIO()
            
            cv = Converter(pdf_file)
            cv.convert(docx_file)
            cv.close()
            
            return docx_file.getvalue()
            
        except ImportError:
            raise UserError(_(
                "PDF to Word converter not installed!\n"
                "Please run: pip install pdf2docx"
            ))
        except Exception as e:
            _logger.error("Word report generation failed: %s", str(e))
            raise
    
    def _render(self, report_ref, docids, data=None):
        """
        Override render method to handle 'word' report_type
        """
        report = self._get_report(report_ref)
        if report.report_type == 'word':
            word_content = report._render_word(docids, data=data)
            
            # Create filename
            filename = report.print_report_name
            if isinstance(filename, str) and "' + " in filename:
                # Evaluate the print_report_name like Odoo does
                docs = self.env[report.model].browse(docids)
                if docs:
                    filename = eval(filename, {'object': docs[0], 'time': time})
            
            if not filename:
                filename = report.name
            
            # Return Word content with headers
            return word_content, 'docx'
        
        return super()._render(report_ref, docids, data=data)