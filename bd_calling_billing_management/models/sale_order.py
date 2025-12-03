import logging

from odoo import models, fields, api
_logger = logging.getLogger(__name__)

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

    # Add categ_id as a Many2one field to sale.order.line
    # categ_id = fields.Many2one(
    #     'product.category',
    #     string='Category',
    #     related='product_id.categ_id',
    #     store=True,
    #     readonly=True
    # )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_category_id = fields.Many2one(
        'product.category',
        string='Category'
    )
    # test_per_unit = fields.Float(string='Test Per Unit')
    # total_test = fields.Float(string='Total Test')
    # price_per_test = fields.Float(string='Price Per Test')
    test_per_unit = fields.Integer(
        string='Test per Unit',
        compute='_compute_test_per_unit',
        store=True
        
    )
    
    total_test = fields.Integer(
         string='Total Test',
       compute='_compute_total_test',
         store=True
    )
    
    price_per_test = fields.Float(
         string='Price per Test',
         compute='_compute_price_per_test',
         store=True,
         digits='Product Price'
     )
    @api.onchange('product_category_id')
    def _onchange_product_category_id(self):
        """Filter products based on selected category"""
        # Clear the product fields when category changes
        if self.product_category_id:
            self.product_id = False
            self.product_template_id = False
            return {
                'domain': {
                    'product_id': [('categ_id', '=', self.product_category_id.id)],
                    'product_template_id': [('categ_id', '=', self.product_category_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'product_id': [],
                    'product_template_id': []
                }
            }

    @api.onchange('product_id')
    def _onchange_product_id_category(self):
        """Auto-fill category when product is selected"""
        if self.product_id and self.product_id.categ_id:
            self.product_category_id = self.product_id.categ_id

    @api.onchange('product_template_id')
    def _onchange_product_template_id_category(self):
        """Auto-fill category when product template is selected"""
        if self.product_template_id and self.product_template_id.categ_id:
            self.product_category_id = self.product_template_id.categ_id



    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     """Auto-set category when product is selected"""
    #     if self.product_id and not self.categ_id:
    #         self.categ_id = self.product_id.categ_id
    #     return super()._onchange_product_id()
    
    @api.depends('product_id', 'product_id.test_count')
    def _compute_test_per_unit(self):
        for record in self:
            if record.product_id and record.product_id.test_count:
                record.test_per_unit = record.product_id.test_count
                _logger.info(f"Set test_per_unit to {record.test_per_unit} for product {record.product_id.name}")
            else:
                record.test_per_unit = 0
                _logger.info(f"No test_count found for product {record.product_id.name if record.product_id else 'None'}")
    
    @api.depends('product_uom_qty', 'test_per_unit')
    def _compute_total_test(self):
        for record in self:
            record.total_test = record.product_uom_qty * record.test_per_unit
    
    @api.depends('price_unit', 'test_per_unit')
    def _compute_price_per_test(self):
        for record in self:
            if record.test_per_unit and record.test_per_unit > 0:
                record.price_per_test = record.price_unit / record.test_per_unit
            else:
                record.price_per_test = 0
    
    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        _logger.info(f"Category changed to: {self.categ_id}")
        if self.categ_id:
            self.product_id = False
        domain = [('product_tmpl_id.categ_id', 'child_of', self.categ_id.id)] if self.categ_id else []
        return {'domain': {'product_id': domain}}
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            _logger.info(f"Product selected: {self.product_id.name}, Category: {self.product_id.categ_id}")
            _logger.info(f"Product test_count: {getattr(self.product_id, 'test_count', 'NOT FOUND')}")
            self.categ_id = self.product_id.categ_id
    @api.model
    def create(self, vals):
        """Apply pricelist tax when new lines are created"""
        line = super().create(vals)
        
        # Apply pricelist tax if available
        if line.order_id.pricelist_id and line.order_id.pricelist_id.tax_id:
            line.tax_ids = [(6, 0, [line.order_id.pricelist_id.tax_id.id])]
        
        return line
    
    def _prepare_invoice_line(self, **optional_values):
        """Copy test fields from sale order line to invoice line"""
        res = super()._prepare_invoice_line(**optional_values)
        res.update({
            'test_per_unit': self.test_per_unit,
            'total_test': self.total_test,
            'price_per_test': self.price_per_test,
        })
        return res
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Apply pricelist tax when product is selected"""
        if self.product_id and self.order_id.pricelist_id and self.order_id.pricelist_id.tax_id:
            self.tax_ids = [(6, 0, [self.order_id.pricelist_id.tax_id.id])]
            
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    custom_chalian_number = fields.Char(string='Chalian No.')  

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        """Apply pricelist tax to ALL order lines when pricelist is selected"""
        if self.pricelist_id and self.pricelist_id.tax_id:
            # Apply the tax to all existing order lines
            for line in self.order_line:
                line.tax_ids = [(6, 0, [self.pricelist_id.tax_id.id])]
    
    # Also apply tax when new lines are added
    def _create_order_line_from_ui(self, product, quantity, **kwargs):
        """Override to apply pricelist tax when adding lines from UI"""
        line = super()._create_order_line_from_ui(product, quantity, **kwargs)
        
        # Apply pricelist tax to the new line
        if self.pricelist_id and self.pricelist_id.tax_id:
            line.tax_ids = [(6, 0, [self.pricelist_id.tax_id.id])]
        
        return line
    
    def action_print_custom_quotation(self):
        """Print custom quotation without test data"""
        return self.env.ref('estate_report.action_report_custom_quotation').report_action(self)
    
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    # custom_chalian_number = fields.Char(string='Chalian No.')
    custom_chalian_number = fields.Char(
        string='Chalian No. (Delivery ID)',
        compute='_compute_chalian_number',
        store=True
    )
    # test_per_unit = fields.Integer(
    #     string='Test per Unit',
    #     related='sale_line_ids.test_per_unit',
    #     store=True,
    #     readonly=False
    # )
    
    # total_test = fields.Integer(
    #     string='Total Test',
    #     related='sale_line_ids.total_test',
    #     store=True,
    #     readonly=False
    # )
    
    # price_per_test = fields.Float(
    #     string='Price per Test',
    #     related='sale_line_ids.price_per_test',
    #     store=True,
    #     readonly=False,
    #     digits='Product Price'
    # )
    # @api.depends('invoice_origin')
    # def _compute_chalian_number(self):
    #     """Automatically get delivery ID from source document"""
    #     for invoice in self:
    #         chalian_number = False
    #         if invoice.invoice_origin:
    #             # Find delivery order linked to the source (sale order)
    #             delivery = self.env['stock.picking'].search([
    #                 ('origin', '=', invoice.invoice_origin),
    #                 ('picking_type_id.code', '=', 'outgoing')
    #             ], limit=1)
                
    #             if delivery:
    #                 chalian_number = delivery.name  # 'WH/OUT/00058'
            
    #         invoice.custom_chalian_number = chalian_number
    @api.depends('invoice_origin')
    def _compute_chalian_number(self):
        for invoice in self:
            delivery_ids = []
            if invoice.invoice_origin:
                deliveries = self.env['stock.picking'].search([
                    ('origin', '=', invoice.invoice_origin),
                    ('picking_type_id.code', '=', 'outgoing')
                ])
                delivery_ids = deliveries.mapped('name')
            
            invoice.custom_chalian_number = ', '.join(delivery_ids) if delivery_ids else False
    
    def action_print_custom_quotation(self):
        """Print custom quotation without test data"""
        return self.env.ref('estate_report.action_report_custom_quotation').report_action(self)
    
    def action_print_with_test(self):
        """Print standard format WITH test fields"""
        return self.env.ref('bd_calling_billing_management.action_report_with_test').report_action(self)
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    # test_per_unit = fields.Integer(string='Test per Unit')
    # total_test = fields.Integer(string='Total Test')
    # price_per_test = fields.Float(string='Price per Test', digits='Product Price')
    test_per_unit = fields.Integer(
        string='Test per Unit',
        related='sale_line_ids.test_per_unit',
        store=True,
        readonly=False
    )
    
    total_test = fields.Integer(
        string='Total Test',
        related='sale_line_ids.total_test',
        store=True,
        readonly=False
    )
    
    price_per_test = fields.Float(
        string='Price per Test',
        related='sale_line_ids.price_per_test',
        store=True,
        readonly=False,
        digits='Product Price'
    )