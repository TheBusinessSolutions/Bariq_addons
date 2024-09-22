# -*- coding: utf-8 -*-
{
    'name': "Bariq Project",

    'summary': """ Bariq Project """,

    'description': """ Bariq Project """,

    'author': "Bariq | Mohab Ahmed Hamed",

    'website': "",

    'category': '',

    'version': '15.0.1',

    'depends': ['base', 'mail', 'web', 'purchase', 'stock', 'purchase_stock', 'purchase_line_discount', 'purchase_import_fields', 'po_create_multi_picking_by_container_numbers'],

    'data': [
        'security/ir.model.access.csv',

        'reports/report_picking_bale_barcode_template.xml',

        'views/product_template.xml',
        'views/purchase_order.xml',
        'views/stock_location.xml',
        'views/stock_picking.xml',
        'views/stock_weight.xml',
        'views/shift_weight.xml',
        'views/res_company.xml',
        'views/stock_picking_bale.xml',
        'views/weight_in_production.xml',
        'views/view_show_bales_number_in_lot.xml',
    ],
}
