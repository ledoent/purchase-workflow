# Copyright 2019 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSubstate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.substate_test_purchase = cls.env["purchase.order"]
        cls.substate_test_purchase_line = cls.env["purchase.order.line"]

        cls.base_substate = cls.env["base.substate"]
        cls.target_draft = cls.env.ref("purchase_substate.target_state_value_draft")
        cls.target_purchase = cls.env.ref(
            "purchase_substate.target_state_value_purchase"
        )
        # Build the substates here rather than env.ref'ing the demo records:
        # Odoo stopped loading demo data by default in 19.0, so the refs this
        # test used raised "External ID not found". Negative sequences keep
        # these ahead of the demo substates when demo IS loaded, so the
        # defaults the assertions rely on stay deterministic either way.
        cls.substate_under_nego = cls.base_substate.create(
            {
                "name": "In negotiation",
                "sequence": -20,
                "target_state_value_id": cls.target_draft.id,
            }
        )
        cls.substate_won = cls.base_substate.create(
            {
                "name": "Won",
                "sequence": -10,
                "target_state_value_id": cls.target_draft.id,
            }
        )
        cls.substate_wait_docs = cls.base_substate.create(
            {
                "name": "Waiting for legal documents",
                "sequence": -5,
                "target_state_value_id": cls.target_draft.id,
            }
        )
        cls.substate_valid_docs = cls.base_substate.create(
            {
                "name": "To validate legal documents",
                "sequence": -20,
                "target_state_value_id": cls.target_purchase.id,
            }
        )
        cls.substate_in_receipt = cls.base_substate.create(
            {
                "name": "In receipt",
                "sequence": -10,
                "target_state_value_id": cls.target_purchase.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test vendor"})

        cls.product = cls.env["product.product"].create({"name": "Test"})

    def test_purchase_order_substate(self):
        po_test1 = self.substate_test_purchase.create(
            {
                "name": "Test base substate to basic purchase",
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "line test",
                            "product_id": self.product.id,
                            "uom_id": self.product.uom_id.id,
                            "price_unit": 120.0,
                            "product_qty": 1.5,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        self.assertTrue(po_test1.state == "draft")
        self.assertTrue(po_test1.substate_id == self.substate_under_nego)

        # Block substate not corresponding to draft state
        with self.assertRaises(ValidationError):
            po_test1.substate_id = self.substate_valid_docs
        # Test that validation of purchase order change substate_id
        po_test1.button_confirm()
        self.assertTrue(po_test1.state == "purchase")
        self.assertTrue(po_test1.substate_id == self.substate_valid_docs)

        # Test that substate_id is set to false if
        # there is not substate corresponding to state
        po_test1.button_cancel()
        self.assertTrue(po_test1.state == "cancel")
        self.assertTrue(not po_test1.substate_id)
