# models/product_template.py
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sap_reference = fields.Char(string='SAP Reference')
