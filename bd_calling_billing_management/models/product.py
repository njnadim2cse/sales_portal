from odoo import models, fields

class Product(models.Model):
    _inherit = 'product.template'
    test_count = fields.Integer('Test Count')
    
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    test_count = fields.Integer(
        string='Test Count',
        related='product_tmpl_id.test_count',
        readonly=True,
        store=True
    )