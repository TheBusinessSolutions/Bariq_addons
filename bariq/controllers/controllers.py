# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo.http import request, Response, route
from datetime import datetime, date
from odoo import http
import requests
import json
import math

class BariqAPI(http.Controller):

    @route('/create/purchase/order', type='json', auth='public', methods=['POST'], sitemap=False, csrf=False)
    def create_purchase_order(self, **kw):
        data  = json.loads(request.httprequest.data)
        lines = []

        if not data.get('partner_id') or not data.get('dawar_ticket_number') or not data.get('driver_name') or not data.get('driver_license') or not data.get('truck_number') or not data.get('trailer_number') or not data.get('lines'):
            response = {"code": 400, "message": "API Body is not Correct", "data": {'body': data}}
            return response

        partner_id = request.env['res.partner'].sudo().search([('id', '=', data.get('partner_id'))], limit=1)
        if not partner_id:
            response = {"code": 400, "message": "Partner ID is not Found", "data": {'partner_id': data.get('partner_id')}}
            return response

        for line in data.get('lines').values():
            product_id = request.env['product.product'].sudo().search([('barcode', '=', line['product_code'])], limit=1)
            if not product_id:
                response = {"code": 400, "message": "Product Code is not Found", "data": {'product_id': line['product_code']}}
                return response

            lines.append((0, 6, {
                'product_id'  : product_id.id,
                'name'        : line['description'],
                'product_qty' : line['product_qty'],
                'bales_number': line['bales_number'],
                'price_unit'  : line['price_unit'],
            }))


        order_id = request.env['purchase.order'].sudo().create({
            'partner_id'     : partner_id.id,
            'partner_ref'    : data.get('dawar_ticket_number'),
            'driver_name'    : data.get('driver_name'),
            'driver_license' : data.get('driver_license'),
            'truck_number'   : data.get('truck_number'),
            'trailer_number' : data.get('trailer_number'),
            'order_line' : lines,
        })
        
        order_id.button_confirm()

        response = {"code": 200, "message": "Purchase Order Created Successfully", "data": {'purchase_id': order_id.id, 'purchase_name': order_id.name}}
        return response