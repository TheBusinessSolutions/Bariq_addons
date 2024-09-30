{
    "name": "Product Restriction on User",

    'version': "15.0",

    'category': "Product",

    "summary": "This app will restrict multiple Products for particular user.",
    
    'author': 'INKERP',

    'website': "http://www.INKERP.com",

    "depends": ['product'],
    
    "data": [
        "security/security.xml",
        "views/res_users_views.xml",
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
