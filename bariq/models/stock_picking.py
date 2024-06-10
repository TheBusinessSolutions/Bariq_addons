# -*- coding: utf-8 -*-

import re
import socket
from datetime import datetime
from odoo.exceptions import UserError
from odoo import models, api, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    driver_name    = fields.Char(string="Driver Name",    compute='compute_ticket_details')
    driver_license = fields.Char(string="Driver License", compute='compute_ticket_details')
    truck_number   = fields.Char(string="Truck Number",   compute='compute_ticket_details')
    trailer_number = fields.Char(string="Trailer Number", compute='compute_ticket_details')
    dawar_ticket   = fields.Char(string="Dawar Ticket",   compute='compute_ticket_details')

    weight_ticket_number = fields.Char(string="Ticket Number", related='weight_id.code')
    available_weight_ids = fields.Many2many('stock.weight', string='Available Weight', compute='compute_available_weight')
    is_get_weight_1 = fields.Boolean(string='Is Get Weight 1')
    is_get_weight_2 = fields.Boolean(string='Is Get Weight 2')
    weight_id = fields.Many2one('stock.weight', string='Weight')
    is_manual = fields.Boolean(string="Manual", related='weight_id.is_manual')
    weight_1  = fields.Float(string="Weight 1")
    weight_2  = fields.Float(string="Weight 2")
    rejected  = fields.Float(string="Rejected (%)")

    is_dawar_picking = fields.Boolean(compute='compute_is_dawar_picking')
    is_generate_lots = fields.Boolean()


    def compute_available_weight(self):
        for record in self:
            record.available_weight_ids = self.env['stock.weight'].search([]).filtered(lambda weight: record.env.user.id in weight.user_ids.ids)

    
    def compute_ticket_details(self):
        for record in self:
            purcahse_id = self.env['purchase.order'].search([('id', '=', record.purchase_id.id), ('is_dawar_purchase', '=', True)])

            record.driver_name    = purcahse_id.driver_name    if purcahse_id else ''
            record.driver_license = purcahse_id.driver_license if purcahse_id else ''
            record.truck_number   = purcahse_id.truck_number   if purcahse_id else ''
            record.trailer_number = purcahse_id.trailer_number if purcahse_id else ''
            record.dawar_ticket   = purcahse_id.partner_ref    if purcahse_id else ''


    def compute_is_dawar_picking(self):
        for record in self:
            purcahse_id = self.env['purchase.order'].search([('id', '=', record.purchase_id.id), ('is_dawar_purchase', '=', True)])
            record.is_dawar_picking = True if purcahse_id else False


    def reset_weight_1(self):
        self.weight_1 = 0.0
        self.is_get_weight_1 = False

        for record in self.move_line_nosuggest_ids:
            record.qty_done = self.weight_1 - self.weight_2


    def reset_weight_2(self):
        self.weight_2 = 0.0
        self.is_get_weight_2 = False

        for record in self.move_line_nosuggest_ids:
            record.qty_done = self.weight_1 - self.weight_2


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

            for record in self.move_line_nosuggest_ids:
                record.qty_done = self.weight_1 - self.weight_2

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

            for record in self.move_line_nosuggest_ids:
                record.qty_done = self.weight_1 - self.weight_2

            client.close()

        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" % e)


    @api.onchange('weight_1', 'weight_2')
    def onchange_weight(self):
        if self.weight_1 != 0.0 or self.weight_2 != 0.0:
            for record in self.move_line_nosuggest_ids:
                record.qty_done = self.weight_1 - self.weight_2


    def action_generate_lots_name(self):
        day    = str(fields.date.today().day)
        month  = str(fields.date.today().month)
        code   = False
        ticket = str(self.weight_ticket_number) if self.weight_ticket_number else ''

        for shift in self.env['shift.weight'].search([]):
            time_format = "%I:%M %p"
            time_now    = datetime.now().strftime(time_format)
            time_now    = datetime.strptime(time_now, time_format)
            start_shift = datetime.strptime(f"{shift.start_hour}:{shift.start_minute} {shift.start_type}", time_format)
            end_shift   = datetime.strptime(f"{shift.end_hour}:{shift.end_minute} {shift.end_type}", time_format)

            if start_shift <= end_shift and start_shift <= time_now <= end_shift:
                code = shift.code

            if not start_shift <= end_shift and (time_now >= start_shift or time_now <= end_shift):
                code = shift.code

        for record in self.move_line_nosuggest_ids:
            barcode = str(record.product_id.material_code) if record.product_id.material_code else ''
            record.lot_name = barcode + day + month + code + ticket

        self.is_generate_lots = True


    def button_validate(self):
        rec = super(StockPicking, self).button_validate()

        if not self.is_generate_lots and self.is_dawar_picking:
            raise UserError(_('You Must Generate Lots Name Before Validate.'))

        if (not self.is_get_weight_1 or not self.is_get_weight_2) and self.is_dawar_picking:
            raise UserError(_('You Must Get Track Weight First Before Validate.'))

        if self.rejected != 0.0:
            for record in self.purchase_id.order_line:
                record.discount = self.rejected

        for record in self.move_line_nosuggest_ids:
            record.qty_done = self.weight_1 - self.weight_2

        return rec