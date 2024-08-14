# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from lxml import etree
from datetime import datetime

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
from datetime import datetime

from odoo.addons.base.models.ir_ui_view import (
    transfer_modifiers_to_node,
    transfer_node_to_modifiers,
)
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
        readonly=True,  # Making the field read-only
    )

    is_lot_number_propagated = fields.Boolean(
        default=False,
        readonly=True,
        help=(
            "Lot/lot number is propagated "
            "from a component to the finished product."
        ),
    )
    propagated_lot_producing = fields.Char(
        compute="_compute_propagated_lot_producing"
    )

    @api.depends(
        "move_raw_ids.propagate_lot_number",
        "move_raw_ids.move_line_ids.qty_done",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        for order in self:
            day = str(fields.date.today().day)
            month = str(fields.date.today().month)
            code = ''
            sequence = self.env['ir.sequence'].next_by_code('mrp.production') or ''

            propagated = False  # Flag to check if lot number is propagated

            for move in order.move_raw_ids:
                for line in move.move_line_ids.filtered(lambda l: l.qty_done > 0):
                    barcode = str(line.product_id.material_code) if line.product_id.material_code else ''

                    for shift in self.env['shift.weight'].search([]):
                        time_format = "%I:%M %p"
                        time_now = datetime.strptime(datetime.now().strftime(time_format), time_format)
                        start_shift = datetime.strptime(f"{shift.start_hour}:{shift.start_minute} {shift.start_type}",
                                                        time_format)
                        end_shift = datetime.strptime(f"{shift.end_hour}:{shift.end_minute} {shift.end_type}",
                                                      time_format)

                        if start_shift <= end_shift and start_shift <= time_now <= end_shift:
                            code = shift.code
                        if not start_shift <= end_shift and (time_now >= start_shift or time_now <= end_shift):
                            code = shift.code

                    # Combine the components to form the lot name
                    lot_name = barcode + day + month + code + sequence

                    # Assign the lot name to the propagated_lot_producing field
                    order.propagated_lot_producing = lot_name
                    propagated = True  # Mark as propagated

            # Update the is_lot_number_propagated flag
            order.is_lot_number_propagated = propagated

            if not propagated:
                order.propagated_lot_producing = False
                order.is_lot_number_propagated = False

    @api.onchange("bom_id")
    def _onchange_bom_id_lot_number_propagation(self):
        self.is_lot_number_propagated = self.bom_id.lot_number_propagation

    def action_confirm(self):
        res = super().action_confirm()
        self._set_lot_number_propagation_data_from_bom()
        return res

    def _get_propagating_component_move(self):
        self.ensure_one()
        return self.move_raw_ids.filtered(lambda o: o.propagate_lot_number)

    def _set_lot_number_propagation_data_from_bom(self):
        """Copy information from BoM to the manufacturing order."""
        for order in self:
            propagate_lot = order.bom_id.lot_number_propagation
            if not propagate_lot:
                continue
            order.is_lot_number_propagated = propagate_lot
            propagate_move = order.move_raw_ids.filtered(
                lambda m: m.bom_line_id.propagate_lot_number
            )
            if not propagate_move:
                raise UserError(
                    _(
                        "Bill of material is marked for lot number propagation, but "
                        "there are no components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            elif len(propagate_move) > 1:
                raise UserError(
                    _(
                        "Bill of material is marked for lot number propagation, but "
                        "there are multiple components propagating lot number. "
                        "Please check BOM configuration."
                    )
                )
            else:
                propagate_move.propagate_lot_number = True

    def _post_inventory(self, cancel_backorder=False):
        self._create_and_assign_propagated_lot_number()
        return super()._post_inventory(cancel_backorder=cancel_backorder)

    def _create_and_assign_propagated_lot_number(self):
        for order in self:
            if not order.is_lot_number_propagated or order.lot_producing_id:
                continue
            finish_moves = order.move_finished_ids.filtered(
                lambda m: m.product_id == order.product_id
                          and m.state not in ("done", "cancel")
            )
            if finish_moves and not finish_moves.quantity_done:
                lot_model = self.env["stock.production.lot"]
                lot = lot_model.search(
                    [
                        ("product_id", "=", order.product_id.id),
                        ("company_id", "=", order.company_id.id),
                        ("name", "=", order.propagated_lot_producing),
                    ],
                    limit=1,
                )
                if lot.quant_ids:
                    raise UserError(
                        _(
                            "Lot/lot number %s already exists and has been used. "
                            "Unable to propagate it."
                        )
                    )
                if not lot:
                    lot = self.env["stock.production.lot"].create(
                        {
                            "product_id": order.product_id.id,
                            "company_id": order.company_id.id,
                            "name": order.propagated_lot_producing,
                        }
                    )
                order.with_context(lot_propagation=True).lot_producing_id = lot

    def write(self, vals):
        for order in self:
            if (
                    order.is_lot_number_propagated
                    and "lot_producing_id" in vals
                    and not self.env.context.get("lot_propagation")
            ):
                raise UserError(
                    _(
                        "Lot/lot number is propagated from a component, "
                        "you are not allowed to change it."
                    )
                )
        return super().write(vals)

    def fields_view_get(
            self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # Override to hide the "lot_producing_id" field + "action_generate_lot"
        # button if the MO is configured to propagate a lot number
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if result.get("name") in self._views_to_adapt():
            result["arch"] = self._fields_view_get_adapt_lot_tags_attrs(result)
        return result

    def _views_to_adapt(self):
        """Return the form view names bound to 'mrp.production' to adapt."""
        return ["mrp.production.form"]

    def _fields_view_get_adapt_lot_tags_attrs(self, view):
        """Hide elements related to lot if it is automatically propagated."""
        doc = etree.XML(view["arch"])
        tags = (
            "//label[@for='lot_producing_id']",
            "//field[@name='lot_producing_id']/..",  # parent <div>
        )
        for xpath_expr in tags:
            attrs_key = "invisible"
            nodes = doc.xpath(xpath_expr)
            for field in nodes:
                attrs = safe_eval(field.attrib.get("attrs", "{}"))
                if not attrs[attrs_key]:
                    continue
                invisible_domain = expression.OR(
                    [attrs[attrs_key], [("is_lot_number_propagated", "=", True)]]
                )
                attrs[attrs_key] = invisible_domain
                field.set("attrs", str(attrs))
                modifiers = {}
                transfer_node_to_modifiers(field, modifiers, self.env.context)
                transfer_modifiers_to_node(modifiers, field)
        return etree.tostring(doc, encoding="unicode")

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

    def reset_weight_1(self):
        self.weight_1 = 0.0
        self.is_get_weight_1 = False
        for record in self.move_raw_ids.move_line_ids:
            record.qty_done = 0.0

    def action_generate_lots_name(self):
        day = str(fields.date.today().day)
        month = str(fields.date.today().month)
        code = ''
        ticket = str(self.weight_id.code)
        sequence = str(self.weight_id.sequence_id._next()) if self.weight_id.sequence_id else ''

        for record in self.move_raw_ids.move_line_ids:
            barcode = str(record.product_id.material_code) if record.product_id.material_code else ''

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
        material_code = self.product_id.product_tmpl_id.material_code

        # Combine the material_code and weight_ticket_number without any separation characters
        if self.weight_ticket_number:
            name = f"{material_code}{self.weight_ticket_number}"

        # Create the lot/serial with the combined name
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
