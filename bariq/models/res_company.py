# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    link = fields.Char(string="Link")
    username = fields.Char(string='Username')
    password = fields.Char(string='Password')