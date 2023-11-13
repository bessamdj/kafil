# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date

from dateutil.relativedelta import relativedelta

STATE = [
        ('none', 'Non Member'),
        ('canceled', 'Old Member'),
        ('nonactive',  'To renew Member'),
        ('active', 'Active Member'),]

class KafilMember(models.Model):
    _name = 'kafil.member'
    _rec_name = 'name'
    _order = 'id desc'
    _description = "Association Members"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def default_country_id(self):
        company = self.env.company
        country = company[0].partner_id.country_id
        domain = country.id
        return domain

    def calculateAge(self):
        today = date.today()
        born = self.date_birth
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        self.age = age

    name = fields.Char('Name', required=True)
    image = fields.Binary(string="Image", attachment=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], default='male', string="Sexe", required=True)
    street = fields.Char('Street ...')
    street2 = fields.Char('Street 2...')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=', country)]")
    country = fields.Many2one('res.country', string='Country', ondelete='restrict', default=default_country_id)
    date_birth = fields.Date('Date of Birth', required=True)
    age = fields.Integer('Age', compute='calculateAge')
    function = fields.Char('Function in the association')
    is_member = fields.Boolean('Is Member')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)

    #membership = fields.Many2one()
    # partner_id = fields.One2many() ???? to update every line
    # onchange >>>> all the necesseray field to the partner realted fields

    is_donor = fields.Boolean('Is Donor')
    # don't connect doner to partner so it can be filtred by company
    parent_id = fields.Many2one('res.partner')
    active = fields.Boolean(default=True)
    phone = fields.Char()
    whatsapp = fields.Char()
    email = fields.Char()

    date_join = fields.Date(string='Join Date',
                            help="Date on which member has joined the membership")
    date_from = fields.Date('date from')
    date_to = fields.Date(string='Cancel date')

    member_lines = fields.One2many('kafil.member.lines','member')
    membership_state = fields.Selection(STATE, compute='_compute_membership_state', # membership.STATE
                                        string='Membership Status', store=True,
                                        help='It indicates the membership state.\n'    
                                         '-Non Member: A member who has not applied for any membership.\n'
                                         '-Cancelled Member: A member who has cancelled his membership.\n'
                                         '-Old Member: A member whose membership date has expired.\n'
                                         '-Active Member: A member whose paied his membership has been paied.')


    @api.onchange('member_lines')
    def onchange_member_lines(self):
        today = fields.Date.today()
        test = fields.date.today() + relativedelta(years=-1)
        print (1)
        #for rec in self.member_lines:
        #    rec.date_from > today
        #if today != self.school_year.order:
        #    search_id = self.env['kafil.orphan.years'].search(
        #        [('order', '=', today)], limit=1)
        #    self.school_year = search_id


    @api.depends('member_lines.date_to', 'member_lines.date_from',)
    def _compute_membership_state(self):
        today = fields.Date.today()
        for partner in self:
            state = 'none'

            partner.date_from = self.env['kafil.member.lines'].search([
                ('member', '=', partner.id)
            ], limit=1, order='date_from').date_from or today
            partner.date_to = self.env['kafil.member.lines'].search([
                ('member', '=', partner.id)
            ], limit=1, order='date_to desc').date_to or today

            if partner.date_to and partner.date_from and today > partner.date_to:
                    state = 'active'
                    continue
            #if partner.free_member and state != 'paid':
            #    state = 'free'
            partner.membership_state = state


    @api.model
    def _cron_update_members_state(self):
        partners = self.search([('membership_state', 'in', ['none', 'active'])])
        # mark the field to be recomputed, and recompute it
        self.env.add_to_compute(self._fields['membership_state'], partners)


class MembershipLine(models.Model):
    _name = 'kafil.member.lines'
    _rec_name = 'member'
    _order = 'id desc'
    _description = 'Membership Line'

    member = fields.Many2one('kafil.member', string='Member', ondelete='cascade', index=True)
    membership_id = fields.Many2one('product.product', string="Membership", required=True) #filtre only membership product
    date_from = fields.Date(string='From', readonly=True)
    date_to = fields.Date(string='To', readonly=True)
    member_price = fields.Float(related='membership_id.list_price', string='Membership Fee',
        digits='Product Price', required=True,
        help='Amount for the membership')
    paid = fields.Boolean('Paid')
    state = fields.Selection(STATE, string='Membership Status', store=True,
        help="It indicates the membership status.\n"
             "-Non Member: A member who has not applied for any membership.\n"
             "-Cancelled Member: A member who has cancelled his membership.\n"
             "-Old Member: A member whose membership date has expired.\n"
             "-Active Member: A member whose paied his membership has been paied.")

    #  compute='_compute_state',


class Partner(models.Model):
    _inherit = "res.partner"

    is_member = fields.Boolean('Is Member')
    is_donor = fields.Boolean('Is Donor')
    is_doctor = fields.Boolean('Is Doctor')


class Product(models.Model):
    _inherit = 'product.template'

    membership = fields.Boolean(help='Check if the product is eligible for membership.')
