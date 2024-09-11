{
    'name': 'Restriction on Product Creation',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'summery': '',
    'author': 'INKERP',
    'website': "http://www.INKERP.com",
    'depends': ['product'],
    'data': [
        'security/group.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
