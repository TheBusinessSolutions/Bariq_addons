# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, common, new_test_user
from odoo.tests.common import users


class TestStockProductSet(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.product_a = cls.env["product.product"].create(
            {"name": "Test product A", "type": "product"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Test product B", "type": "product"}
        )
        cls.product_set = cls.env["product.set"].create(
            {
                "name": "Test product set",
                "set_line_ids": [
                    (0, 0, {"product_id": cls.product_a.id, "quantity": 2}),
                    (0, 0, {"product_id": cls.product_b.id, "quantity": 1}),
                ],
            }
        )
        cls.picking_type_internal = cls.env.ref("stock.picking_type_internal")
        cls.picking_type_internal.default_location_dest_id = cls.env.ref(
            "stock.stock_location_components"
        )
        new_test_user(cls.env, login="test-stock-user", groups="stock.group_stock_user")

    @users("test-stock-user")
    def test_wizard_product_set_add_1(self):
        picking_form = Form(
            self.env["stock.picking"].with_context(
                default_picking_type_id=self.picking_type_internal.id
            )
        )
        picking = picking_form.save()
        wizard_form = Form(
            self.env["product.set.add.from.picking"].with_context(
                default_picking_id=picking.id
            )
        )
        wizard_form.product_set_id = self.product_set
        wizard = wizard_form.save()
        wizard.add_set()
        self.assertEqual(len(picking.move_ids_without_package), 2)
        products = picking.move_ids_without_package.mapped("product_id")
        self.assertIn(self.product_a, products)
        self.assertIn(self.product_b, products)
        self.assertEqual(
            sum(picking.move_ids_without_package.mapped("product_uom_qty")), 3
        )
