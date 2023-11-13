# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AideServices(models.Model):
    _name = "aide.services"
    _rec_name = "ref"
    _description = "Aide in services of goods"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('delivered', 'Delivered'),
        ('not_approved', 'Not Approved'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {'approved': [('readonly', True)],
                        'delivered': [('readonly', True)],
                        'not_approved': [('readonly', True)],}

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    caretaker = fields.Many2one('kafil.caretaker')
    date = fields.Date('Date', default=fields.Datetime.now)
    amount = fields.Float ('Estimated Amount', )
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    type_of_services = fields.Many2one('type.services', string='Service type')
    partner = fields.Many2one('res.partner')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('aide.services') or _('New')
        result = super(AideServices, self).create(vals)
        return result

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_disapproved(self):
        self.write({'state': 'not_approved'})


class TypeServices(models.Model):
    _name = 'type.services'
    _description = "Type of services"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name',
                       help='')
    type = fields.Selection([('academic','Academic'), ('training','Training'), ('rent','Pay rent'),
                             ('electricity_gas','Electricity and Gas'), ('legal','Legale'), ('Other','Other')],
                            string='Type', help='')