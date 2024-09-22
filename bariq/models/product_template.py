# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    material_code = fields.Char(string='Material Code')


    def action_view_bales(self):
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', self.id)])
        action = self.env['ir.actions.act_window']._for_xml_id('bariq.stock_picking_bale_action')
        action["domain"] = [("product_id", "in", product_id.ids)]
        return action