# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingImportSerialNumber(models.TransientModel):
    _name = "stock.picking.import.serial.number.wiz"
    _description = "Import S/N wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if (
            self.env.context.get("active_ids")
            and self.env.context.get("active_model") == "stock.picking"
        ):
            pickings = self.env["stock.picking"].browse(
                self.env.context.get("active_ids")
            )
            if pickings.exists():
                res.update({"picking_ids": [(6, 0, pickings.ids)]})
        return res

    picking_ids = fields.Many2many("stock.picking")
    data_file = fields.Binary(string="File to import")
    filename = fields.Char(string="Filename")
    overwrite_serial = fields.Boolean()
    sn_search_product_by_field = fields.Selection(
        [("default_code", "Reference"), ("barcode", "Barcode")],
        string="Search product by field",
        default="default_code",
    )
    sn_product_column_index = fields.Integer(
        string="Column index for product", default=0
    )
    sn_serial_column_index = fields.Integer(
        string="Column index for S/N", default="1"
    )
    quantity_done_column_index = fields.Integer(
        string="Column index for Quantity Done", default="2"
    )
    process_only_lot_available = fields.Boolean(default=True)
    quantity_done = fields.Float(string="Quantity Done", default=1.0)

    def action_import(self):
        if self.picking_ids.filtered(
            lambda p: not p.picking_type_id.import_lot_from_file
        ):
            raise UserError(
                _(
                    "You only can import S/N for picking operations with"
                    " import lots checked"
                )
            )
        if not self.data_file:
            raise UserError(_("You must upload file to import records"))
        xl_workbook = False
        xl_sheet = False
        if self.filename.split(".")[1] in ["xls", "xlsx"]:
            xl_workbook = xlrd.open_workbook(
                file_contents=base64.b64decode(self.data_file)
            )
            xl_sheet = xl_workbook.sheet_by_index(0)
            for picking in self.picking_ids:
                move_lines = picking.mapped("move_line_ids").filtered(
                    lambda ln: ln.product_id.tracking == "serial"
                    and ln.picking_id.picking_type_id.import_lot_from_file
                )
                self._import_serial_number(xl_sheet, move_lines, picking)
        self.data_file = False

    def _import_serial_number(self, xl_sheet, stock_move_lines, picking):
        product_file_set = set()
        serial_quantity_list = []
        for row_idx in range(1, xl_sheet.nrows):
            product = str(xl_sheet.cell(row_idx, self.sn_product_column_index).value)
            serial = str(xl_sheet.cell(row_idx, self.sn_serial_column_index).value)
            quantity_done = xl_sheet.cell(row_idx, self.quantity_done_column_index).value
            product_file_set.add(product)
            serial_quantity_list.append((product, serial, quantity_done))

        products = self.env["product.product"].search(
            [(self.sn_search_product_by_field, "in", list(product_file_set))]
        )
        assigned_sml = set()
        for item in serial_quantity_list:
            product_name, serial, quantity_done = item
            product = products.filtered(
                lambda p: p[self.sn_search_product_by_field] == product_name
            )
            if picking.import_lot_from_file:
                self._assign_lot(
                    picking, product, serial, quantity_done, stock_move_lines, assigned_sml
                )

    def _assign_lot(self, picking, product, serial, quantity_done, stock_move_lines, assigned_sml):
        domain = [("product_id", "=", product.id), ("lot_name", "=", False)]
        if self.overwrite_serial:
            domain.remove(("lot_name", "=", False))
        smls = stock_move_lines.filtered_domain(domain)

        if picking.picking_type_code == "incoming":
            if picking.picking_type_id.show_reserved:
                for sml in smls:
                    if not sml.lot_name or (
                        self.overwrite_serial and sml.id not in assigned_sml
                    ):
                        sml.lot_name = serial
                        sml.qty_done = quantity_done
                        assigned_sml.add(sml.id)
                        break
            elif product:
                self._create_new_stock_move_line(
                    picking, product, serial, quantity_done, assigned_sml
                )
        else:
            sml = smls.filtered(
                lambda ln: ln.product_id == product and ln.lot_id.name == serial
            )
            if sml:
                sml.qty_done = quantity_done
                assigned_sml.add(sml.id)
            else:
                self._create_new_stock_move_line(
                    picking, product, serial, quantity_done, assigned_sml, search_lot=True
                )

    def _create_new_stock_move_line(
        self, picking, product, serial, quantity_done, assigned_sml, search_lot=False
    ):
        lot = False
        quant_available = self.env["stock.quant"].browse()
        if search_lot:
            lot = self.env["stock.production.lot"].search(
                [("product_id", "=", product.id), ("name", "=", serial)]
            )
            if lot:
                quant_available = self.env["stock.quant"]._gather(
                    product, picking.location_id, lot_id=lot
                )
                if self.process_only_lot_available and not quant_available:
                    return False
            else:
                return False
        move = picking.move_lines.filtered(lambda ln: ln.product_id == product)
        vals = {
            "picking_id": picking.id,
            "location_id": quant_available.location_id.id or picking.location_id.id,
            "location_dest_id": picking.location_dest_id.id,
            "product_id": product.id,
            "product_uom_id": product.uom_id.id,
            "lot_name": serial,
            "qty_done": quantity_done,
            "move_id": move[:1].id,
        }
        if not picking.picking_type_id.show_reserved:
            vals["product_uom_qty"] = 0.0
        if lot:
            vals["lot_id"] = lot.id
        sml = self.env["stock.move.line"].create(vals)
        assigned_sml.add(sml.id)
