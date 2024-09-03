# -*- coding: utf-8 -*-
import re
import json
import socket
import requests
from datetime import datetime
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    weight_id = fields.Many2one('stock.weight', string='Weight type')
    weight_1 = fields.Float(string="Weight")
    is_get_weight_1 = fields.Boolean(string='Is Get Weight')

    weight_ticket_number = fields.Char(readonly=True, string="Ticket Number")
    is_generate_lots = fields.Boolean(string="Is Generate Lots", default=False)
    lot_producing_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number',
        copy=False,
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",
        check_company=True,
        readonly=True,
    )

    is_lot_number_propagated = fields.Boolean(
        default=False,
        readonly=True,
        help=(
            "Lot/Serial number is propagated "
            "from a component to the finished product."
        ),
    )
    propagated_lot_producing = fields.Char(
        compute="_compute_propagated_lot_producing",
        store=True,
        help=(
            "The lot/serial number for the finished product is automatically generated "
            "based on the material code and the weight ticket number."
        ),
    )

    @api.depends("weight_ticket_number", "product_id")
    def _compute_propagated_lot_producing(self):
        for order in self:
            if order.weight_ticket_number and order.product_id:
                material_code = order.product_id.product_tmpl_id.material_code if hasattr(
                    order.product_id.product_tmpl_id, 'material_code') else ""
                lot_name = f"{material_code}{order.weight_ticket_number}"

                # Check if the lot/serial number already exists
                existing_lot = self.env['stock.production.lot'].search([
                    ('product_id', '=', order.product_id.id),
                    ('company_id', '=', order.company_id.id),
                    ('name', '=', lot_name),
                ], limit=1)

                if existing_lot:
                    order.lot_producing_id = existing_lot
                else:
                    # Create a new lot/serial number if it doesn't exist
                    lot = self.env['stock.production.lot'].create({
                        'product_id': order.product_id.id,
                        'company_id': order.company_id.id,
                        'name': lot_name,
                    })
                    order.lot_producing_id = lot

                order.propagated_lot_producing = lot_name

    def action_generate_mrp_lots_name(self):
        if not self.weight_id:
            raise UserError(_('Weight ID is missing. Please configure the Weight ID before generating lots.'))

        # Check if there are backorders
        if self.move_finished_ids.filtered(lambda move: move.state == 'waiting'):
            self.weight_ticket_number = False
            return

        day = str(fields.date.today().day)
        month = str(fields.date.today().month)
        code = ''
        ticket = str(self.weight_id.code)
        sequence = str(self.weight_id.sequence_id._next()) if self.weight_id.sequence_id else ''

        for record in self.move_raw_ids.move_line_ids:
            barcode = str(record.product_id.material_code) if hasattr(record.product_id, 'material_code') else ''

            for shift in self.env['shift.weight'].search([]):
                time_format = "%I:%M %p"
                time_now = datetime.strptime(datetime.now().strftime(time_format), time_format)
                start_shift = datetime.strptime(f"{shift.start_hour}:{shift.start_minute} {shift.start_type}",
                                                time_format)
                end_shift = datetime.strptime(f"{shift.end_hour}:{shift.end_minute} {shift.end_type}", time_format)

                if start_shift <= end_shift and start_shift <= time_now <= end_shift:
                    code = shift.code
                if not start_shift <= end_shift and (time_now >= start_shift or time_now <= end_shift):
                    code = shift.code

            record.lot_name = barcode + day + month + code + ticket + sequence

        self.weight_ticket_number = day + month + code + ticket + sequence
        self.is_generate_lots = True

        material_code = self.product_id.product_tmpl_id.material_code if hasattr(self.product_id.product_tmpl_id,
                                                                                 'material_code') else ""
        lot_name = f"{material_code}{self.weight_ticket_number}"

        # Check if the lot/serial number already exists
        existing_lot = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('name', '=', lot_name),
        ], limit=1)

        if existing_lot:
            self.lot_producing_id = existing_lot
        else:
            # Create a new lot/serial number if it doesn't exist
            self.lot_producing_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': lot_name,
            })

    def button_mark_done(self):
        # Ensure that weight_1 is fetched before marking done
        if not self.weight_1:
            raise UserError(_('You Must Get Track Weight First Before Marking Done.'))

        # Apply logic for weight
        for record in self.move_raw_ids.move_line_ids:
            record.qty_done = abs(self.weight_1)

        return super(MrpProduction, self).button_mark_done()

    def action_generate_serial(self):
        self.ensure_one()
        if self.product_id.tracking == 'none':
            return

        # Fetch the standard serial name
        name = self.env['stock.production.lot']._get_new_serial(self.company_id, self.product_id)

        # Fetch the material_code from product.template
        material_code = self.product_id.product_tmpl_id.material_code if hasattr(self.product_id.product_tmpl_id,
                                                                                 'material_code') else ""

        # Combine the material_code and weight_ticket_number without any separation characters
        if self.weight_ticket_number:
            name = f"{material_code}{self.weight_ticket_number}"

        # Check if the lot/serial number already exists
        existing_lot = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('name', '=', name),
        ], limit=1)

        if existing_lot:
            self.lot_producing_id = existing_lot
        else:
            # Create the lot/serial with the combined name if it doesn't exist
            self.lot_producing_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': name,
            })

        # If tracking by serial, adjust the quantity to produce
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()

    @api.onchange('weight_1')
    def _onchange_weight_1(self):
        if self.weight_1:
            self.qty_producing = abs(self.weight_1)

    def get_weight_1(self):
        if not self.weight_id:
            raise UserError("Weight configuration is missing. Please ensure that a valid Weight ID is set.")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.weight_id.ip_addr, int(self.weight_id.port)))

            response = client.recv(1024)
            response = response.decode("utf-8")

            if not response.isdigit():
                raise UserError("Invalid Return Response %s" % response)

            try:
                self.weight_1 = float(response)
                self.is_get_weight_1 = True
            except:
                self.weight_1 = 0.0
                self.is_get_weight_1 = False

            client.close()

        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" % e)
