# __manifest__.py
{
    'name': 'Product SAP Reference',
    'version': '1.0',
    'summary': 'Add SAP Reference field to product form',
    'description': 'This module adds a SAP Reference field to the product form and allows searching by this field.',
    'author': 'Business Solutions',
    'category': 'Inventory',
    'depends': ['product'],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
}
