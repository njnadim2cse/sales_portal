from odoo import models, api
import base64

class ReportService(models.AbstractModel):
    _name = 'report.service.word'
    _description = 'Word Report Service'
    
    @api.model
    def get_word_report_action(self, report_name, docids):
        """
        Return action to download Word report
        """
        report = self.env['ir.actions.report']._get_report_from_name(report_name)
        
        # Generate Word content
        word_content = report._render_word(docids)
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"{report.name}.docx",
            'datas': base64.b64encode(word_content),
            'res_model': report.model,
            'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        })
        
        # Return download URL
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }