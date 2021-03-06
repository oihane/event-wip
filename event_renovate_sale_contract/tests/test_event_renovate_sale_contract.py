# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventRenovateSaleContract(common.TransactionCase):

    def setUp(self):
        super(TestEventRenovateSaleContract, self).setUp()
        self.sale_model = self.env['sale.order']
        self.account_model = self.env['account.analytic.account']
        self.wiz_model = self.env['wiz.sale.order.renovate.contract']
        self.wiz2_model = self.env['wiz.analytic.account.renovate.contract']
        self.wiz3_model = self.env['wiz.analytic.invoice.line.increase']
        self.service_product = self.browse_ref(
            'product.product_product_consultant')
        line_vals = {'product_id': self.service_product.id,
                     'name': self.service_product.name,
                     'quantity': 1,
                     'uom_id': self.service_product.uom_id.id,
                     'price_unit': 100}
        account_vals = {'name': 'Event renovate sale contract',
                        'date_start': '2025-01-01',
                        'date': '2025-12-31',
                        'type': 'contract',
                        'recurring_invoices': True,
                        'recurring_interval': 1,
                        'recurring_rule_type': 'monthly',
                        'recurring_next_date': '2025-01-15',
                        'recurring_invoice_line_ids': [(0, 0, line_vals)]}
        self.account = self.account_model.create(account_vals)
        sale_vals = {
            'name': 'sale order 1600',
            'partner_id': self.ref('base.res_partner_1'),
            'project_id': self.account.id}
        sale_line_vals = {
            'product_id': self.service_product.id,
            'name': self.service_product.name,
            'product_uom_qty': 7,
            'product_uom': self.service_product.uom_id.id,
            'price_unit': self.service_product.list_price}
        sale_vals['order_line'] = [(0, 0, sale_line_vals)]
        self.sale_order = self.sale_model.create(sale_vals)
        account_vals = {'name': 'Event renovate sale contract-2',
                        'date_start': '2025-01-01',
                        'date': '2025-12-31',
                        'type': 'contract',
                        'recurring_invoices': True,
                        'recurring_interval': 1,
                        'recurring_rule_type': 'monthly',
                        'recurring_next_date': '2025-01-15',
                        'recurring_invoice_line_ids': [(0, 0, line_vals)]}
        self.account2 = self.account_model.create(account_vals)

    def test_event_renovate_sale_contract(self):
        wiz = self.wiz_model.create({})
        wiz.with_context(
            {'active_ids':
             self.sale_order.ids}).renovate_sale_order_and_contract()
        cond = [('name', '=', '{} {}'.format(self.account.name, '2026'))]
        account = self.account_model.search(cond, limit=1)
        self.assertNotEqual(
            len([account]), 0, 'Renovate contract not found')
        self.assertEqual(
            account.date_start, '2026-01-01',
            'Error in date start of renovate contract')
        self.assertEqual(
            account.date, '2026-12-31',
            'Error in date end of renovate contract')
        cond = [('project_id', '=', account.id)]
        sale = self.sale_model.search(cond, limit=1)
        self.assertNotEqual(len([sale]), 0, 'New sale not found')

    def test_account_analytic_account_renovate_contract(self):
        wiz_vals = {'increase': 0.014}
        wiz = self.wiz2_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': self.account2.ids}).renovate_contracts()
        cond = [('name', '=', '{} {}'.format(self.account2.name, '2026'))]
        account = self.account_model.search(cond, limit=1)
        self.assertNotEqual(
            len([account]), 0, 'Renovate contract not found(2)')
        self.assertEqual(
            account.date_start, '2026-01-01',
            'Error in date start of renovate contract(2)')
        self.assertEqual(
            account.date, '2026-12-31',
            'Error in date end of renovate contract(2)')
        self.assertEqual(
            account.recurring_invoice_line_ids[0].price_unit, 101.4,
            'Error in price unit of renovate contract')

    def test_analytic_invoice_line_increase(self):
        wiz_vals = {'increase': 0.014}
        wiz = self.wiz3_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': self.account.ids}).increase_account_invoice_line()
        new_price = self.account.recurring_invoice_line_ids[0].price_unit
        self.assertEqual(
            new_price, 101.4, 'Wrong increase for new price')
