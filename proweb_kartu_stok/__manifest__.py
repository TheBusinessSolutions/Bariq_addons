#############################################################################
#
#    PT. PROWEB INDONESIA.
#
#    Copyright (C) 2021-TODAY PROWEB INDONESIA(<https://www.proweb.co.id>)
#    Author: Junus J Djunawidjaja
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
	"name": "Kartu Stok",
	"version": "1.0", 
	"depends": [
		"base",
		"stock",
	], 
	"author": "PT. Proweb Indonesia",
	"company": "PT. Proweb Indonesia",
	"maintainer": "PT. Proweb Indonesia",
	"website": "https://www.proweb.co.id",
	"category": "Warehouse",
	'summary': """Print Kartu Stok (Stock Card) PDF/XLSX Report of Products/Product Variants
with Lots/Serial Number and Expired Date.""",
	"description": """
Features:
* Print Kartu Stok (Stock Card) of some Product / Product Variants on spesific Warehouse location
* Show Specific Date Range or Last Day number
* Output Report in PDF or Excel (XLSX) file format
* Display Lots/Serial Number and Expired Date

  This Report has some columns:
    - Date 
    - In
    - Out
    - Stock
    - Batch # (Lot)
    - ED  (Expired Date)
    - Distributor (Seller)
    - Buyer
""",
	"data": [
	'security/ir.model.access.csv',
	"report/product_product.xml",
	"wizard/kartu_stok_report.xml"
	],
	'images': ['static/description/images/main_report.gif'],
	"application": True,
	"installable": True,
	"auto_install": False,
	"license": "AGPL-3",
}

