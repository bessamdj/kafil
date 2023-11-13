# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AidePurchase(models.Model):
    _name = "aide.purchase"
    _rec_name = "ref"
    _description = "Aide in purchase of goods"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('delivered', 'Delivered'),
        ('not_approved', 'Not Approved'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {'draft': [('readonly', True)],}

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    caretaker = fields.Many2one('kafil.caretaker')
    date = fields.Date('Date', default=fields.Datetime.now)
    amount = fields.Float ('Amount', )
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)
    type_of_purchase = fields.Many2one('type.purchase', string='Type of purchase')

    partner = fields.Many2one('res.partner')

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('aide.purchase') or _('New')
        result = super(AidePurchase, self).create(vals)
        return result

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_disapproved(self):
        self.write({'state': 'not_approved'})


class TypePurchase(models.Model):
    _name = 'type.purchase'
    _description = "Type of purchase"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    type = fields.Selection([('grocery','Grocery'),('butcher','Butcher'),('clothes','Clothes'), ('home_basics','Home basics'),
                             ('home_appliances','Home appliances'), ('home_improvement','Home improvement'),
                             ('wedding','Wedding'),('computer_office','Computer/Office tools'),('other','Other'),],
                            string='Type', help='')
    name = fields.Char(string='Name', help='')
    purchase_service = fields.Boolean(string='Purchase or service')
    need_quantity = fields.Boolean('Need quantity')
    for_any_member = fields.Boolean('For any members')
    elements = fields.Many2many('type.purchase.elements')
    need_detail = fields.Boolean('need detail')


class TypePurchaseElements(models.Model):
    _name = 'type.purchase.elements'
    _description = "Element of type of purchase"

    name = fields.Char('Name')
