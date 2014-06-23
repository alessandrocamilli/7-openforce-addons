# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import fields, orm


class AccountReportPartnersLedgerWizard(orm.TransientModel):
    """Will launch partner ledger report and pass required args"""

    _inherit = "account.common.partner.report"
    _name = "partners.due.register.webkit"
    _description = "Partner Ledger Report"

    _columns = {
        'amount_currency': fields.boolean("With Currency",
                                          help="It adds the currency column"),
        'partner_ids': fields.many2many('res.partner', string='Filter on partner',
                                         help="Only selected partners will be printed. "
                                              "Leave empty to print all partners."),
        'filter': fields.selection([('filter_no', 'No Filters'),
                                    ('filter_date', 'Date'),
                                    ('filter_date_maturity', 'Date Maturity'),
                                    ('filter_period', 'Periods')], "Filter by", required=True,
                                   help='Filter by date: no opening balance will be displayed. '
                                        '(opening balance can only be computed based on period to be correct).'),
        'date_maturity_from': fields.date("Start Date Maturity"),
        'date_maturity_to': fields.date("End Date Maturity"),
        'order_by': fields.selection([('partner', 'Partner'),
                                    ('date_maturity', 'Date Maturity')], "Order by", required=True),
        'exclude_reconcile': fields.boolean("Exclude Reconcile"),
    }
    _defaults = {
        'amount_currency': False,
        'result_selection': 'customer_supplier',
        'order_by': 'date_maturity',
        'exclude_reconcile': True,
    }

    def _check_fiscalyear(self, cr, uid, ids, context=None):
        obj = self.read(cr, uid, ids[0], ['fiscalyear_id', 'filter'], context=context)
        if not obj['fiscalyear_id'] and obj['filter'] == 'filter_no':
            return False
        return True

    _constraints = [
        (_check_fiscalyear,
         'When no Fiscal year is selected, you must choose to '
         'filter by periods or by date.',
         ['filter']),
    ]

    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False, 'date_to': False, 'date_maturity_from': False, 'date_maturity_to': False}
        if filter == 'filter_date':
            if fiscalyear_id:
                fyear = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
                date_from = fyear.date_start
                date_to = fyear.date_stop > time.strftime('%Y-%m-%d') and time.strftime('%Y-%m-%d') or fyear.date_stop
            else:
                date_from, date_to = time.strftime('%Y-01-01'), time.strftime('%Y-%m-%d')
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': date_from, 'date_to': date_to, 'date_maturity_from': False, 'date_maturity_to': False}
        if filter == 'filter_date_maturity':
            if fiscalyear_id:
                fyear = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=context)
                date_from = fyear.date_start
                date_to = fyear.date_stop > time.strftime('%Y-%m-%d') and time.strftime('%Y-%m-%d') or fyear.date_stop
            else:
                date_from, date_to = time.strftime('%Y-01-01'), time.strftime('%Y-%m-%d')
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False, 'date_to': False, 'date_maturity_from': date_from, 'date_maturity_to': date_to}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods = [i[0] for i in cr.fetchall()]
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False, 'date_maturity_from': False, 'date_maturity_to': False}
        return res
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_maturity_from',  'date_maturity_to', 'date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move', 'order_by', 'exclude_reconcile'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = used_context
        return self._print_report(cr, uid, ids, data, context=context)

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(AccountReportPartnersLedgerWizard, self).pre_print_report(cr, uid, ids, data, context)
        if context is None:
            context = {}
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids,
                         ['amount_currency', 'partner_ids'],
                         context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account_report_partners_due_register',
                'datas': data}