
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"
    lot_production_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number')
    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super()._prepare_inspection_header(object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == "mrp.production":
            res["qty"] = object_ref.product_qty
            res["lot_id"] = object_ref.lot_producing_id
        return res

    #the print action:
    def action_print_inspection_report(self):
        return self.env.ref('quality_control_mrp_oca.action_report_qc_inspection').report_action(self)
    @api.depends("object_id")
    def _compute_production_id(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == "stock.move":
                    inspection.production_id = inspection.object_id.production_id
                elif inspection.object_id._name == "mrp.production":
                    inspection.production_id = inspection.object_id

    @api.depends("object_id")
    def _compute_product_id(self):
        """Overriden for getting the product from a manufacturing order."""
        for inspection in self:
            super()._compute_product_id()
            if inspection.object_id and inspection.object_id._name == "mrp.production":
                inspection.product_id = inspection.object_id.product_id
                inspection.lot_id = inspection.object_id.lot_producing_id
                inspection.qty = inspection.object_id.product_qty

    def object_selection_values(self):
        objects = super().object_selection_values()
        objects.append(("mrp.production", "Manufacturing Order"))
        return objects

    production_id = fields.Many2one(
        comodel_name="mrp.production", compute="_compute_production_id", store=True
    )


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        related="inspection_id.production_id",
        store=True,
        string="Production order",
    )
