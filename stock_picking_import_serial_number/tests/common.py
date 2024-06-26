# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


class CommonStockPickingImportSerial(object):
    def assertUniqueIn(self, element_list):
        elements = []
        for element in element_list:
            if element in elements:
                raise Exception("Element %s is not unique in list" % element)
            elements.append(element)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.lot_obj = cls.env["stock.production.lot"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_int = cls.env.ref("stock.picking_type_internal")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_in.use_create_lots = True
        cls.picking_type_in.show_reserved = True

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.shelf_location = cls.env["stock.location"].create(
            {
                "name": "shelf for tests",
                "location_id": cls.stock_location.id,
                "usage": "internal",
            }
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier - test"})
        cls.customer = cls.env["res.partner"].create({"name": "Customer - test"})
        cls.file = b"0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAOwADAP7/CQAGAAAAAAAAAAAAAAABAAAACQAAAAAAAAAAEAAAAgAAAAEAAAD+////AAAAAAAAAAD////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////9//////////7///8EAAAABQAAAAYAAAAHAAAACAAAAP7///8KAAAA/v///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////1IAbwBvAHQAIABFAG4AdAByAHkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWAAUA////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD+////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP7///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/v///wAAAAAAAAAAAQAAAAIAAAADAAAABAAAAAUAAAAGAAAABwAAAAgAAAAJAAAACgAAAAsAAAAMAAAADQAAAA4AAAAPAAAAEAAAABEAAAASAAAAEwAAABQAAAAVAAAAFgAAABcAAAAYAAAAGQAAABoAAAAbAAAAHAAAAB0AAAAeAAAAHwAAACAAAAAhAAAAIgAAACMAAAAkAAAAJQAAACYAAAAnAAAA/v///ykAAAD+/////v///ywAAAAtAAAA/v///y8AAAD+//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8JCBAAAAYFALsNzAcAAAAABgAAAOEAAgCwBMEAAgAAAOIAAABcAHAABAAAQ2FsYyAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIEIAAgCwBGEBAgAAAMABAAA9AQIAAQCcAAIADgCvAQIAAAC8AQIAAAA9ABIAAAAAAABAACA4AAAAAAABAPQBQAACAAAAjQACAAAAIgACAAAADgACAAEAtwECAAAA2gACAAAAMQAaAMgAAAD/f5ABAAAAAgAABQFBAHIAaQBhAGwAMQAaAMgAAAD/f5ABAAAAAAAABQFBAHIAaQBhAGwAMQAaAMgAAAD/f5ABAAAAAAAABQFBAHIAaQBhAGwAMQAaAMgAAAD/f5ABAAAAAAAABQFBAHIAaQBhAGwAMQAuAMgAAAD/f5ABAAAAAQAADwFUAGkAbQBlAHMAIABOAGUAdwAgAFIAbwBtAGEAbgAeBAwApAAHAABHZW5lcmFs4AAUAAAApAD1/yAAAAAAAAAAAAAAAMAg4AAUAAEAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAEAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAIAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAIAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAAAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAAAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAAAAAD1/yAAAPQAAAAAAAAAAMAg4AAUAAAAAAD1/yAAAPQAAAAAAAAAAMAg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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABIAAgADAAAA//////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAAASQAAAAAAAAABAE8AbABlAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgACAP///////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoAAAAUAAAAAAAAAAUAUwB1AG0AbQBhAHIAeQBJAG4AZgBvAHIAbQBhAHQAaQBvAG4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoAAIA/////wUAAAD/////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKwAAAKwAAAAAAAAABQBEAG8AYwB1AG0AZQBuAHQAUwB1AG0AbQBhAHIAeQBJAG4AZgBvAHIAbQBhAHQAaQBvAG4AAAAAAAAAAAAAADgAAgD///////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuAAAAdAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP7///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/v///wAAAAAAAAAA"  # noqa: B950

    @classmethod
    def _create_product(cls, tracking="lot", reference=None):
        name = "{tracking}".format(tracking=tracking)
        vals = {
            "name": name,
            "type": "product",
            "tracking": tracking,
        }
        if reference:
            vals["default_code"] = reference
        return cls.env["product.product"].create(vals)

    @classmethod
    def _create_picking(cls, picking_type):
        vals = {}
        if picking_type.code == "incoming":
            vals.update(
                {
                    "partner_id": cls.supplier.id,
                    "picking_type_id": cls.picking_type_in.id,
                    "location_id": cls.supplier_location.id,
                }
            )
        if picking_type.code == "internal":
            vals.update(
                {
                    "picking_type_id": cls.picking_type_int.id,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.shelf_location.id,
                }
            )
        if picking_type.code == "outgoing":
            vals.update(
                {
                    "partner_id": cls.customer.id,
                    "picking_type_id": cls.picking_type_customer.id,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                }
            )
        return (
            cls.env["stock.picking"]
            .with_context(default_picking_type_id=picking_type.id)
            .create(vals)
        )

    @classmethod
    def _create_move(cls, picking, product=None, qty=1.0):
        cls.move = cls.env["stock.move"].create(
            {
                "name": "test-{product}".format(product=product.name),
                "product_id": product.id,
                "picking_id": picking.id,
                "picking_type_id": picking.picking_type_id.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )

    @classmethod
    def _create_lots_for_product(cls, product, lots_name):
        vals_list = [
            {"product_id": product.id, "name": x, "company_id": cls.env.company.id}
            for x in lots_name
        ]
        return cls.env["stock.production.lot"].create(vals_list)

    @classmethod
    def _create_quant_for_lot(cls, lots):
        vals_list = [
            {
                "product_id": x.product_id.id,
                "location_id": cls.stock_location.id,
                "quantity": 1.0,
                "lot_id": x.id,
            }
            for x in lots
        ]
        return cls.env["stock.quant"].create(vals_list)
