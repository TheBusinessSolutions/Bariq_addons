from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines



# Adds a new boolean field to the model, 
# allowing users to indicate whether quality inspection 
# should be skipped for a specific bill of materials (BOM).
class MrpBom(models.Model):
    _inherit = "mrp.bom"

    skip_quality_inspection = fields.Boolean(string="Skip Quality Inspection")