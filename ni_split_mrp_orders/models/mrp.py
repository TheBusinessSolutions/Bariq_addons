from odoo import fields, models, api, _


class Mrp(models.Model):
    _inherit = "mrp.production"

    product_qty = fields.Float(
        'Quantity To Produce',
        default=1.0, digits='Product Unit of Measure',
        readonly=True, required=True, tracking=True,
        states={'confirmed': [('readonly', False)]})
    split_mo_count = fields.Integer(default=0, compute='_compute_split_count')

    def _compute_split_count(self):
        for data in self:
            count = 0
            mrp_obj = data.search([('origin', '=', data.name)])
            if mrp_obj:
                for mrp_id in mrp_obj:
                    count = count + 1

            data.split_mo_count = count

    def btn_split_mo(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Split Production Order'),
                'res_model': 'split.mo.wizard',
                'target': 'new',
                'view_id': self.env.ref('ni_split_mrp_orders.split_mo_wizard_view_form').id,
                'view_mode': 'form',
                'view_type': 'form',
                'context': {}
                }

    def list_split_orders(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Split Manufacturing Orders'),
                'res_model': 'mrp.production',
                'target': 'current',
                'view_id': self.env.ref('mrp.mrp_production_tree_view').id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': False,
                'context': False,
                'domain': [('origin', '=', self.name)]
                }
