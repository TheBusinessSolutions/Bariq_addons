# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError


class ShiftWeight(models.Model):
    _name = 'shift.weight'


    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)


    start_hour   = fields.Integer(string="Start Hour", required=True)
    start_minute = fields.Integer(string="Start Minute", required=True)
    start_type   = fields.Selection([('am', 'AM'), ('pm', 'PM')], string="Start Type", required=True)
    
    end_hour   = fields.Integer(string="End Hour", required=True)
    end_minute = fields.Integer(string="End Minute", required=True)
    end_type   = fields.Selection([('am', 'AM'), ('pm', 'PM')], string="End Type", required=True)

    @api.constrains('start_hour', 'start_minute', 'end_hour', 'end_minute')
    def check_time_value(self):
        for record in self:
            if not 1 <= record.start_hour <= 12:
                raise ValidationError("Start Hour Value Must be Between 1 - 12")

            if not 1 <= record.end_hour <= 12:
                raise ValidationError("End Hour Value Must be Between 1 - 12")

            if not 0 <= record.start_minute <= 59:
                raise ValidationError("Start Minute Value Must be Between 00 - 59")

            if not 0 <= record.end_minute <= 59:
                raise ValidationError("End Minute Value Must be Between 00 - 59")