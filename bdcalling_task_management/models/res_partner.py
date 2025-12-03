# # bdcalling_task_management/models/res_partner.py
# from odoo import models, api

# class ResPartner(models.Model):
#     _inherit = "res.partner"

#     @api.model
#     def name_get(self):
#         """
#         Display:
#          - Person with parent company: "Person Name (Company)"
#          - Company: just the company name
#          - Person without company: Person name
#         """
#         # Use the default behaviour for fallback and performance where needed.
#         res = []
#         # prefetch parent names to reduce queries
#         parents = {p.id: p.name for p in self.mapped('parent_id')}
#         for partner in self:
#             name = partner.name or ''
#             # For persons (not companies) with a parent company, show "Person (Company)"
#             if not partner.is_company and partner.parent_id:
#                 parent_name = parents.get(partner.parent_id.id) or partner.parent_id.name or ''
#                 # guard against empty parent name
#                 if parent_name:
#                     name = f"{partner.name} ({parent_name})"
#                 else:
#                     name = partner.name
#             # Companies remain as their own names
#             res.append((partner.id, name))
#         return res
