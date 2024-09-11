import logging

from odoo.exceptions import ValidationError
from odoo.tests import common

_logger = logging.getLogger(__name__)


class TestTransfert(common.TransactionCase):
    def setUp(self):

        super(TestTransfert, self).setUp()

        # cree l'entrepot
        self.entrepot = self.env["stock.warehouse"].create(
            {"name": "TEST_WAREHOUSE", "code": "TEST"}
        )

        self.default_location = self.entrepot.mapped("view_location_id")

        # cree emplacement 1
        self.location1 = self.env["stock.location"].create(
            {
                "name": "LOCATION TEST 1",
                "location_id": self.default_location.id,
                "usage": "internal",
            }
        )

        # cree emplacement 2
        self.location2 = self.env["stock.location"].create(
            {
                "name": "LOCATION TEST 2",
                "location_id": self.default_location.id,
                "usage": "internal",
            }
        )

        # create 1 article
        self.article = self.env["product.product"].create(
            {"name": "article test", "sale_ok": True, "type": "product"}
        )

        # create a new sequence for picking type
        sequence = self.env["ir.sequence"].create(
            {
                "name": "Test entrepot",
                "code": "stock.picking",
                "prefix": "TESTSTOCKPICKING",
                "padding": 2,
                "number_increment": 1,
                "number_next_actual": 1,
                "implementation": "standard",
            }
        )

        # create a new picking type
        self.picking_type = self.env["stock.picking.type"].create(
            {
                "name": "TYPE PICKING TEST",
                "code": "internal",
                "sequence_id": sequence.id,
                "warehouse_id": self.entrepot.id,
            }
        )

        # provisionne l'emplacement location1
        # create a new transfert
        inventory_location = self.env.ref("stock.location_inventory")
        transfert = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type.id,
                "location_id": inventory_location.id,
                "location_dest_id": self.location1.id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": self.article.id,
                "product_uom": 1,
                "product_uom_qty": 100,
                "name": self.article.name,
                "picking_id": transfert.id,
                "location_id": inventory_location.id,
                "location_dest_id": self.location1.id,
            }
        )
        transfert.action_confirm()
        transfert.action_done()

        # cree les utilisateurs de test
        self.user1 = self.env["res.users"].create(
            {
                "name": "Utilisateur 1",
                "login": "user01@test.com",
                "email": "user01@test.com",
            }
        )

        self.user2 = self.env["res.users"].create(
            {
                "name": "Utilisateur 2",
                "login": "user02@test.com",
                "email": "user02@test.com",
            }
        )

        group_user_warehouse = self.env.ref("stock.group_stock_user")
        group_user_warehouse.users |= self.user1
        group_user_warehouse.users |= self.user2

    # @common.post_install(True)
    def test_do_transfert(self):
        """Teste la creation d'un transfert."""

        # create a new transfert
        transfert = (
            self.env["stock.picking"]
            .sudo(self.user1)
            .create(
                {
                    "picking_type_id": self.picking_type.id,
                    "location_id": self.location1.id,
                    "location_dest_id": self.location2.id,
                }
            )
        )

        self.env["stock.move"].sudo(self.user1).create(
            {
                "product_id": self.article.id,
                "product_uom": 1,
                "product_uom_qty": 100,
                "name": self.article.name,
                "picking_id": transfert.id,
                "location_id": self.location1.id,
                "location_dest_id": self.location2.id,
            }
        )

        # confirme le mouvement
        transfert.action_confirm()
        self.assertEqual(transfert.state, "confirmed")

        transfert.action_assign()
        self.assertEqual(transfert.state, "assigned")

        transfert.action_done()
        self.assertEqual(transfert.state, "done")

    @common.post_install(True)
    def test_do_transfert_restrict(self):
        """Teste la restriction de l'emplacement lors d'un transfert."""

        self.location2.allowed_users |= self.user2

        # create a new transfert
        transfert = (
            self.env["stock.picking"]
            .sudo(self.user1)
            .create(
                {
                    "picking_type_id": self.picking_type.id,
                    "location_id": self.location1.id,
                    "location_dest_id": self.location2.id,
                }
            )
        )

        self.env["stock.move"].sudo(self.user1).create(
            {
                "product_id": self.article.id,
                "product_uom": 1,
                "product_uom_qty": 100,
                "name": self.article.name,
                "picking_id": transfert.id,
                "location_id": self.location1.id,
                "location_dest_id": self.location2.id,
            }
        )

        # confirme le mouvement
        transfert.action_confirm()
        self.assertEqual(transfert.state, "confirmed")

        transfert.action_assign()
        self.assertEqual(transfert.state, "assigned")

        try:
            transfert.action_done()
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        transfert.sudo(self.user2).action_done()
        self.assertEqual(transfert.state, "done")
