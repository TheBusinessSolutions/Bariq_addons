from odoo import _, models
from odoo.exceptions import ValidationError

TEMP_MOVE_RESTRICT = _(
    """Only the users: %s \n """ """are allowed to do transfert %s this location"""
)


class StockMove(models.Model):
    """."""

    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        """."""
        uid = self.env.user.id
        for record in self:
            srcl = record.location_id
            dstl = record.location_dest_id

            if srcl.allowed_users and uid not in srcl.allowed_users.ids:
                allowed = ",".join(srcl.allowed_users.mapped("name"))
                raise ValidationError(TEMP_MOVE_RESTRICT % (allowed, "from"))

            if dstl.allowed_users and uid not in dstl.allowed_users.ids:
                allowed = ",".join(dstl.allowed_users.mapped("name"))
                raise ValidationError(TEMP_MOVE_RESTRICT % (allowed, "to"))
            super(StockMove, record)._action_done(cancel_backorder)
