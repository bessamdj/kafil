# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AideReceptionMoney(models.Model):
    _name = 'aide.reception.money'
    _rec_name = 'ref'
    _description = 'Financial Aide Reception '
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {'draft': [('readonly', False)],}

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    is_company = fields.Boolean('Is Company', )
    donor = fields.Many2one('res.partner')
    street = fields.Char('street', related='donor.street')
    street2 = fields.Char('street2', related='donor.street2')
    city = fields.Char('City', related='donor.city')
    state_id = fields.Many2one('res.country.state', related='donor.state_id')
    country_id = fields.Many2one('res.country', related='donor.country_id')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    date = fields.Date('Date', default=fields.Datetime.now)
    amount = fields.Float('Amount')
    designation = fields.Many2one('money.label', string='Designation')
    type = fields.Selection([('cash', 'Cash'), ('check', 'Check'), ])
    number = fields.Char('Number / Bank')
    specific_family = fields.Many2one('kafil.caretaker')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('money.reception') or _('New')
        result = super(AideReceptionMoney, self).create(vals)
        return result

    def action_received(self):
        self.create_payment()
        self.write({'state': 'received'})

    def create_register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'aide.reception.money',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def create_payment(self):
        if self.type == 'cash':
            journal_cach = self.env['account.journal'].sudo().search([('code', '=', 'CSH1')])
        else:
            journal_cach = self.env['account.journal'].sudo().search([('code', '=', 'BNK1')])
        payment_id = self.env['account.payment']
        vals = {
            'partner_id': self.donor.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'ref': self.ref,
            'amount': self.amount,
            'date': self.date,
            'journal_id': journal_cach.id,
        }
        paye = payment_id.create(vals)
        paye.action_post()
        paye.mark_as_sent()


class AideMoney(models.Model):
    _name = 'aide.money'
    _rec_name = 'ref'
    _description = 'Financial Aide and payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('delivered', 'Delivered'),
        ('not_approved', 'Not Approved'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {'draft': [('readonly', False)]}

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    caretaker = fields.Many2one('kafil.caretaker')
    date = fields.Date('Date', default=fields.Datetime.now)
    designation = fields.Many2one('money.label', string='Designation')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)
    partner_id = fields.Many2one('res.partner')
    activity = fields.Char('Activity', related='partner_id.function')
    street = fields.Char('street', related='partner_id.street')
    street2 = fields.Char('street2', related='partner_id.street2')
    city = fields.Char('City', related='partner_id.city')
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id')
    country_id = fields.Many2one('res.country', related='partner_id.country_id')

    amount = fields.Float('Amount')
    aide_origin = fields.Many2one('aide.reception.money')
    type = fields.Selection([('cash', 'Cash'), ('check', 'Check'), ])
    number = fields.Char('Bank account')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('money.distribution') or _('New')
        result = super(AideMoney, self).create(vals)
        return result

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_delivered(self):
        self.create_payment()
        self.write({'state': 'delivered'})

    def action_disapproved(self):
        self.write({'state': 'not_approved'})

    def create_payment(self):
        if self.type == 'cash':
            journal_cach = self.env['account.journal'].sudo().search([('code', '=', 'CSH1')])
        else:
            journal_cach = self.env['account.journal'].sudo().search([('code', '=', 'BNK1')])
        payment_id = self.env['account.payment']
        vals = {
            #'partner_id': self.donor.id,
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'ref': self.ref,
            'amount': self.amount,
            'date': self.date,
            'journal_id': journal_cach.id,
        }
        paye = payment_id.create(vals)
        paye.action_post()
        paye.mark_as_sent()

class MoneyBox(models.Model):
    _name = 'money.box'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Money Box"
    _check_company_auto = True
    _rec_name = 'ref'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {
        'received': [('readonly', True)],
    }

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    date = fields.Datetime('Date', default=fields.Datetime.now)
    presente = fields.Many2many('kafil.member', string='Present member')
    total = fields.Float('Total Amount', store=True, compute='_compute_amount')
    amount_line = fields.One2many('money.box.line', 'box_id')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('money.box') or _('New')
        result = super(MoneyBox, self).create(vals)
        return result

    @api.depends('amount_line.amount')
    def _compute_amount(self):
        for box in self:
            amount = 0.0
            for line in box.amount_line:
                amount += line.amount
            currency = self.env.company.currency_id
            box.update({'total': currency.round(amount),})


class MoneyBoxLine(models.Model):
    _name = 'money.box.line'
    _description = "Money Box Line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Datetime('Date', default=fields.Datetime.now)
    amount = fields.Float('Amount')
    designation = fields.Many2one('money.label', string='Designation')
    box_id = fields.Many2one('money.box')
    company_id = fields.Many2one(related='box_id.company_id', string='Company', store=True, readonly=True,
                                 index=True)


class MoneyLabel(models.Model):
    _name = 'money.label'
    _description = "Money Label"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name',
                       help='This label is used to define where go the money collected like orphan or Sadaka or Zakat')

