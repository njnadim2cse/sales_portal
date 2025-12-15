from odoo import models, fields, api


class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'
    
    product_category_id = fields.Many2one(
        'product.category',
        string='Category'
    )

    incoming_qty = fields.Float(
        string='Incoming Qty',
        compute='_compute_product_quantities',
        store=False,
        help='Incoming quantity from product.product'
    )
    
    outgoing_qty = fields.Float(
        string='Outgoing Qty',
        compute='_compute_product_quantities',
        store=False,
        help='Outgoing quantity from product.product'
    )
    total_qty=  fields.Float(
        string='Total Qty',
        compute='_compute_product_quantities',
        store=False,
        help='Outgoing quantity from product.product'
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
    
    @api.depends('product_id')
    def _compute_product_quantities(self):
        """Compute incoming and outgoing quantities from product"""
        for line in self:
            if line.product_id:
                line.incoming_qty = line.product_id.incoming_qty
                line.outgoing_qty = line.product_id.outgoing_qty
                line.total_qty = line.product_id.qty_available
            else:
                line.incoming_qty = 0.0
                line.outgoing_qty = 0.0
                line.total_qty = 0.0