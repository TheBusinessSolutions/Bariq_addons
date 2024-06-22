# -*- coding: utf-8 -*-
{
    'name': "Bariq Project",

    'summary': """ Bariq Project """,

    'description': """ Bariq Project """,

    'author': "Bariq | Mohab Ahmed Hamed",

    'website': "",

    'category': '',

    'version': '15.0.1',

    'depends': ['base', 'mail', 'web', 'purchase', 'stock', 'purchase_stock', 'purchase_line_discount'],

    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/purchase_order.xml',
        'views/stock_picking.xml',
        'views/stock_weight.xml',
        'views/shift_weight.xml',
        'views/res_company.xml',
    ],
}
