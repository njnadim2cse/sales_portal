from odoo import models, fields

class TaskPurpose(models.Model):
    _name = "task.purpose"
    _description = "Task Purpose"
    _rec_name = "name"

    name = fields.Char(string="Purpose Name", required=True)