from odoo import _, api, fields, models, tools
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sequence_id = fields.Many2one('ir.sequence', 'Sequence', copy=False, invisible=True)
    seq_count = fields.Integer(default=1, string='Start From')


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_normal_sequence = fields.Boolean(string='Normal Sequence', default=True)
    seq_count = fields.Integer(related='product_id.seq_count', readonly=False)

    def action_generate_serial(self):
        for rec in self:
            current_date = fields.Date.today()
            year = current_date.year
            no_year = year % 100
            day_of_year = current_date.timetuple().tm_yday
            day_of_year_digits = f"{day_of_year:03d}"
            code_product = rec.product_id.default_code
            prefix_code = str(no_year) + str(day_of_year_digits)
            seq_count_digits = f"{rec.product_id.seq_count:03d}"
            seq = prefix_code + str(seq_count_digits)

            f_seq = str(seq) + '.' + str(code_product)
            rec.product_id.seq_count += 1
            rec.is_normal_sequence = True
            print(f_seq)
            rec.lot_producing_id = rec.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': f_seq,
            })
            if self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids:
                self.move_finished_ids.filtered(
                    lambda m: m.product_id == self.product_id).move_line_ids.lot_id = self.lot_producing_id
            if self.product_id.tracking == 'serial':
                self._set_qty_producing()

    def _compute_propagated_lot_producing(self):
        for order in self:
            order.propagated_lot_producing = False
            move_with_lot = order._get_propagating_component_move()
            line_with_sn = move_with_lot.move_line_ids.filtered(
                lambda l: (
                        l.lot_id
                        and l.product_id.tracking == "lot"
                        and tools.float_compare(
                    l.qty_done, 1, precision_rounding=l.product_uom_id.rounding
                )
                        == 0
                )
            )
            if len(line_with_sn) == 1:
                lot_no = line_with_sn.lot_id.name
                replaced_lot = lot_no.split('.')[0] + '.' + order.product_id.default_code
                order.propagated_lot_producing = replaced_lot

# @api.model
#     def create(self, vals):
#         res = super(SaleOrder, self).create(vals)
#         for rec in res:
#             unpaid_orders = self.env['sale.order'].search(
#                 [('user_id', '=', rec.user_id.id), ('hydro_payment_state', '=', 'notpaid'), ('id', '!=', rec.id),
#                  ('is_booking_type', '=', True)])
#             if unpaid_orders:
#                 raise ValidationError(
#                     _("""There is pending unpaid order. """))
#
#         if res.hotel_id.sequence_id:
#             res.sequence = res.hotel_id.sequence_id.next_by_code(res.hotel_id.name)
#         if not res.hotel_id.sequence_id:
#             seq_vals = {
#                 'code': res.hotel_id.name,
#                 'name': res.hotel_id.name,
#                 'prefix': res.hotel_id.name + '/',
#                 'padding': 5
#             }
#             seq = self.env['ir.sequence'].sudo().create(seq_vals)
#             res.hotel_id.sequence_id = seq
#             res.sequence = seq.next_by_code(res.hotel_id.name)
