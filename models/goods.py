# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AideReceptionInkind(models.Model):
    _name = 'aide.reception.inkind'
    _rec_name = 'ref'
    _description = 'In-kind Aide Reception'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def create_picking(self):
        for lines in self.aide_line:
            product_ids = self.env['product.product'].search(
                [('id', '=', lines.product_id.id)])
            for prod_id in product_ids:
                move_id = self.env['stock.picking']
                type_object = self.env['stock.picking.type']
                company_id = self.env.context.get('company_id') or self.env.user.company_id.id
                types = type_object.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)],
                                           limit=1)
                partner = self.donor
                vals = {
                    'partner_id': partner.id,
                    'origin': self.ref,
                    'move_type': 'one',
                    'picking_type_id': types.id,
                    'location_id': partner.property_stock_supplier.id,
                    'location_dest_id': types.default_location_dest_id.id,
                    'move_ids': [(0, 0, {
                        'name': self.ref,
                        'product_id': prod_id.id,
                        'product_uom': prod_id.uom_id.id,
                        'product_uom_qty': lines.quantity,
                        'quantity_done': lines.quantity,
                        'location_id': partner.property_stock_supplier.id,
                        'location_dest_id': types.default_location_dest_id.id,
                    })],
                }
                move = move_id.create(vals)
                move.action_confirm()
                move.action_assign()
                move._action_done()

    def domain_is_company(self):
        if self.is_company:
            domain = [('is_company', '=', True)]
        else:
            domain = [('is_company', '=', False)]
        return domain

    state = fields.Selection([
        ('draft', 'Draft'),
        ('received', 'Received'),
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    READONLY_STATES = {'received': [('readonly', True)],}

    ref = fields.Char('Ref', readonly=True, default=lambda self: _('New'))
    is_company = fields.Boolean('Is Company', required=True, default=True)
    donor = fields.Many2one('res.partner', required=True,  domain=domain_is_company)
    date = fields.Date('Date', required=True,  index=True, copy=False, default=fields.Datetime.now,)
    total_amount = fields.Float('Amount', store=True, compute='_compute_total_amount')
    aide_line = fields.One2many('aide.reception.inkind.line', 'reception_id')
    specific_family = fields.Many2one('kafil.caretaker')
    #picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.company.id, index=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('reception.inkind') or _('New')
        result = super(AideReceptionInkind, self).create(vals)
        return result

    @api.depends('aide_line.amount_value')
    def _compute_total_amount(self):
        for aide in self:
            amount = 0.0
            for line in aide.aide_line:
                amount += line.amount_value
            currency = self.env.company.currency_id
            aide.update({
                'total_amount': currency.round(amount),
            })

    def action_received(self):
        self.create_picking()
        self.write({'state': 'received'})


class AideReceptionInkindLine(models.Model):
    _name = 'aide.reception.inkind.line'
    _description = 'In-kind Aide Reception Lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date('Date', default=fields.Datetime.now)
    product_id = fields.Many2one('product.product',  required=True, domain="[('type', '=', 'product')]")
    quantity = fields.Float('Quantity', default=1)
    product_value = fields.Float(related='product_id.standard_price', required=True, string='Estimated Value', readonly=False)
    amount_value = fields.Float('Amount', store=True, compute='_compute_amount_value')
    reception_id = fields.Many2one('aide.reception.inkind')
    state = fields.Selection(related='reception_id.state')
    company_id = fields.Many2one(related='reception_id.company_id', string='Company', store=True, readonly=True, index=True)

    @api.depends('quantity','product_value')
    def _compute_amount_value(self):
        for line in self :
            line.amount_value = line.quantity * line.product_value


class AideInKind(models.Model):
    _name = "aide.in_kind"
    _rec_name = "ref"
    _description = "In kind Aide Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def create_delivery(self):
        for lines in self.aide_line:
            product_ids = self.env['product.product'].search(
                [('id', '=', lines.product_id.id)])
            for prod_id in product_ids:
                move_id = self.env['stock.picking']
                type_object = self.env['stock.picking.type']
                type_location = self.env['stock.location']
                company_id = self.env.context.get('company_id') or self.env.user.company_id.id
                types = type_object.search([('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)],
                                           limit=1)
                dest_location = type_location.search([('name', '=', 'Customers')],limit=1)
                print (dest_location)
                partner = self.env['res.partner'].search([('name','=','anonymous')])
                vals = {
                    #'partner_id': partner.id,
                    'origin': self.ref,
                    'move_type': 'one',
                    'picking_type_id': types.id,
                    'location_id': types.default_location_src_id.id,
                    'location_dest_id':dest_location.id,
                    'move_ids': [(0, 0, {
                        'name': self.ref,
                        'product_id': prod_id.id,
                        'product_uom': prod_id.uom_id.id,
                        'product_uom_qty': lines.quantity,
                        'quantity_done': lines.quantity,
                        'location_id': types.default_location_src_id.id,
                        'location_dest_id': dest_location.id,
                    })],
                }
                move = move_id.create(vals)
                move.action_confirm()
                move.action_assign()
                move._action_done()

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
    caretaker = fields.Many2one('kafil.caretaker', required=True,)
    aide_origin = fields.Many2one('aide.reception.inkind', states=READONLY_STATES)
    date = fields.Date('Date', default=fields.Datetime.now)
    aide_line = fields.One2many('aide.in_kind.line', 'aide_id')
    total_amount = fields.Float ('Amount', store=True, compute='_compute_total_amount')
    #picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('aides.inkind') or _('New')
        result = super(AideInKind, self).create(vals)
        return result

    @api.depends('aide_line.amount_value')
    def _compute_total_amount(self):
        for aide in self:
            amount = 0.0
            aides = aide.aide_line
            aide.total_amount = sum(aides.mapped('amount_value'))
            currency = self.env.company.currency_id
            #aide.update({ 'total_amount': currency.round(amount),})

    def action_to_approve(self):
        self.write({'state': 'to_approve'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_disapproved(self):
        self.write({'state': 'not_approved'})

    def action_delivered(self):
        self.create_delivery()
        self.write({'state': 'delivered'})


class AideInKindLine(models.Model):
    _name = 'aide.in_kind.line'
    _description = 'In kind Aide Lines'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date = fields.Date('Date', default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', required=True, domain="[('type', '=', 'product')]")
    quantity = fields.Float('Quantity', default=1)
    product_value = fields.Float(related='product_id.standard_price', string='Estimated Value', readonly=False)
    amount_value = fields.Float('Amount', store=True, compute='_compute_amount_value')
    aide_id = fields.Many2one('aide.in_kind')
    state = fields.Selection(related='aide_id.state')
    company_id = fields.Many2one(related='aide_id.company_id', string='Company', store=True, readonly=True, index=True)

    @api.depends('quantity', 'product_value')
    def _compute_amount_value(self):
        for line in self:
            line.amount_value = line.quantity * line.product_value


class TypeInKind(models.Model):
    _name = 'type.in_kind'
    _description = "Type of in kind aide"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name',
                       help='')
    type = fields.Selection([('clothes','Clothes'), ('aide1','Aide el Fitre'), ('aide2','Aide el Adha')],
                            string='Type', help='')