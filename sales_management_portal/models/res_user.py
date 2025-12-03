from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    use_contact_portal = fields.Boolean(string='Access Contact Portal', default=False)
    use_quotation_portal = fields.Boolean(string='Access Quotation Portal', default=False)
    use_service_portal = fields.Boolean(string='Access Service Portal', default=False)
    use_sales_portal = fields.Boolean(string='Access Sales Portal', default=False)