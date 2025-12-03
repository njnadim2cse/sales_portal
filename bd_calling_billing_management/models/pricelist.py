from odoo import models, fields

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    tax_id = fields.Many2one(
            'account.tax',
            string='Default Tax',
            domain="[('type_tax_use', '=', 'sale')]",
            help="Default tax applied when using this pricelist"
        )