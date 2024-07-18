from odoo import models


class bulk_cancel_picking(models.TransientModel):
    _name = "bulk.cancel.picking"
    _description = "Bulk Cancel Picking"

    def bulk_cancel_picking(self):
        model = self._context.get('active_model')
        model_ids = self.env[model].browse(self._context.get('active_ids'))
        for model_id in model_ids:
            if model in ["sale.order", "stock.picking"]:
                model_id.action_cancel()
            if model in ["purchase.order", "account.move"]:
                model_id.button_cancel()
