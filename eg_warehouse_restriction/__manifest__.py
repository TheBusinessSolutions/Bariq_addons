{
    "name": "Warehouse Restriction",

    'version': "15.0",

    'category': "Stock",

    "summary": "This app will Restrict selected warehouse for particular User",
    
    'author': 'INKERP',
    
    'website': "https://www.INKERP.com",

    "depends": ['base', 'stock'],
    
    "data": [
        "views/res_users_view.xml",
        "security/security.xml",
        "views/stock_warehouse_views.xml",
    ],

    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
