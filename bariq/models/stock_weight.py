# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError

class StockWeight(models.Model):
    _name = 'stock.weight'


    name      = fields.Char(string="Name", required=True)
    code      = fields.Char(string="Code", required=True)
    ip_addr   = fields.Char(string="IP Address", required=True)
    port      = fields.Char(string="Port Number", required=True)
    user_ids  = fields.Many2many('res.users', string="Access Users", required=True)
    is_manual = fields.Boolean(string="Manual")


    @api.model
    def create(self, vals):
        stock_weight_ids = self.env['stock.weight'].search([('ip_addr', '=', vals.get('ip_addr')), ('port', '=', vals.get('port'))])
        if stock_weight_ids:
            raise ValidationError(f"This IP {vals.get('ip_addr')} & Port {vals.get('port')} Already Exist")
        return super(StockWeight, self).create(vals)


    def write(self, vals):
        ip_addr = vals.get('ip_addr') or self.ip_addr
        port = vals.get('port') or self.port
        stock_weight_ids = self.env['stock.weight'].search([('ip_addr', '=', ip_addr), ('port', '=', port)])
        if stock_weight_ids:
            raise ValidationError(f"This IP {ip_addr} & Port {port} Already Exist")
        return super(StockWeight, self).write(vals)