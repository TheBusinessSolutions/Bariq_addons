from datetime import timedelta
import pytz

from odoo import fields, api, models


class movesReport(models.AbstractModel):

    _name = 'report.custom_moves_report.report_moves'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(
            {
            'product_ids': data.get('product_ids'),
            'location_id': data.get('location_id'),
            'date_start': data.get('date_start'),
            'date_stop': data.get('date_stop'),
            'report_head': data.get('report_head'),
            'to_collapse': data.get('to_collapse'),
            }
        )
        data.update(self.get_sale_details(data['date_start'], data['date_stop'], data['product_ids'], data['location_id'], data['to_collapse']))
        return data

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, products=False, location=False, to_collapse=False):
        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
            date_start = today.astimezone(pytz.timezone('UTC'))

        if date_stop:
            date_stop = fields.Datetime.from_string(date_stop)
            # avoid a date_stop smaller than date_start
            if (date_stop < date_start):
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        
        domain = [
            '&', '&', 
            ('state', '=', 'done'),
            ('product_id', 'in', products),
            ('date', '<=', fields.Datetime.to_string(date_stop)),
            '|',
            ('location_id', '=', location),
            ('location_dest_id', '=', location),
        ]
            
        all_moves = self.env['stock.move.line'].search(domain, order='date')
        prods = self.env['product.product'].search([('id', 'in', products)])
        prods = [prod.name_get()[0][1] for prod in prods]
        return{
            'products': prods,
            'data': list(self._process_moves(products, all_moves, date_start, location))
        }
    
    @api.model
    def _process_moves(self, products, all_moves, date_start, location):
        for product in products:
            lst = []
            total_out = 0
            total_in = 0
            opening_balance = 0
            balance = 0
            moves = all_moves.filtered(lambda r: r.product_id.id==product)
            if moves:
                balance = sum(-move.qty_done if move.location_id.id==location else move.qty_done for move in moves if move.date<=date_start)
                opening_balance = balance
                moves = moves.filtered(lambda r: r.date>=date_start)
                for move in moves:
                    temp_dict = {}
                    if location == move.location_id.id:
                        temp_dict['out'] = move.qty_done
                        temp_dict['in'] = '--'
                        balance += -(move.qty_done)
                        total_out += move.qty_done
                    else:
                        temp_dict['in'] = move.qty_done
                        temp_dict['out'] = '--'
                        balance += move.qty_done
                        total_in += move.qty_done
                    temp_dict['date'] = move.date
                    temp_dict['picking_type'] = self.substitute(move.picking_type_id.code)
                    temp_dict['balance'] = balance
                    lst.append(temp_dict)
            yield {
                'opening_balance': opening_balance,
                'balance': balance,
                'total_in': total_in,
                'total_out': total_out,
                'lst': lst,
            }

    @staticmethod
    def substitute(code):
        return code.replace('_', " ").title() if code else code
