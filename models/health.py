# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HealthPhysical(models.Model):
    _name = "health.physical"
    _description = "Physical Health"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date('Obs. Date', default=fields.Datetime.now)
    good = fields.Selection([('good', 'Good'), ('bad', 'Bad'), ('issues', 'Minor Issues')], string='State')
    type = fields.Many2one('health.physical.diseases', string='Disease',   domain="[('type', '=', category)]")
    category = fields.Selection (related='type.type', readonly=False)
    follow = fields.Many2one('res.partner',  domain="[('is_member', '=', True)]")
    medic_needs = fields.Char('Medical needs')
    caretaker_id = fields.Many2one('kafil.caretaker', string='Caretaker')
    orphan_id = fields.Many2one('kafil.orphan', string='Orphan')


class HealthPhysicalDiseases(models.Model):
    _name = "health.physical.diseases"
    _description = "Physical Health"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    type = fields.Selection ([('chronic', 'Chronic'), ('handicap', 'Handicap'), ('other', 'Other'), ], default='other')


class HealthMental(models.Model):
    _name = "health.mental"
    _description = "Mental Health"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date('Obs. Date', default=fields.Datetime.now)
    is_good = fields.Selection([('good', 'Good'), ('bad', 'Bad'), ('issues', 'Minor Issues')], string='State')
    disorder = fields.Many2one('health.mental.disorder', string='Psychological Disorder')
    reason = fields.Char('Reason & causes')
    mood = fields.Selection([('calm','Calm'),('nervous','Nervous'),('heavy','Heavy'),])
    follow = fields.Many2one('res.partner', domain="[('is_member', '=', True)]")
    caretaker_id = fields.Many2one('kafil.caretaker', string='Caretaker')
    orphan_id = fields.Many2one('kafil.orphan', string='Orphan')


class HealthMentalDisorder(models.Model):
    _name = "health.mental.disorder"
    _description = "Mental Health Disorder"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Disorder')

# --- receiving

