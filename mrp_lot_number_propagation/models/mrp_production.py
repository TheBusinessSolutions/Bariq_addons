from lxml import etree
from datetime import datetime
import socket
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare

from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    weight_id = fields.Many2one('stock.weight', string='Weight type')
    weight_1 = fields.Float(string="Weight")
    is_get_weight_1 = fields.Boolean(string='Is Get Weight')

    weight_ticket_number = fields.Char(readonly=True, string="Ticket Number")
    is_generate_lots = fields.Boolean(string="Is Generate Lots", default=False)
    lot_producing_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number',
        copy=False,
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id)]",
        check_company=True,
        readonly=True,
    )

    is_lot_number_propagated = fields.Boolean(
        default=False,
        readonly=True,
        help=(
            "Lot/Serial number is propagated "
            "from a component to the finished product."
        ),
    )
    propagated_lot_producing = fields.Char(
        compute="_compute_propagated_lot_producing",
        store=True,
        help=(
            "The lot/serial number for the finished product is automatically generated "
            "based on the material code and the weight ticket number."
        ),
    )

    @api.depends("weight_ticket_number", "product_id")
    def _compute_propagated_lot_producing(self):
        for order in self:
            if order.weight_ticket_number and order.product_id:
                material_code = order.product_id.product_tmpl_id.material_code if hasattr(
                    order.product_id.product_tmpl_id, 'material_code') else ""
                lot_name = f"{material_code}{order.weight_ticket_number}"

                # Check if the lot/serial number already exists
                existing_lot = self.env['stock.production.lot'].search([
                    ('product_id', '=', order.product_id.id),
                    ('company_id', '=', order.company_id.id),
                    ('name', '=', lot_name),
                ], limit=1)

                if existing_lot:
                    order.lot_producing_id = existing_lot
                else:
                    # Create a new lot/serial number if it doesn't exist
                    lot = self.env['stock.production.lot'].create({
                        'product_id': order.product_id.id,
                        'company_id': order.company_id.id,
                        'name': lot_name,
                    })
                    order.lot_producing_id = lot

                order.propagated_lot_producing = lot_name

    def action_generate_lots_name(self):
        if not self.weight_id:
            raise UserError(_('Weight ID is missing. Please configure the Weight ID before generating lots.'))

        # Check if there are backorders
        if self.move_finished_ids.filtered(lambda move: move.state == 'waiting'):
            self.weight_ticket_number = False
            return

        day = str(fields.date.today().day)
        month = str(fields.date.today().month)
        code = ''
        ticket = str(self.weight_id.code)
        sequence = str(self.weight_id.sequence_id._next()) if self.weight_id.sequence_id else ''

        for record in self.move_raw_ids.move_line_ids:
            barcode = str(record.product_id.material_code) if hasattr(record.product_id, 'material_code') else ''

            for shift in self.env['shift.weight'].search([]):
                time_format = "%I:%M %p"
                time_now = datetime.strptime(datetime.now().strftime(time_format), time_format)
                start_shift = datetime.strptime(f"{shift.start_hour}:{shift.start_minute} {shift.start_type}",
                                                time_format)
                end_shift = datetime.strptime(f"{shift.end_hour}:{shift.end_minute} {shift.end_type}", time_format)

                if start_shift <= end_shift and start_shift <= time_now <= end_shift:
                    code = shift.code
                if not start_shift <= end_shift and (time_now >= start_shift or time_now <= end_shift):
                    code = shift.code

            record.lot_name = barcode + day + month + code + ticket + sequence

        self.weight_ticket_number = day + month + code + ticket + sequence
        self.is_generate_lots = True

        material_code = self.product_id.product_tmpl_id.material_code if hasattr(self.product_id.product_tmpl_id,
                                                                                 'material_code') else ""
        lot_name = f"{material_code}{self.weight_ticket_number}"

        # Check if the lot/serial number already exists
        existing_lot = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('name', '=', lot_name),
        ], limit=1)

        if existing_lot:
            self.lot_producing_id = existing_lot
        else:
            # Create a new lot/serial number if it doesn't exist
            self.lot_producing_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': lot_name,
            })

    def button_mark_done(self):
        # Ensure that weight_1 is fetched before marking done
        if not self.weight_1:
            raise UserError(_('You Must Get Track Weight First Before Marking Done.'))

        # Apply logic for weight
        for record in self.move_raw_ids.move_line_ids:
            record.qty_done = abs(self.weight_1)

        return super(MrpProduction, self).button_mark_done()

    def action_generate_serial(self):
        self.ensure_one()
        if self.product_id.tracking == 'none':
            return

        # Fetch the standard serial name
        name = self.env['stock.production.lot']._get_new_serial(self.company_id, self.product_id)

        # Fetch the material_code from product.template
        material_code = self.product_id.product_tmpl_id.material_code if hasattr(self.product_id.product_tmpl_id,
                                                                                 'material_code') else ""

        # Combine the material_code and weight_ticket_number without any separation characters
        if self.weight_ticket_number:
            name = f"{material_code}{self.weight_ticket_number}"

        # Check if the lot/serial number already exists
        existing_lot = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product_id.id),
            ('company_id', '=', self.company_id.id),
            ('name', '=', name),
        ], limit=1)

        if existing_lot:
            self.lot_producing_id = existing_lot
        else:
            # Create the lot/serial with the combined name if it doesn't exist
            self.lot_producing_id = self.env['stock.production.lot'].create({
                'product_id': self.product_id.id,
                'company_id': self.company_id.id,
                'name': name,
            })

        # If tracking by serial, adjust the quantity to produce
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()

    @api.onchange('weight_1')
    def _onchange_weight_1(self):
        if self.weight_1:
            self.qty_producing = abs(self.weight_1)

    def get_weight_1(self):
        if not self.weight_id:
            raise UserError("Weight configuration is missing. Please ensure that a valid Weight ID is set.")
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.weight_id.ip_addr, int(self.weight_id.port)))

            response = client.recv(1024)
            response = response.decode("utf-8")

            if not response.isdigit():
                raise UserError("Invalid Return Response %s" % response)

            try:
                self.weight_1 = float(response)
                self.is_get_weight_1 = True
            except:
                self.weight_1 = 0.0
                self.is_get_weight_1 = False

            client.close()

        except Exception as e:
            raise UserError("We Can't Process Request: (%s)" % e)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id

            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits)
                for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
            )
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding)
                for move_line in picking.move_line_ids
            )

            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding)
                    )
                for line in lines_to_check:
                    product = line.product_id


        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())

        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit mode and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        pickings_not_to_backorder = self.env['stock.picking']
        pickings_to_backorder = self

        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda
                                                 m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search(
                    [('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.ids),
                     ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                    ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                    ('product_qty', '>', 0),
                    ('location_id', 'in', wh_location_ids),
                    ('move_orig_ids', '=', False),
                    ('picking_id', 'not in', self.ids),
                    ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
        return True

    def _pre_action_done_hook(self):
        pickings_to_immediate = self._check_immediate()
        if pickings_to_immediate:
            return pickings_to_immediate._action_generate_immediate_wizard(show_transfers=self._should_show_transfers())

        pickings_to_backorder = self._check_backorder()
        if pickings_to_backorder:
            return pickings_to_backorder._action_generate_backorder_wizard(show_transfers=self._should_show_transfers())
        return True

    def _should_show_transfers(self):
        """Whether the different transfers should be displayed on the pre action done wizards."""
        return len(self) > 1

    def _get_without_quantities_error_message(self):
        """ Returns the error message raised in validation if no quantities are reserved or done.
        The purpose of this method is to be overridden in case we want to adapt this message.

        :return: Translated error message
        :rtype: str
        """
        return _(
            'You cannot validate a transfer if no quantities are reserved nor done. '
            'To force the transfer, switch in edit mode and encode the done quantities.'
        )