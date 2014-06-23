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

from openerp.osv import fields, orm, osv

class relate_common_report(osv.osv_memory):

    _name = "relate.common.report"
    _description = "Relate Common Report"

    _columns = {
        'recipient': fields.selection([('custom', 'Custom params'),
                            ('company', 'Company'),
                            ('customer', 'Customer'),], "Recipient", required=True,
                           help=''),
        'cost': fields.boolean("With Cost", help="It adds the cost column"),
        'price': fields.boolean("With Price", help="It adds the price column"),
        'partner': fields.boolean("With Partner", help="It adds the partner column"),
        'invoiced': fields.boolean("With Invoiced", help="It adds the invoiced column"),
        
        'detail_by': fields.selection([('journal', 'Journal'),
                            ('date', 'Date')], "Detail by", required=True,
                           help=''),
        
        'contract_ids': fields.many2many('account.analytic.account', string='Contracts',
                                         help="Only selected contracts will be printed. "
                                              "Leave empty to print all contracts."),
        'partner_ids': fields.many2many('res.partner', string='Partners',
                                         help="Only selected partners will be printed. "
                                              "Leave empty to print all partners."),
        'analytic_journal_ids': fields.many2many('account.analytic.journal', string='Journals',
                                         help="Only selected journals will be printed. "
                                              "Leave empty to print all journals."),
        'filter': fields.selection([('filter_no', 'No Filters'),
                                    ('filter_date', 'Date'),
                                    ('filter_period', 'Periods')], "Filter by", required=True,
                                   help='Filter by date: no opening balance will be displayed. '
                                        '(opening balance can only be computed based on period to be correct).'),
        'date_from': fields.date("Start Date "),
        'date_to': fields.date("End Date "),
        'period_from': fields.many2one('account.period', 'Start Period'),
        'period_to': fields.many2one('account.period', 'End Period'),
        
        'selection_line': fields.selection([('all', 'All lines'),
                                    ('to_invoice', 'Only to invoice')], "Selection line", required=True,)
    }
    _defaults = {
        'recipient': 'company',
        'filter': 'filter_no',
        'selection_line': 'all',
    }
    
    #def _check_fiscalyear(self, cr, uid, ids, context=None):
    #    obj = self.read(cr, uid, ids[0], ['fiscalyear_id', 'filter'], context=context)
    #    if not obj['fiscalyear_id'] and obj['filter'] == 'filter_no':
    #        return False
    #    return True
    
    def onchange_recipient(self, cr, uid, ids, recipient='company', context=None):
        res = {}
        if recipient == 'customer':
            res['value'] = {'price': True, 'cost': False, 'partner': False, 'invoiced': False, 'selection_line': 'to_invoice'}
        if recipient == 'company':
            res['value'] = {'price': True, 'cost': True, 'partner': True, 'invoiced': True, 'selection_line': 'all'}
        return res
    
    
    def onchange_filter(self, cr, uid, ids, filter='filter_no', context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False, 'date_to': False}

        if filter == 'filter_date':
            date_from, date_to = time.strftime('%Y-%m-01'), time.strftime('%Y-%m-%d')
            
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': date_from, 'date_to': date_to}
        
        return res
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['recipient', 'cost', 'price', 'invoiced', 'partner', 'contract_ids', 'partner_ids', 'detail_by',\
                                'analytic_journal_ids', 'filter', 'selection_line', 'date_from', 'date_to', 'period_from', 'period_to'], context=context)[0]
        if data['form'].get('period_from', False):
            data['form'].update({'period_from' : data['form']['period_from'][0]})
        if data['form'].get('period_to', False):
            data['form'].update({'period_to' : data['form']['period_to'][0]})
        return self._print_report(cr, uid, ids, data, context=context)

    def pre_print_report(self, cr, uid, ids, data, context=None):
        '''
        data = super(AccountReportPartnersLedgerWizard, self).pre_print_report(cr, uid, ids, data, context)
        if context is None:
            context = {}
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['chart_account_id']]
        vals = self.read(cr, uid, ids,
                         ['amount_currency', 'partner_ids'],
                         context=context)[0]
        data['form'].update(vals)'''
        return data
'''
    def _print_report(self, cursor, uid, ids, data, context=None):
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account_report_partners_due_register',
                'datas': data}
'''