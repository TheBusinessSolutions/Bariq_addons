# print_warehouse_weight_data/__manifest__.py
{
    'name': 'Print Warehouse Weight Data',
    'version': '15.0.1.0.0',
    'summary': 'Add weight and ticket data in the delivery slip report',
    'description': 'weight and ticket data in the delivery slip report',
    'category': 'Warehouse',
    'author': 'BUsiness Solutions',
    'website': 'http://thebusinesssolutions.net',
    'depends': ['stock'],
    'data': [
        'views/report_deliveryslip_templates.xml',
        'report/delivery_slip_report.xml',
    ],
    'installable': True,
    'application': False,
}
