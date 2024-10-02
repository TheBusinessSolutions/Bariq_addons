from odoo import fields, models, api, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        user = self.env.user
        if user.has_group('eg_warehouse_restriction.group_warehouse_restriction_for_users'):
            args += [('id', 'in', user.warehouse_ids.ids)]
        return super(StockWarehouse, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
