import logging
from odoo import models, fields, api
from datetime import date
from datetime import datetime, timedelta, date
import pytz
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    lc_order_id = fields.Many2one('lc.order', string='LC Reference', readonly=True)
    
    # def button_confirm(self):
    #     # First confirm the PO
    #     result = super().button_confirm()
        
    #     # Create LC record after confirmation
    #     for order in self:
    #         if not order.lc_order_id:  # Only create if LC doesn't exist
    #             # Create LC
    #             lc = self.env['lc.order'].create({
    #                 'po_number': order.id,  # Changed: use order.id instead of order.name
    #                 'vendor_id': order.partner_id.id,
    #             })
                
    #             # Add lines from PO
    #             for line in order.order_line:
    #                 self.env['lc.order.line'].create({
    #                     'lc_order_id': lc.id,
    #                     'product_id': line.product_id.id,
    #                     'quantity': line.product_qty,
    #                     'unit_price': line.price_unit,
    #                     'po_line_id': line.id,
    #                     'product_category_id': line.product_category_id.id if line.product_category_id else False,
    #                 })
                
    #             # Link LC to PO
    #             order.lc_order_id = lc.id
        
    #     return result

class LCOrder(models.Model):
    _name = 'lc.order'
    _description = 'Letter of Credit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    name = fields.Char(string='LC Number', default='New')
    
   
    po_number = fields.Many2one('purchase.order', string='Work Order', readonly=True, tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', related='po_number.partner_id', store=True, tracking=True)
    pi_number = fields.Char(string='PI Number', tracking=True)  # REMOVED required=True
    bank_id = fields.Many2one('res.bank', string='Bank', tracking=True)  # REMOVED required=True
    pi_date = fields.Date(string='PI Date', default=fields.Date.today(), tracking=True)  # REMOVED required=True
    lc_opening_date = fields.Date(string='LC Opening Date', default=fields.Date.today(), tracking=True)  # REMOVED required=True
    
    lc_line_ids = fields.One2many('lc.order.line', 'lc_order_id', string='Products')
    payment_terms = fields.Many2one('lc.payment.term', string='Payment Terms', tracking=True)
    payment_term_line_ids = fields.One2many('lc.payment.term.line', 'lc_order_id', string='Payment Term Lines')
    # currency_id = fields.Many2one(
    #     'res.currency',
    #     string='Currency',
    #     default=lambda self: self.env.company.currency_id,
    #     required=True,
    #     tracking=True
    # )
    
    # active_currency_ids = fields.Many2many(
    #     'res.currency',
    #     compute='_compute_active_currencies',
    #     string='Active Currencies',
    #     store=False
    # )
    
    # # Update amount fields to use currency
    # total_amount = fields.Monetary(
    #     string='Total Amount',
    #     currency_field='currency_id',
    #     compute='_compute_total_amount',
    #     store=True
    # )
    
    # @api.depends('vendor_id', 'po_number')
    # def _compute_active_currencies(self):
    #     """Get active currencies to show at top of dropdown"""
    #     for record in self:
    #         # Get all active currencies
    #         active_currencies = self.env['res.currency'].search([
    #             ('active', '=', True)
    #         ], order='name')
            
    #         record.active_currency_ids = [(6, 0, active_currencies.ids)]
    
    # @api.depends('lc_line_ids.subtotal')
    # def _compute_total_amount(self):
    #     """Calculate total amount from LC lines"""
    #     for record in self:
    #         record.total_amount = sum(record.lc_line_ids.mapped('subtotal'))
    
   
    
  
    
    @api.onchange('payment_terms')
    def _onchange_payment_terms(self):
        """Auto-populate payment term lines when payment term is selected"""
        if self.payment_terms:
            # Clear existing lines
            self.payment_term_line_ids = [(5, 0, 0)]
            
            # Create new lines from the selected payment term's description lines
            lines = []
            for line in self.payment_terms.description_line_ids:
                lines.append((0, 0, {
                    'description': line.description,
                }))
            self.payment_term_line_ids = lines
        else:
            # Clear lines if no payment term is selected
            self.payment_term_line_ids = [(5, 0, 0)]
            
 
    @api.onchange('po_number')
    def _onchange_po_number(self):
        """Preview LC lines when PO is selected - for display only"""
        if self.po_number:
            # Clear existing lines
            self.lc_line_ids = [(5, 0, 0)]
            
            # Create preview lines from PO lines (not saved yet)
            lc_lines = []
            for po_line in self.po_number.order_line:
                # Only add lines with products
                if po_line.product_id:
                    lc_lines.append((0, 0, {
                        'product_id': po_line.product_id.id,
                        'quantity': po_line.product_qty,
                        'unit_price': po_line.price_unit,
                        'po_line_id': po_line.id,
                        'product_category_id': po_line.product_id.categ_id.id,
                    }))
            
            self.lc_line_ids = lc_lines
        else:
            # Clear lines if PO is removed
            self.lc_line_ids = [(5, 0, 0)]
    
    def write(self, vals):
        """Ensure lines are preserved when saving"""
        # Remove lc_line_ids to prevent unwanted modifications
        if 'lc_line_ids' in vals:
            vals.pop('lc_line_ids')
            
        result = super(LCOrder, self).write(vals)
        
        # If PO is changed, regenerate lines
        if 'po_number' in vals and vals['po_number']:
            # Delete all existing lines
            self.lc_line_ids.unlink()
            
            # Create new lines from PO
            po = self.env['purchase.order'].browse(vals['po_number'])
            for po_line in po.order_line:
                if po_line.product_id and po_line.product_qty > 0:
                    self.env['lc.order.line'].create({
                        'lc_order_id': self.id,
                        'product_id': po_line.product_id.id,
                        'quantity': po_line.product_qty,
                        'unit_price': po_line.price_unit,
                        'po_line_id': po_line.id,
                        'product_category_id': po_line.product_id.categ_id.id,
                    })
        
        return result
    
    @api.model
    def create(self, vals_list):
        """Create LC lines when creating new LC order"""
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        records_to_create = []
        for vals in vals_list:
            # Generate sequence number
            if vals.get('name', 'New') == 'New':
                # Search for previous LC records (not M/D/ records)
                last_record = self.search([('name', 'like', 'LC%')], order='id desc', limit=1)
                
                if last_record and last_record.name:
                    try:
                        # Extract the numeric part from LC00001, LC00002, etc.
                        # Remove "LC" prefix and get the number
                        seq_str = last_record.name[2:]  # Remove first 2 chars "LC"
                        last_seq = int(seq_str)
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                # Format with leading zeros (5 digits)
                vals['name'] = f"LC{str(next_seq).zfill(5)}"
            
            # Remove lc_line_ids from vals to prevent saving onchange lines
            if 'lc_line_ids' in vals:
                vals.pop('lc_line_ids')
            
            records_to_create.append(vals)
        
        # Create the records
        records = super(LCOrder, self).create(records_to_create)
        
        # Handle single record creation (for backward compatibility)
        if isinstance(records, models.Model):
            records = records
        
        # Create LC lines from PO if specified
        for record in records:
            if record.po_number:
                for po_line in record.po_number.order_line:
                    # Only create lines for products that exist and have quantity
                    if po_line.product_id and po_line.product_qty > 0:
                        self.env['lc.order.line'].create({
                            'lc_order_id': record.id,
                            'product_id': po_line.product_id.id,
                            'quantity': po_line.product_qty,
                            'unit_price': po_line.price_unit,
                            'po_line_id': po_line.id,
                            'product_category_id': po_line.product_id.categ_id.id,
                        })
        
        return records
class LCOrderLine(models.Model):
    _name = 'lc.order.line'
    _description = 'LC Line'
    
    lc_order_id = fields.Many2one('lc.order', string='LC Order', required=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True, required=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    unit_price = fields.Float(string='Unit Price',readonly=True)
    po_line_id = fields.Many2one('purchase.order.line', string='PO Line')
    product_category_id = fields.Many2one(
        'product.category',
        string='Category',
        store=True,
        readonly=True
        
    )
    @api.model_create_multi
    def create(self, vals_list):
        """Prevent creation of empty lines"""
        # Filter out lines without product_id
        filtered_vals = [vals for vals in vals_list if vals.get('product_id')]
        
        # If no valid lines, return empty recordset
        if not filtered_vals:
            return self.env['lc.order.line']
            
        return super(LCOrderLine, self).create(filtered_vals)
    


class LCPaymentTerm(models.Model):
    _name = 'lc.payment.term'
    _description = 'LC Payment Terms'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True)
    description_line_ids = fields.One2many('lc.payment.term.description', 'payment_term_id', string='Description Lines')  # FIXED: Changed to lc.payment.term.description


class LCPaymentTermDescription(models.Model):
    _name = 'lc.payment.term.description'
    _description = 'Payment Term Description Template'
    
    payment_term_id = fields.Many2one('lc.payment.term', string='Payment Term', required=True, ondelete='cascade')
    description = fields.Text(string='Description', required=True)


class LCPaymentTermLine(models.Model):
    _name = 'lc.payment.term.line'
    _description = 'Payment Term Line in LC Order'
    
    lc_order_id = fields.Many2one('lc.order', string='LC Order', required=True, ondelete='cascade')  # FIXED: Changed from payment_term_id to lc_order_id
    description = fields.Text(string='Description')
    
