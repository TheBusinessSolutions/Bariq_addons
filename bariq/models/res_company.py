# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    weight_script_url  = fields.Char(string="Weight Script URL")
    weight_script_port = fields.Char(string="Weight Script Port")