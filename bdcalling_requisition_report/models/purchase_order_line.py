from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_category_id = fields.Many2one(
        'product.category',
        string='Category'
    )

    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        """Filter products based on selected category"""
        # Clear the product field when category changes
        if self.product_category_id:
            self.product_id = False
            return {
                'domain': {
                    'product_id': [('categ_id', '=', self.product_category_id.id), ('purchase_ok', '=', True)]
                }
            }
        else:
            return {
                'domain': {
                    'product_id': [('purchase_ok', '=', True)]
                }
            }

    @api.onchange('product_id')
    def _onchange_product_id_category(self):
        """Auto-fill category when product is selected"""
        if self.product_id and self.product_id.categ_id:
            self.product_category_id = self.product_id.categ_id