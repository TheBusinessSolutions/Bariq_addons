# -*- coding: utf-8 -*-

import re
import json
import socket
import requests
from datetime import datetime
from odoo.exceptions import UserError
from odoo import models, api, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_name    = fields.Char(string="Driver Name",    compute='compute_ticket_details', store=True)
    driver_license = fields.Char(string="Driver License", compute='compute_ticket_details', store=True)
    truck_number   = fields.Char(string="Truck Number",   compute='compute_ticket_details', store=True)
    trailer_number = fields.Char(string="Trailer Number", compute='compute_ticket_details', store=True)
    dawar_ticket   = fields.Char(string="Dawar Ticket",   compute='compute_ticket_details', store=True)

    weight_ticket_number = fields.Char(string="Ticket Number", compute='compute_weight_ticket_number', store=True)
    available_weight_ids = fields.Many2many('stock.weight', string='Available Weight', compute='compute_available_weight')
    is_get_weight_1 = fields.Boolean(string='Is Get Weight 1')
    is_get_weight_2 = fields.Boolean(string='Is Get Weight 2')
    weight_id = fields.Many2one('stock.weight', string='Weight')
    is_manual = fields.Boolean(string="Manual", related='weight_id.is_manual')
    weight_1  = fields.Float(string="Weight 1")
    weight_2  = fields.Float(string="Weight 2")
    rejected  = fields.Float(string="Rejected (%)")

    is_dawar_picking = fields.Boolean(compute='compute_is_dawar_picking', store=True)
    is_generate_lots = fields.Boolean()

    barcode = fields.Char(string='Barcode')


    def action_open_label_layout(self):
        view  = self.env.ref('stock.product_label_layout_form_picking')
        bales = 0

        for record in self.move_ids_without_package:
            bales = record.bales_number

        if bales != 0:
            return {
                'name': _('Choose Labels Layout'),
                'type': 'ir.actions.act_window',
                'res_model': 'product.label.layout',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {
                    'default_product_ids': self.move_lines.product_id.ids,
                    'default_move_line_ids': self.move_line_ids.ids,
                    'default_picking_quantity': 'custom',
                    'default_custom_quantity': bales,
                },
            }

        else:
            return {
                'name': _('Choose Labels Layout'),
                'type': 'ir.actions.act_window',
                'res_model': 'product.label.layout',
                'views': [(view.id, 'form')],
                'target': 'new',
                'context': {
                    'default_product_ids': self.move_lines.product_id.ids,
                    'default_move_line_ids': self.move_line_ids.ids,
                    'default_picking_quantity': 'picking'
                },
            }


    @api.onchange('barcode')
    def create_new_picking_line(self):
        if self.barcode and self.picking_type_id.code in ['outgoing', 'internal']:

            stock_lot_id = self.env['stock.production.lot'].sudo().search([('name', '=', self.barcode)])
            product_id   = False

            if not stock_lot_id:
                product_id = self.env['product.product'].sudo().search([('barcode', '=', self.barcode)])

                if not product_id:
                    raise UserError("This Barcode Not Found In Products & Lots")
            else:
                product_id = stock_lot_id.product_id

            self.move_ids_without_package = [(0, 0, {
                'product_id': product_id.id,
                'name': product_id.name,
                'date': datetime.now(),
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'quantity_done': stock_lot_id.product_qty if stock_lot_id else 0.0,
                'product_uom': product_id.uom_id.id,
                'company_id': self.env.company.id,
                'bariq_lot_id': stock_lot_id.id if stock_lot_id else False
            })]

            self.barcode = False


    def close_dawar_ticket(self):
        auth_link, close_link, user_token = '', '', ''

        if self.env.company.link and self.env.company.link[-1] == '/':
            auth_link  = self.env.company.link + 'auth/login'
            close_link = self.env.company.link + 'tickets/oddo/close/'  + self.dawar_ticket
        else:
            auth_link  = self.env.company.link + '/auth/login'
            close_link = self.env.company.link + '/tickets/oddo/close/' + self.dawar_ticket


        try:
            headers    = {'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
            payload    = {'grant_type': 'client_credentials', 'phone': self.env.company.username, 'password': self.env.company.password}
            response   = requests.request("POST", auth_link, headers=headers, data=payload)
            user_token = response.json().get('access_token')
        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" % e)


        try:
            headers  = {'Authorization': f'Bearer {user_token}', 'Content-Type': 'application/json'}
            payload  = {
                'grant_type'  : 'client_credentials',
                'weighBridgeId': self.weight_ticket_number,
                'netweight'   : abs((self.weight_1 - self.weight_2) * (self.rejected / 100)),
                'firstWeight' : self.weight_1,
                'secondWeight': self.weight_2,
                'grossWeight' : self.weight_1 - self.weight_2,
                'rejectedRate': self.rejected / 100
            }
            response = requests.patch(close_link, json=payload, headers=headers)
        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" % e)


    @api.onchange('weight_1', 'weight_2')
    def action_calculate_done_qty(self):
        for record in self.move_line_ids_without_package:
            record.qty_done = abs(self.weight_1 - self.weight_2)


    @api.onchange('weight_1')
    def set_is_get_weight_1(self):
        self.is_get_weight_1 = True if self.weight_1 > 0 else False


    @api.onchange('weight_2')
    def set_is_get_weight_2(self):
        self.is_get_weight_2 = True if self.weight_2 > 0 else False


    def compute_available_weight(self):
        for record in self:
            record.available_weight_ids = self.env['stock.weight'].search([]).filtered(lambda weight: record.env.user.id in weight.user_ids.ids)


    @api.depends('purchase_id')
    def compute_ticket_details(self):
        for record in self:
            purcahse_id = self.env['purchase.order'].search([('id', '=', record.purchase_id.id), ('is_dawar_purchase', '=', True)])

            record.driver_name    = purcahse_id.driver_name    if purcahse_id else ''
            record.driver_license = purcahse_id.driver_license if purcahse_id else ''
            record.truck_number   = purcahse_id.truck_number   if purcahse_id else ''
            record.trailer_number = purcahse_id.trailer_number if purcahse_id else ''
            record.dawar_ticket   = purcahse_id.partner_ref    if purcahse_id else ''


    @api.depends('purchase_id')
    def compute_is_dawar_picking(self):
        for record in self:
            purcahse_id = self.env['purchase.order'].search([('id', '=', record.purchase_id.id), ('is_dawar_purchase', '=', True)])
            record.is_dawar_picking = True if purcahse_id else False


    def reset_weight_1(self):
        self.weight_1 = 0.0
        self.is_get_weight_1 = False
        for record in self.move_line_ids_without_package:
            record.qty_done = abs(self.weight_1 - self.weight_2)


    def reset_weight_2(self):
        self.weight_2 = 0.0
        self.is_get_weight_2 = False
        for record in self.move_line_ids_without_package:
            record.qty_done = abs(self.weight_1 - self.weight_2)


    def get_weight_1(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.weight_id.ip_addr, int(self.weight_id.port)))

            response = client.recv(1024)
            response = response.decode("utf-8")

            if not response.isdigit():
                raise UserError("Invaild Return Response %s" %response)

            try:
                self.weight_1 = float(response)
                self.is_get_weight_1 = True
            except:
                self.weight_1 = 0.0
                self.is_get_weight_1 = False

            for record in self.move_line_ids_without_package:
                record.qty_done = abs(self.weight_1 - self.weight_2)

            client.close()
            
        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" %e)


    def get_weight_2(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.weight_id.ip_addr, int(self.weight_id.port)))

            response = client.recv(1024)
            response = response.decode("utf-8")

            if not response.isdigit():
                raise UserError("Invaild Return Response %s" % response)

            try:
                self.weight_2 = float(response)
                self.is_get_weight_2 = True
            except:
                self.weight_2 = 0.0
                self.is_get_weight_2 = False

            for record in self.move_line_ids_without_package:
                record.qty_done = abs(self.weight_1 - self.weight_2)

            client.close()

        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" % e)


    @api.onchange('weight_1', 'weight_2')
    def onchange_weight(self):
        if self.weight_1 != 0.0 or self.weight_2 != 0.0:
            for record in self.move_line_ids_without_package:
                record.qty_done = abs(self.weight_1 - self.weight_2)


    def action_generate_lots_name(self):
        day    = str(fields.date.today().day)
        month  = str(fields.date.today().month)
        code   = ''
        ticket = str(self.weight_id.code)
        sequence = str(self.weight_id.sequence_id._next()) if self.weight_id.sequence_id else ''

        for record in self.move_line_ids_without_package:
            barcode  = str(record.product_id.material_code) if record.product_id.material_code else ''

            for shift in self.env['shift.weight'].search([]):
                time_format = "%I:%M %p"
                time_now    = datetime.strptime(datetime.now().strftime(time_format), time_format)
                start_shift = datetime.strptime(f"{shift.start_hour}:{shift.start_minute} {shift.start_type}", time_format)
                end_shift   = datetime.strptime(f"{shift.end_hour}:{shift.end_minute} {shift.end_type}", time_format)

                if start_shift <= end_shift and start_shift <= time_now <= end_shift:
                    code = shift.code
                if not start_shift <= end_shift and (time_now >= start_shift or time_now <= end_shift):
                    code = shift.code

            record.lot_name = barcode + day + month + code + ticket + sequence


        self.weight_ticket_number = day + month + code + ticket + sequence
        self.is_generate_lots = True


    def button_validate(self):
        if self.picking_type_id.code == 'incoming':
            if not self.is_generate_lots and self.is_dawar_picking:
                raise UserError(_('You Must Generate Lots Name Before Validate.'))

            if (not self.is_get_weight_1 or not self.is_get_weight_2) and self.is_dawar_picking:
                raise UserError(_('You Must Get Track Weight First Before Validate.'))

            if self.rejected != 0.0:
                for record in self.purchase_id.order_line:
                    record.discount = self.rejected

            for record in self.move_line_ids_without_package:
                record.qty_done = abs(self.weight_1 - self.weight_2)

            if self.is_dawar_picking:
                self.close_dawar_ticket()


        if self.picking_type_id.code in ['outgoing', 'internal']:
            for record in self.move_ids_without_package:
                for line in record.move_line_ids:
                    line.lot_id = int(record.bariq_lot_id) if record.bariq_lot_id else False

        return super(StockPicking, self).button_validate()