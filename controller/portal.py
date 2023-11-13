from odoo.addons.portal.controllers.portal import CustomerPortal
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.portal.controllers.portal import pager as portal_pager


class PaymentPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(PaymentPortal, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        AidePurchase = request.env['aide.purchase']
        if 'va_count' in counters:
            values['va_count'] = AidePurchase.search_count(self._prepare_payments_domain(partner)) \
                if AidePurchase.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_payments_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['approved', 'delivered'])
        ]

    def action_preview_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _get_payments_searchbar_sortings(self):
        return {
            'date': {'label': _('Order Date'), 'rec_name': 'date desc'},
            'name': {'label': _('Reference'), 'rec_name': 'ref'},
            'stage': {'label': _('Stage'), 'rec_name': 'state'},
        }

    def _prepare_payments_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kwargs
    ):
        AidePurchase = request.env['aide.purchase']

        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()
        url = "/my/purchase_requests"

        domain = self._prepare_payments_domain(partner)

        searchbar_sortings = self._get_payments_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['rec_name']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=AidePurchase.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        requests = AidePurchase.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'requests': requests.sudo(),
            'page_name': 'Requests',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    @http.route(['/my/purchase_requests', '/my/purchase_requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payments(self, **kwargs):
        values = self._prepare_payments_portal_rendering_values(**kwargs)
        request.session['my_payments_history'] = values['requests'].ids[:100]
        return request.render("kafil.portal_my_payments", values)

