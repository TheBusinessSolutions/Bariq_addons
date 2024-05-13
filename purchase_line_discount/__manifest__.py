# -*- coding: utf-8 -*-
{
    'name': "SW - Purchase Order Lines Discount",
    'summary': "Add Percentage Discount (%) to your Purchase Orders and Requests for Quotations.",
    'description': "Adds new \"Discount (%)\" field in POL that applies discount to the POL and affects the inventory valuation. Odoo by default doesn't allow for discounts in the PO.",
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Purchases',
    'version': '1.0',
    'depends': ['base', 'purchase'],
    'data': [
        'views/purchase_order.xml',
        'report/purchase_order_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'purchase_line_discount/static/src/js/purchase_order_view.js',
            'purchase_line_discount/static/src/js/product_discount_widget.js',
        ],
    },
    'images':  ["static/description/image.png"],
    'license': "Other proprietary",
}
