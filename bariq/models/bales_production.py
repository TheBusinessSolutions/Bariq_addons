# -*- coding: utf-8 -*-

from odoo import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    production_bales_number = fields.Integer(string="Production Bales Number")


    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        for production in self:
            if production.production_bales_number:
                pickings = production.picking_ids.filtered(lambda p: p.state not in ['done', 'cancel'])
                for picking in pickings:
                    for move in picking.move_ids_without_package:
                        move.update({'production_bales_number': production.production_bales_number})
        return res