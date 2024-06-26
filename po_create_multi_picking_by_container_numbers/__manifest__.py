# -*- coding: utf-8 -*-
{
    'name': "Purchase Multi Pickings",

    'version': "15.0.0.1",

    'summary': "This module allows you to create separate picking for Purchase order based on number of containers.",

    'category': 'Purchases',

    'description': """
        This module allows create multi receiving Picking
        based on the number of containers
    """,

    'author': "Business Solutions",

    'website': "thebusinesssolutions.net",

    'depends': ['base', 'purchase', 'purchase_import_fields'],

    'data': ['views/purchase.xml'],

    'demo': [],

    "license": "OPL-1",

    'images': ['static/description/banner.jpg'],

    'live_test_url': 'https://youtu.be/6pql7VwPPjo',

    'installable': True,

    'application': True,
    
    'auto_install': False,
}
