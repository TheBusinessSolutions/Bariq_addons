# -*- coding: utf-8 -*-

from odoo.http import request, Response, route
from odoo import http
import datetime
import json
import jwt


def verify_jwt_token(token):
    secret_key = request.env['ir.config_parameter'].sudo().get_param('database.secret')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return None


class BariqAPI(http.Controller):


    @http.route('/api/authenticate', type='json', auth='none', methods=['POST'], csrf=False)
    def authenticate(self, **kwargs):
        data = json.loads(request.httprequest.data)
        
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            response = {"code": 400, "message": "Missing username or password", "data": {}}
            return response

        uid = request.session.authenticate(request.env.cr.dbname, username, password)

        if uid:
            secret_key = request.env['ir.config_parameter'].sudo().get_param('database.secret')
            payload = {'user_id': uid, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}
            token   = jwt.encode(payload, secret_key, algorithm='HS256')

            response = {"code": 200, "message": "Token Generated Successfully", "data": {'token': token}}
            return response
        else:
            response = {"code": 400, "message": "Invalid username or password", "data": {}}
            return response


    @route('/create/purchase/order', type='json', auth='public', methods=['POST'], sitemap=False, csrf=False)
    def create_purchase_order(self, **kw):
        token = request.httprequest.headers.get('Authorization')

        if not token:
            response = {"code": 200, "message": "Missing token", "data": {}}
            return response

        user_id = verify_jwt_token(token)
        
        if not user_id:
            response = {"code": 400, "message": "Invalid or expired token", "data": {}}
            return response

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
            product_id = request.env['product.product'].sudo().search([('material_code', '=', line['product_code'])], limit=1)
            if not product_id:
                response = {"code": 400, "message": "Product Code is not Found", "data": {'material_code': line['product_code']}}
                return response

            lines.append((0, 6, {
                'product_id'  : product_id.id,
                'name'        : line['description'],
                'product_qty' : line['product_qty'],
                'bales_number': line['bales_number'],
                'price_unit'  : line['price_unit'],
            }))


        order_id = request.env['purchase.order'].sudo().create({
            'is_dawar_purchase' : True,
            'partner_id'     : partner_id.id,
            'partner_ref'    : data.get('dawar_ticket_number'),
            'driver_name'    : data.get('driver_name'),
            'driver_license' : data.get('driver_license'),
            'truck_number'   : data.get('truck_number'),
            'trailer_number' : data.get('trailer_number'),
            'order_line'     : lines,
        })
        
        order_id.button_confirm()

        response = {"code": 200, "message": "Purchase Order Created Successfully", "data": {'purchase_id': order_id.id, 'purchase_name': order_id.name}}
        return response