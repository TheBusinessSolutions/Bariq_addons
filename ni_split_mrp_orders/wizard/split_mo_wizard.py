from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SplitMO(models.TransientModel):
    _name = "split.mo.wizard"

    split_mo_by = fields.Selection([('by_no', 'Number of split'), ('by_qty', 'Split By Quantity')], required=True)
    split_mo_no = fields.Integer('Split No/Qty', required=True)

    def btn_split(self):
        mrp_obj = self.env['mrp.production']
        active_id = self.env.context.get('active_id')

        current_mrp_data = mrp_obj.search([('id', '=', active_id)])

        if self.split_mo_by == 'by_no':
            split_mo_no = self.split_mo_no

            for i in range(0, split_mo_no):

                line_vals = {}
                mrp_line_data = []

                mrp_vals = {
                    'product_id': current_mrp_data.product_id.id,
                    'product_qty': current_mrp_data.product_qty / split_mo_no,
                    'date_planned_start': current_mrp_data.date_planned_start,
                    'company_id': current_mrp_data.company_id.id,
                    'origin': current_mrp_data.name,
                    'bom_id': current_mrp_data.bom_id.id,
                    'product_uom_id': current_mrp_data.product_uom_id.id,
                }

                for mo_line in current_mrp_data.bom_id.bom_line_ids:
                    line_vals = {'product_id': mo_line.product_id.id,
                                 'name': mo_line.product_id.name,
                                 'product_uom_qty': (
                                             mo_line.product_qty * (current_mrp_data.product_qty / split_mo_no)),
                                 'location_id': current_mrp_data.location_src_id.id,
                                 'location_dest_id': current_mrp_data.location_dest_id.id,
                                 'product_uom': current_mrp_data.product_uom_id.id}
                    mrp_line_data.append((0, 0, line_vals))

                    mrp_vals.update({'move_raw_ids': mrp_line_data})

                mrp_obj.create(mrp_vals)

            current_mrp_data.do_unreserve()
            current_mrp_data.state = 'cancel'

        elif self.split_mo_by == 'by_qty':
            split_mo_qty = self.split_mo_no
            print('split_mo_qty+++++++++', split_mo_qty)
            qty = int(current_mrp_data.product_qty) - int(split_mo_qty)

            change_production_qty_wizard_id = self.env['change.production.qty'].create({'product_qty': qty})
            change_production_qty_wizard_id.change_prod_qty()

            mrp_line_data = []

            mrp_vals = {
                'product_id': current_mrp_data.product_id.id,
                'product_qty': split_mo_qty,
                'date_planned_start': current_mrp_data.date_planned_start,
                'company_id': current_mrp_data.company_id.id,
                'origin': current_mrp_data.name,
                'bom_id': current_mrp_data.bom_id.id,
                'product_uom_id': current_mrp_data.product_uom_id.id,
            }

            for mo_line in current_mrp_data.bom_id.bom_line_ids:
                line_vals = {'product_id': mo_line.product_id.id,
                             'name': mo_line.product_id.name,
                             'product_uom_qty': (mo_line.product_qty * split_mo_qty),
                             'location_id': current_mrp_data.location_src_id.id,
                             'location_dest_id': current_mrp_data.location_dest_id.id,
                             'product_uom': current_mrp_data.product_uom_id.id}
                mrp_line_data.append((0, 0, line_vals))

                mrp_vals.update({'move_raw_ids': mrp_line_data})

            mrp_obj.create(mrp_vals)

        #
        # mrp_obj = self.env['mrp.production']
        # active_id = self.env.context.get('active_id')
        #
        # current_mrp_data = mrp_obj.search([('id', '=', active_id)])
        # qty_to_consumed = int(current_mrp_data.product_qty)
        # total_split_no = self.split_mo_no
        #
        # if total_split_no > qty_to_consumed:
        #     raise ValidationError(_("Please set the split qty less than the qty to produce"))
        # if total_split_no <= 1:
        #     raise ValidationError(_("Please set the qty greater than 1"))
        #
        # split_qty_list = []
        # if qty_to_consumed < total_split_no:
        #     print(-1)
        # elif qty_to_consumed % total_split_no == 0:
        #     for i in range(total_split_no):
        #         split_qty_list.append(qty_to_consumed // total_split_no)
        # else:
        #     zp = total_split_no - (qty_to_consumed % total_split_no)
        #     pp = qty_to_consumed // total_split_no
        #     for i in range(total_split_no):
        #         if i >= zp:
        #             split_qty_list.append(pp + 1)
        #         else:
        #             split_qty_list.append(pp)
        #
        # print('qty_to_consumed------', qty_to_consumed)
        # print('total_split_no------', total_split_no)
        # print('split_qty_list------', split_qty_list)
        #
        # change_production_qty_wizard_id = self.env['change.production.qty'].create({'product_qty': split_qty_list[0]})
        # change_production_qty_wizard_id.change_prod_qty()
        # # current_mrp_data.update({
        # #     'product_qty': split_qty_list[0],
        # # })
        # print('\ncurrent_mrp_data+++++++++++', current_mrp_data.id, current_mrp_data.product_id.name)
        #
        # mrp_bom_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', current_mrp_data.product_id.name)])
        # print('\nmrp_bom_obj++++++++++++', mrp_bom_obj)
        #
        # bom_com_product_list = []
        # bom_com_qty_list = []
        # for bom in mrp_bom_obj.bom_line_ids:
        #     print('\nbom+++++++++++++++', bom.product_id)
        #     bom_com_product_list.append(bom.product_id.id)
        #     bom_com_qty_list.append(bom.product_qty)
        #
        # # new_pro_up.update({'seller_ids': [(0, 0, {'min_qty': 1, 'name': partner_id, 'price': row[8]})]})
        # # vals.update({'move_raw_ids': [
        # #     (0, 0, {'product_uom_qty': (bom.product_qty * split_qty_list[i + 1]), 'product_id': j, })]})
        #
        # for i in range(0, total_split_no - 1, 1):
        #     print('i++++++++++++++++++++', split_qty_list[i + 1])
        #     vals = {
        #         'product_id': current_mrp_data.product_id.id,
        #         'product_qty': split_qty_list[i + 1],
        #         'date_planned_start': current_mrp_data.date_planned_start,
        #         'company_id': current_mrp_data.company_id.id,
        #         'origin': current_mrp_data.name,
        #         'bom_id': current_mrp_data.bom_id.id,
        #         'product_uom_id': current_mrp_data.product_uom_id.id,
        #     }
        #
        #     for j in zip(bom_com_product_list, bom_com_qty_list):
        #         product_name = self.env['product.product'].search([('id', '=', j[0])], limit=1)
        #
        #         # student = {'product_uom_qty': (j[i] * split_qty_list[i + 1]), 'product_id': j[0],
        #         #            'name': product_name.name,
        #         #            'location_id': current_mrp_data.location_src_id.id,
        #         #            'location_dest_id': current_mrp_data.location_dest_id.id,
        #         #            'product_uom': current_mrp_data.product_uom_id.id}
        #
        #         vals.update({'move_raw_ids': [
        #             (0, 0,
        #              {'product_uom_qty': (j[i] * split_qty_list[i + 1]), 'product_id': j[0], 'name': product_name.name,
        #               'location_id': current_mrp_data.location_src_id.id,
        #               'location_dest_id': current_mrp_data.location_dest_id.id,
        #               'product_uom': current_mrp_data.product_uom_id.id})]})
        #
        #     # vals.update(l)
        #
        #     mrp_obj.create(vals)
