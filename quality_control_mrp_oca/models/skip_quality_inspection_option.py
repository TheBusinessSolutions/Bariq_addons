from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    skip_quality_inspection = fields.Boolean(string="Skip Quality Inspection")

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    skip_quality_inspection = fields.Boolean(string='Skip Quality Inspection')

    @api.model
    def create(self, vals):
        if 'bom_id' in vals:
            bom = self.env['mrp.bom'].browse(vals['bom_id'])
            vals['skip_quality_inspection'] = bom.skip_quality_inspection
        return super(MrpProduction, self).create(vals)
