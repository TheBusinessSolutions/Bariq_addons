from odoo import models, fields

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    skip_quality_inspection = fields.Boolean(string="Skip Quality Inspection")
