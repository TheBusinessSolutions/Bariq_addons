from datetime import timedelta

from odoo import api, fields, models


class movesDetails(models.TransientModel):
    _name = 'moves.details.report'
    _description = 'Product Moves Report'

    def _default_start_date(self):
        return fields.Datetime.now() - timedelta(days=1)

    start_date = fields.Datetime(required=True, default=_default_start_date)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    product_ids = fields.Many2many(
        'product.product', string='Product', required=True,
        )
    location_id = fields.Many2one(
        'stock.location', 'Location', required=True,
        help="Select a location.")
    to_collapse = fields.Boolean(string='Collapse', default=False)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    def generate_report(self):
        data = {
            'date_start': self.start_date,
            'date_stop': self.end_date,
            'product_ids': self.product_ids.mapped('id'),
            'location_id': self.location_id.id,
            'to_collapse': self.to_collapse,
            'report_head': f'Movement Report in {self.location_id.name_get()[0][1]}'
        }
        return self.env.ref('custom_moves_report.moves_report').report_action([], data=data)
