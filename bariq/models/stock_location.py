# -*- coding: utf-8 -*-

from odoo import models, api, fields


class StockLocation(models.Model):
    _inherit = 'stock.location'


    def action_view_bales(self):
        action = self.env['ir.actions.act_window']._for_xml_id('bariq.stock_picking_bale_action')
        action["domain"] = [("location_id", "=", self.id)]
        return action