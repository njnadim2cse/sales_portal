# models/ir_actions_report.py
from odoo import models, fields

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    is_docx_report = fields.Boolean(string="DOCX Report", default=False)
