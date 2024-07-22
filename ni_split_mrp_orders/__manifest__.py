{
    'name': "Split the MRP orders",
    'summary': """Split the MRP orders""",
    'description': """
Split the MRP orders
""",

    'version': '15.0',
    "sequence":  1,
    "images": ['static/description/Banner.gif'],
    "author":  "Nevioo Technologies",
    "license": 'OPL-1',
    'depends': ['base', "product", "sale_management", "purchase", "stock", 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'security/user_group_security.xml',
        'wizard/split_mo_wizard_view.xml',
        'views/mrp_views.xml',


    ],
    'qweb': [],
    "application":  True,
    "installable":  True,
    "auto_install":  False
}