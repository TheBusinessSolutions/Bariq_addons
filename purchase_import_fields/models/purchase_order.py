from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    imported_order = fields.Boolean(string='Imported Order')

    cntrs_number = fields.Char(string='CNTRs #')
    bl_number = fields.Char(string='BL#')
    pol = fields.Char(string='POL')
    pod = fields.Char(string='POD')
    vessel_etd = fields.Date(string='Vessel ETD')
    vessel_eta = fields.Date(string='Vessel ETA')
    number_of_days = fields.Integer(string='No# of Days')
    acid_number = fields.Char(string='ACID#')
    acid_date = fields.Date(string='ACID Date')
    shipped_from_supplier = fields.Boolean(string='Shipped from supplier')
    received_documents = fields.Date(string='Received Documents')
    inspection_certificate = fields.Char(string='Inspection Certificate')
    insurance_certificate = fields.Char(string='Insurance Certificate')
    arrived_at_port = fields.Date(string='Arrived at port')
    lg_date = fields.Date(string='L/G Date')
    arrived_at_bariq = fields.Date(string='Arrived at Bariq')
    clearance_start_date = fields.Date(string='Clearance Start date')
    clearance_end_date = fields.Date(string='Clearance End Date')
    clearance_days = fields.Char(string='Clearance days')
    clearance_company = fields.Char(string='Clearance Co.')
    customs_certificate_number = fields.Char(string='رقم الشهادة الجمركية')
    customs_certificate_date = fields.Date(string='تاريخ الشهادة الجمركية')
    report_ref_goiec = fields.Char(string='Report Ref# to GOIEC Cairo')
    report_ref_date_goiec = fields.Date(string='Date of Report Ref# to GOIEC Cairo')
    sample_withdrawal_number = fields.Char(string='رقم محضر سحب العينة')
    sample_withdrawal_date = fields.Date(string='تاريخ سحب العينة')
    conformity_certificate_number = fields.Char(string='رقم شهادة المطابقة')
    conformity_certificate_date = fields.Date(string='تاريخ شهادة المطابقة')
    shipment_status = fields.Selection(
    selection=[
        ('pending_advance_payment', 'Pending Advance Payment'),
        ('under_manufacturing', 'Under Manufacturing'),
        ('pending_pickup', 'Pending Pickup'),
        ('pending_vessel_arrival', 'Pending Vessel Arrival'),
        ('pending_original_docs', 'Pending Original Docs'),
        ('pending_customs_duties', 'Pending Customs Duties'),
        ('under_clearance', 'Under Clearance'),
        ('arrived', 'Arrived'),
    ],
    string='Shipment Status'
)
