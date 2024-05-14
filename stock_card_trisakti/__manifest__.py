{
    'name': "Stock Card Trisakti",
    "version": "16.0.1.0.0",
    "category": "Warehouse",
    "summary": "All warehouse related PDF and Excel reports",
    "description": "User is able to print Pdf and Excel report of Stock move,"
                   "Transfer,Product,Stock valuation.All warehouse related PDF"
                   "and Excel report",
    'author': 'Putri Maresti',
    'company': 'Trisakti University',
    'depends': ['stock', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/stock_valuation_report_views.xml',
        'wizards/stock_move_report_views.xml',
        'report/ir_action_reports.xml',
        'report/stock_valuation_report_templates.xml',
        'report/stock_transfer_report_templates.xml',
        'report/stock_move_report_templates.xml',
        'report/stock_product_report_templates.xml',
        'wizards/stock_product_report_views.xml',
        'wizards/stock_transfer_report_views.xml',
        'views/warehouse_reports_menus.xml'
    ],
    'assets':
        {
            'web.assets_backend': [
                'warehouse_reports/static/src/js/stock_excel_report.js'
            ],
        },
    'images': [
        'static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
