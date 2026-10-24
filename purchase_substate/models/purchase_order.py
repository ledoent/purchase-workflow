# Copyright 2019 Akretion
# Copyright 2020 Ecosoft (<http://ecosoft.co.th>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import ClassVar

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("purchase.order", "Purchase Order")],
        ondelete={"purchase.order": "cascade"},
    )


class PurchaseOrder(models.Model):
    _inherit: ClassVar[list[str]] = ["purchase.order", "base.substate.mixin"]
    _name = "purchase.order"
    _state_field = "state"
