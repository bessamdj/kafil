# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, timedelta


class KafilCaretaker(models.Model):
    _name = 'kafil.caretaker'
    _description = 'Care Taker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _rec_name = 'name'

    financial_help_count = fields.Float("Financial Help", compute='_compute_financial_help_count')
    purchase_help_count = fields.Float("Purchase Help", compute='_compute_purchase_help_count')
    service_help_count = fields.Float("Services", compute='_compute_service_help_count')
    in_kind_help_count = fields.Float("In Kind Help", compute='_compute_in_kind_help_count')
    health_help_count = fields.Float("Health help", compute='_compute_health_help_count')
    mental_help_count = fields.Float("Mental Help", compute='_compute_mental_help_count')

    def _compute_financial_help_count(self):
        for record in self:
            record.financial_help_count = sum(self.env['aide.money'].search(
                [('caretaker', '=', record.id), ('state', 'in', ['approved','delivered'])]).mapped('amount'))

    def _compute_purchase_help_count(self):
        for record in self:
            record.purchase_help_count = sum(self.env['aide.purchase'].search(
                [('caretaker', '=', record.id), ('state', 'in', ['approved','delivered'])]).mapped('amount'))

    def _compute_service_help_count(self):
        for record in self:
            record.service_help_count = sum(self.env['aide.services'].search(
                [('caretaker', '=', record.id), ('state', 'in', ['approved','delivered'])]).mapped('amount'))

    def _compute_in_kind_help_count(self):
        #for record in self:
        #    record.in_kind_help_count = sum(self.env['aide.in_kind'].search(
        #        [('caretaker', '=', record.id), ('state', 'in', ['approved','delivered'])]).mapped('total_amount'))
        self.in_kind_help_count = self.env['aide.in_kind'].search_count([('caretaker', '=', self.id), ('state', 'in', ['approved','delivered'])])

    def _compute_health_help_count(self):
        for record in self:
            record.health_help_count = sum(self.env['health.help'].search(
                [('caretaker_id', '=', record.id), ('state', 'in', ['approved','delivered'])]).mapped('amount'))

    def _compute_mental_help_count(self):
        for record in self:
            record.mental_help_count = sum(self.env['health.mental.help'].search(
                [('caretaker_id', '=', record.id), ('state', 'in', ['approved','delivered'])]).mapped('amount'))

    def get_financials(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Financial Help',
            'view_mode': 'tree',
            'res_model': 'aide.money',
            'domain': [('caretaker', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_purchase_help(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Financial Help',
            'view_mode': 'tree',
            'res_model': 'aide.purchase',
            'domain': [('caretaker', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_services(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Services Help',
            'view_mode': 'tree',
            'res_model': 'aide.services',
            'domain': [('caretaker', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_in_kinds(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'In Kind Help',
            'view_mode': 'tree',
            'res_model': 'aide.in_kind',
            'domain': [('caretaker', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_healths(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Health Help',
            'view_mode': 'tree',
            'res_model': 'health.help',
            'domain': [('caretaker_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def get_mentals(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mental Health Help',
            'view_mode': 'tree',
            'res_model': 'health.mental.help',
            'domain': [('caretaker_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def calculate_age(self):
        for rec in self:
            today = date.today()
            born = rec.date_birth
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            rec.age = age

    def default_country_id(self):
        company = self.env.company
        country = company[0].partner_id.country_id
        domain = country.id
        return domain

    def default_state_id(self):
        company = self.env.company
        state = company[0].partner_id.state_id
        print (state.id)
        if state :
            domain = [('country_id', '=', state.id)]
        else :
            domain = [()]
        return domain

    def domain_country_id(self):
        company = self.env.company
        country = company[0].partner_id.country_id
        if country:
            domain = [('country_id', '=', country.id)]
        else :
            domain = [()]
        return domain

    state = fields.Selection(
        [('draft', 'Draft'), ('to_review', 'To review'), ('accepted', 'Accepted'), ('not_accepted', 'Not Accepted'), ('suspended', 'Suspended'), ],
        readonly=True, default='draft', )
    ref = fields.Char('Ref', index=True, copy=False, readonly=True, default=lambda self: _('New') )
    widow = fields.Boolean('Mother of the children', default=True)
    relation = fields.Char('Relation')
    date_closing = fields.Date('Date to review') #????
    name = fields.Char('CareTaker Name', required=True, index=True)
    image = fields.Binary(string="Image", attachment=True)
    age = fields.Integer('Age', compute='calculate_age')
    date_birth = fields.Date("Date of Birth", required=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street 2...')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain=domain_country_id )
    zip = fields.Char('ZIP', )
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=default_country_id)

    active = fields.Boolean("Active", default=True)
    whatsapp = fields.Char(string="WhatsApp")
    phone = fields.Char(string="Phone", required=True)
    email = fields.Char(string="Email")
    place_work = fields.Char(string="Place of work")
    salary = fields.Float('Salary')
    other_rev = fields.Float('Other Revenue')
    experience = fields.Integer('Experience')
    education_level = fields.Selection([('university','University'),('high','High School'),
                                        ('middle','Middle School or lower'),('no_educ','No Education'),],
                                       string='Education Level')
    worked = fields.Selection ([('now', 'Now'), ('looking', 'Before and looking'), ('never', 'Never and looking'), ('before', 'before and not Looking'),
                              ('no', 'No & Not Looking')],  string='Work/Worked')
    profession = fields.Many2one('kafil.job', string='Profession', domain="[('for_man', '=', False)]", )
    speciality = fields.Many2many('kafil.job', string='Work/Worked in', domain="[('for_man', '=', False)]", )

    insurance = fields.Boolean ('Insurance')
    work_type = fields.Selection ([('perma','Permanent'), ('contract','Contract'), ('employ','employment network'), ('social','Social Network'),])
    chiffa_card = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('soon', 'Soon')])
    under_responsibility = fields.Integer ('Persons under responsibility')
    responsibility_detail = fields.Char ('Persons under responsibility')

    # -------------------------
    children_problem = fields.Boolean ('Difficulties with children')
    children_detail = fields.Char ('More detail on children')
    widow_situation_before = fields.Char ('Widow Situation Before')
    widow_situation_now = fields.Char('Widow Situation Now')

    # detail on home situation

    type_home = fields.Selection ([('tin_house', 'Tin House'), ('garage', 'Garage'), ('old_house', 'Old House'), ('new_house', 'New House'), ('f2', 'F2'), ('f3', 'F3'), ('f4', 'F4'),('f5', 'F5'),], required=True,)
    home_with = fields.Selection ([('family', 'Family'),('step_family', 'Husband Family'),('alone', 'Alone'),], required=True,)
    room_count = fields.Selection ([('one', 'One'),('two', 'Two'),('tree', 'Three or more'), ('flore', 'A Flore'),], required=True,)
    home_state = fields.Selection ([('good', 'Good'),('average', 'Average'),('bad', 'Bad'),], required=True, )
    home_ownership = fields.Selection ([('social', 'Social'), ('family', 'Family'), ('private', 'Private'), ('messy', 'Messy'), ('rental', 'Rental'),], required=True,)
    amount_rental = fields.Float ('Amount Rental')
    home_basic = fields.Many2many ('kafil.basic')
    home_deficiency = fields.Char('Home Deficiency')

    #decised father ('', '')
    name_f = fields.Char('Last Name.')
    surname = fields.Char('Family Name.')
    date_death = fields.Date ('Date of death.')
    reason_death = fields.Selection ([('ill_short','Ill for a short periode'), ('ill_long','Ill for a long periode'),
                                    ('sudden','Sudden death'),('accident','Accident'),
                                    ('other','Other reason')],string='Reason of death f.', )
    amount_reason = fields.Float ('Cost pre. death')
    unemployed = fields.Boolean ('Was unemployed')
    unemp_reason = fields.Char ('Unemployment Reason')
    profession_f = fields.Many2one ('kafil.job', string='Profession', domain="[('for_man', '=', True)]",) # to be a many to one to get more statistic related to the background
    pension = fields.Float ('Pension')
    estate = fields.Char ('Real Estate ')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id,
                                 index=True)

    # ---------------
    other_caretacker = fields.Boolean ('Care taker')
    taker_origin = fields.Selection ([('wife_f', 'Wife Family'),('husband_f', 'Husband Family'),
                                      ('neighbor', 'Neighbor'),('benefactor', 'Benefactor'),])
    care_type = fields.Selection ([('money', 'Money'),('goods', 'Goods')])
    care_period = fields.Selection([('month', 'Every Month'), ('regularly', 'Regularly'), ('occasion', 'Occasionally'),
                                  ('timetotime', 'From time to time'), ('yearly', 'Yearly'), ])
    type = fields.Selection ([('green', 'Green'), ('orange', 'Orange'), ('red', 'Red')])
    needs = fields.Text ('Needs Detail ')
    date = fields.Date ('Date')
    # other related info

    orphan_ids = fields.One2many ('kafil.orphan', 'caretaker', string='orphans', )
    education = fields.One2many('kafil.education', 'caretaker_id', string='Education', )
    physical_h = fields.One2many('health.physical', 'caretaker_id', string='Physical Health', )
    mental_h = fields.One2many('health.mental', 'caretaker_id', string='Mental Health', )

    # Action
    def action_to_review(self):
        self.ref = ((self.env['ir.sequence'].next_by_code('kafil.caretaker.sequence'))) or _('New')
        self.write({'state': 'to_review'})

    def action_accepted(self):
        self.write({'state': 'accepted'})

    def action_not_accepted(self):
        self.write({'state': 'not_accepted'})

    def action_suspended(self):
        self.write({'state': 'suspended'})


class KafilJob (models.Model):
    _name = 'kafil.job'
    _description = 'Jobs'

    name = fields.Char('Job Title')
    for_man = fields.Boolean('For Man')


class KafilBasic (models.Model):
    _name = 'kafil.basic'
    _description = 'Home Basics'

    name = fields.Char ('Baiscs & Appliance')


class KafilAssist(models.Model):
    _name = 'kafil.assist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Assistance'

    name = fields.Char ('Name', required=True)


class KafilEduction(models.Model):
    _name = 'kafil.education'
    _description = "Education"

    name = fields.Char('Education', required=True,)
    type = fields.Selection([('academic', 'Academic'), ('pro', 'professional'),])
    academic = fields.Selection([('university', 'University'), ('school', 'School/Private institution'), ('pro_training', 'Professional Institution'), ])
    professional = fields.Selection([('artisan', 'Artisan Card'), ('worker', 'Experienced worker')])
    degree = fields.Char('Degree')
    speciality = fields.Char('Speciality')
    caretaker_id = fields.Many2one('kafil.caretaker',string='Caretaker')
    orphan_id = fields.Many2one('kafil.orphan',string='Orphan')