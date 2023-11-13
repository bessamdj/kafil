# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import warnings

from datetime import date, timedelta

class KafilOrphan(models.Model):
    _name = 'kafil.orphan'
    _description = 'Orphan'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def calculate_age(self):
        for rec in self:
            today = date.today()
            born = rec.date_birth
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            rec.age = age

    name = fields.Char ('Name', required=True)
    image = fields.Binary(string="Image", attachment=True)
    date_birth = fields.Date ("Date of Birth", required=True)
    age = fields.Integer ('Age', compute='calculate_age')
    gender = fields.Selection ([('male','Male'),('female','Female')], string="Sexe", required=True)
    active = fields.Boolean("Active", related='caretaker.active', default=True)
    whatsapp = fields.Char(string="WhatsApp")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    school_year = fields.Many2one('kafil.orphan.years',)
    caretaker = fields.Many2one('kafil.caretaker', string='Caretaker', required=True)
    company_id = fields.Many2one(related='caretaker.company_id', string='Company', store=True, readonly=True, index=True)
    years_line = fields.One2many('kafil.orphan.year', 'orphan', string='Years Lines', copy=True)
    dropout_graduate = fields.Boolean('Graduate/Dropbout', default=False)
    education = fields.One2many('kafil.education', 'orphan_id', string='Education', copy=True )
    physical_h = fields.One2many('health.physical', 'orphan_id', string='Physical Health', copy=True )
    mental_h = fields.One2many('health.mental', 'orphan_id', string='Mental Health', copy=True )

    @api.onchange('school_year')
    def onchange_school_year(self):
        comp = self.school_year.order
        h = 0
        for rec in self.years_line:
            #if comp < rec.order:
            #    self.years_line = [(3, rec.id)]
            if comp > rec.order and h < rec.order :
                h = rec.order
        if h != comp:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': _("Your time off has been canceled."),
                    'sticky': True,
                            }
                    }
        else:
            return False
#            for x in range (h, comp) :
#            search_id = self.env['kafil.orphan.years'].search(
#                [('order', '=', x)], limit=1)
#            self.years_line = [(0,0, {'order': search_id.order,'year': search_id.id})]

    @api.onchange('years_line')
    def onchange_years_line(self):
        h = 0
        for rec in self.years_line:
            if h < rec.order:
                h = rec.order
        if h != self.school_year.order:
            search_id = self.env['kafil.orphan.years'].search(
                [('order', '=', h)], limit=1)
            self.school_year = search_id

    @api.onchange('date_birth')
    def onchange_date_birth(self):
        for record in self:
            sc_age = self.age - 6
            if sc_age >= 0 :
                search_id = self.env['kafil.orphan.years'].search(
                [('order', '=', sc_age)],limit=1)
                record.school_year = search_id
                i = 0
                while i < sc_age:
                    i += 1
                    search_yr = self.env['kafil.orphan.years'].search(
                        [('order', '=', i)], limit=1)
                    #record.years_line.year += search_yr
            else:
                search_id = self.env['kafil.orphan.years'].search(
                    [('order', '=', 0)], limit=1)
                record.school_year = search_id


class KafilOrphanYear(models.Model):
    _name = 'kafil.orphan.year'
    _description = 'School'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order = fields.Integer(related='year.order', index='trigram', default=1)
    year = fields.Many2one('kafil.orphan.years', required=True, index='trigram')
    first = fields.Float('First Trimester')
    second = fields.Float('Second Trimester')
    third = fields.Float('Third Trimester')
    difficult_classes = fields.Many2many('kafil.orphan.classes')
    help_needed = fields.Char('Need')
    orphan = fields.Many2one('kafil.orphan', index=True, required=True, ondelete='cascade')


class KafilOrphanClasses(models.Model):
    _name = 'kafil.orphan.classes'
    _description = "Classes"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Classe')


class KafilOrphanYears(models.Model):
    _name = 'kafil.orphan.years'
    _description = "Years"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Years', required=True, index=True, translate=True)
    order = fields.Integer('Order', required=True,  )

