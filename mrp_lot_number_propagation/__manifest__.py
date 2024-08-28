# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "MRP Serial Number Propagation",
    "version": "15.0.0.3.0",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["sebalix"],
    "summary": "Propagate a serial number from a component to a finished product",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "security/lot_number_seq_secuirty.xml",
        "views/mrp_bom.xml",
        "views/mrp_production.xml",
        "views/mrp_production_seq.xml",
    ],
    "installable": True,
    "application": False,
}
