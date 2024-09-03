#this file containe a generate inspection
#if the mo is confirmed generate inspection
#don't colse the MO is the inspection not done
from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.quality_control_oca.models.qc_trigger_line import _filter_trigger_lines




class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends("qc_inspections_ids")
    def _compute_created_inspections(self):
        for production in self:
            production.created_inspections = len(production.qc_inspections_ids)

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="production_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this production.",
    )
    created_inspections = fields.Integer(
        compute="_compute_created_inspections", string="Created inspections"
    )

    def _post_inventory(self, cancel_backorder=False):
        done_moves = self.mapped("move_finished_ids").filtered(
            lambda r: r.state == "done"
        )
        res = super()._post_inventory(cancel_backorder=cancel_backorder)
        # Commenting out inspection creation for 'done' state
        # inspection_model = self.env["qc.inspection"]
        # new_done_moves = (
        #     self.mapped("move_finished_ids").filtered(lambda r: r.state == "done")
        #     - done_moves
        # )
        # if new_done_moves:
        #     qc_trigger = self.env.ref("quality_control_mrp_oca.qc_trigger_mrp")
        #     for move in new_done_moves:
        #         trigger_lines = set()
        #         for model in [
        #             "qc.trigger.product_category_line",
        #             "qc.trigger.product_template_line",
        #             "qc.trigger.product_line",
        #         ]:
        #             trigger_lines = trigger_lines.union(
        #                 self.env[model].get_trigger_line_for_product(
        #                     qc_trigger, move.product_id
        #                 )
        #             )
        #         for trigger_line in _filter_trigger_lines(trigger_lines):
        #             inspection_model._make_inspection(move, trigger_line)
        return res

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'done':
            for production in self:
                product_tracking = production.product_id.tracking
                inspections = production.qc_inspections_ids.filtered(
                    lambda i: i.state in ('draft', 'ready', 'waiting')
                )
                
                #check first if the order is marked to skip inspection, then skip the error
                
                if not production.skip_quality_inspection:

                #check if the product has a tracking and if there are no inspections
                 #stop mark the MO as done
                    if product_tracking != 'none' and not production.qc_inspections_ids:
                        raise UserError(
                            "You cannot mark the MO as done because no inspection test has been created for the product with tracking."
                        )
                    #check if there are inspections in the MO but the state is not done
                    #stop mark the MO as done                if inspections:
                        raise UserError(
                            "You cannot mark the MO as done because there are inspection tests in draft, ready, or waiting state."
                        )
        res = super(MrpProduction, self).write(vals)
        # if 'state' in vals and vals['state'] == 'confirmed':
        if 'state' in vals and vals['state'] == 'progress':
            self._generate_confirmed_inspections()
        return res

    def _generate_confirmed_inspections(self):
        inspection_model = self.env["qc.inspection"]
        qc_trigger = self.env.ref("quality_control_mrp_oca.qc_trigger_mrp")
        for production in self:
            # for move in production.move_finished_ids.filtered(lambda r: r.state == 'confirmed'):
            for move in production.move_finished_ids.filtered(lambda r: r.state == 'confirmed'):
                trigger_lines = set()
                for model in [
                    "qc.trigger.product_category_line",
                    "qc.trigger.product_template_line",
                    "qc.trigger.product_line",
                ]:
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, move.product_id
                        )
                    )
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_model._make_inspection(move, trigger_line)
