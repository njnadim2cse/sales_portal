from odoo import models, fields, api

class TaskManagement(models.Model):
    _name = "task.management"
    _description = "Task Management Model"
    _rec_name = "task_title"

    task_title = fields.Char(string="Task Title", required=True)

    # 1. Task Team
    task_team = fields.Selection(
        [('sales', 'Sales'), ('service', 'Service')],
        string="Task Team",
        required=True
    )

    # 2. Employee
    employee_id = fields.Many2one('hr.employee', string="Employee")

    # 3. Designation (STORE=True)
    designation = fields.Char(
        string="Designation",
        compute="_compute_designation",
        store=True,
        readonly=False
    )

    # 4. Customer
    customer_id = fields.Many2one('res.partner', string="Customer")

    # 5. Company (STORE=True)
    company_id = fields.Many2one(
        'res.partner',
        string="Company",
        compute="_compute_customer_fields",
        store=True,
        readonly=False
    )

    # 6. Job Position (STORE=True)
    job_position = fields.Char(
        string="Job Position",
        compute="_compute_customer_fields",
        store=True,
        readonly=False
    )

    analyzer = fields.Char(string="Analyzer")
    reagents = fields.Text(string="Reagents")
    remarks = fields.Text(string="Remarks")

    # ===== NEW FIELDS =====
    # Date field
    visit_date = fields.Date(string="Visit Date", default=fields.Date.context_today)
    
    # Time fields (changed to Text for manual entry)
    time_in_dt = fields.Char(string="Time IN")
    time_out_dt = fields.Char(string="Time Out")
    
    # Text fields
    tags = fields.Text(string="Tags")
    purpose_id = fields.Many2one('task.purpose', string="Purpose")
    
    # Warranty Type field
    warranty_type = fields.Selection(
        [('with_warranty', 'With Warranty'), ('without_warranty', 'Without Warranty')],
        string="Warranty Type"
    )

    # -----------------------------
    # FIX 1: Compute employee fields
    # -----------------------------
    @api.depends('employee_id')
    def _compute_designation(self):
        for rec in self:
            job_name = False

            if rec.employee_id:
                if rec.employee_id.job_id:
                    job_name = rec.employee_id.job_id.name
                elif getattr(rec.employee_id, "job_title", False):
                    job_name = rec.employee_id.job_title

            rec.designation = job_name or False

    # -----------------------------------
    # FIX 2: Compute customer fields
    # -----------------------------------
    @api.depends('customer_id')
    def _compute_customer_fields(self):
        for rec in self:
            if rec.customer_id:
                rec.company_id = rec.customer_id.parent_id
                rec.job_position = rec.customer_id.function
            else:
                rec.company_id = False
                rec.job_position = False