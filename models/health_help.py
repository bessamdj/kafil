# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HealthHelp(models.Model):
    _name = "health.help"
    _description = "Health Help"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ref'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {
        'approved': [('readonly', True)],
        'not_approved': [('readonly', True)],
    }

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))

    date = fields.Date('Obs. Date', default=fields.Datetime.now)
    type = fields.Selection([('chronic', 'Chronic'), ('handicap', 'Handicap'), ('other', 'Other'), ],
                                      string='Physical type',)
    to_be_followed = fields.Boolean('State to be followed')
    caretaker_id = fields.Many2one('kafil.caretaker', string='Caretaker')
    for_orphan = fields.Boolean('Is for Orphan', default=False)
    orphan_id = fields.Many2one('kafil.orphan', string='Orphan')
    related_state = fields.Many2one('health.physical.diseases', string='Disease',  domain="[('type', '=', type)]")

    doctor = fields.Many2one('res.doctor', string='Doctor or clinic')
    type_of_price = fields.Selection([('free','Free'), ('none','None'), ('reduced','Reduced price'),
                                      ('pay_after','Pay After')], default='doctor.type_of_help')
    type_of_help = fields.Many2one("type.health.help", string='Type of help', )
    amount = fields.Float('Amount', states=READONLY_STATES)
    aide_origin = fields.Many2one('aide.reception.money', states=READONLY_STATES)
    type = fields.Selection([('cash', 'Cash'), ('check', 'Check'), ], states=READONLY_STATES)
    number = fields.Char('Number / Bank', states=READONLY_STATES)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('medical.help') or _('New')
        result = super(HealthHelp, self).create(vals)
        return result

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_disapproved(self):
        self.write({'state': 'not_approved'})


class HealthMentalHelp(models.Model):
    _name = "health.mental.help"
    _description = "Mental Help"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('not_approved', 'Not Approved'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {
        'approved': [('readonly', True)],
        'not_approved': [('readonly', True)],
    }

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    date = fields.Date('Obs. Date', default=fields.Datetime.now)
    to_be_followed = fields.Boolean('State to be followed')
    caretaker_id = fields.Many2one('kafil.caretaker', string='Caretaker')
    for_orphan = fields.Boolean('Is for Orphan')
    orphan_id = fields.Many2one('kafil.orphan', string='Orphan')
    related_moral_state = fields.Many2one('health.mental.disorder')

    doctor = fields.Many2one('res.doctor', string='Doctor or clinic')
    type_of_price = fields.Selection([('free','Free'), ('none','None'), ('reduced','Reduced price'),
                                      ('pay_after','Pay After')], default='doctor.type_of_help')
    amount = fields.Float('Amount', states=READONLY_STATES)
    aide_origin = fields.Many2one('aide.reception.money', states=READONLY_STATES)
    type = fields.Selection([('cash', 'Cash'), ('check', 'Check'), ], states=READONLY_STATES)
    number = fields.Char('Number / Bank', states=READONLY_STATES)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('mental.help') or _('New')
        result = super(HealthMentalHelp, self).create(vals)
        return result

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_disapproved(self):
        self.write({'state': 'not_approved'})


class ResDoctor(models.Model):
    _name = 'res.doctor'
    _description = "Doctors / Clinics"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def default_country_id(self):
        company = self.env.company
        country = company[0].partner_id.country_id
        domain = country.id
        return domain

    name = fields.Char('Name',)
    speciality = fields.Char()
    street = fields.Char('Street ...', readonly=False)
    street2 = fields.Char('Street 2...', readonly=False)
    city = fields.Char('City', readonly=False)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=', country)]", readonly=False)
    country = fields.Many2one('res.country', string='Country', ondelete='restrict', default=default_country_id)
    phone = fields.Char()
    type_of_payment = fields.Selection([('free','Free'), ('none','None'), ('reduced','Reduced price'), ('pay_after','Pay After'),])



class TypeHealthHelp(models.Model):
    _name = 'type.health.help'
    _description = "Type of health help"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', help='')
    type = fields.Selection([('home_appliances','Home appliances'), ('home_improvement','Home improvement'),
                             ('wedding','Wedding'),('computer_office','Computer/office tools'),('other','Other'),],
                            string='Type', help='')
