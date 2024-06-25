# -*- coding: utf-8 -*-


{
    'name': "Purchase Multi Pickings",
    'version': "11.0.0.1",
    'summary': "This module allows you to create separate picking for Purchase order based on number of containers.",
    'category': 'Purchases',
    'description': """
        This module allows create multi receiving Picking
        based on the number of containers
    """,
    'author': "Business Solutions",
    'website': "thebusinesssolutions.net",
    'depends': ['base', 'purchase'],
    'data': [
        'views/purchase.xml'
    ],
    'demo': [],
    "license": "OPL-1",
    'images': ['static/description/banner.jpg'],
   
    'installable': True,
    'application': True,
    'auto_install': False,
}
