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

from collections import defaultdict
from datetime import datetime

from openerp import pooler
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
#from .common_partner_reports import CommonPartnersReportHeaderWebkit
from .common_reports import CommonReportHeaderWebkit
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class ContractLedgerWebkit(report_sxw.rml_parse, CommonReportHeaderWebkit):

    def __init__(self, cursor, uid, name, context):
        super(ContractLedgerWebkit, self).__init__(cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr
        
        company = self.pool.get('res.users').browse(self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join((_('CONTRACT LEDGER'), company.name, company.currency_id.name))
        
        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('Contract Ledger'),
            'display_account_raw': self._get_display_account_raw,
            'filter_form': self._get_filter,
            'target_move': self._get_target_move,
            'initial_balance': self._get_initial_balance,
            'amount_currency': self._get_amount_currency,
            'display_partner_account': self._get_display_partner_account,
            'display_target_move': self._get_display_target_move,
            'display_cost' : self._get_display_cost,
            'display_price' : self._get_display_price,
            'display_partner' : self._get_display_partner,
            'display_invoiced' : self._get_display_invoiced,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_initial_balance_mode(self, start_period):
        """ Force computing of initial balance for the partner ledger,
        because we cannot use the entries generated by
        OpenERP in the opening period.

        OpenERP allows to reconcile move lines between different partners,
        so the generated entries in the opening period are unreliable.
        """
        return 'initial_balance'

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a ledger_lines attribute on each browse record that will be used
        by mako template"""
        #new_ids = data['form']['chart_account_id']

        # account partner memoizer
        # Reading form
        main_filter = self._get_form_param('filter', data, default='filter_no')
        filter_selection_line = self._get_form_param('selection_line', data)
        #target_move = self._get_form_param('target_move', data, default='all')
        start_date = self._get_form_param('date_from', data)
        stop_date = self._get_form_param('date_to', data)
        #start_period = self._get_form_param('period_from', data)
        #stop_period = self._get_form_param('period_to', data)
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        partner_ids = self._get_form_param('partner_ids', data)
        contract_ids = self._get_form_param('contract_ids', data)
        analytic_journal_ids = self._get_form_param('analytic_journal_ids', data)
        show_cost = self._get_form_param('cost', data)
        show_price = self._get_form_param('price', data)
        detail_by = self._get_form_param('detail_by', data)
        #detail_by = 'journal' # da fare su wizard -> possibile scegliere anche x data
        '''>>>>>>>>>>>>>
        fiscalyear = self.get_fiscalyear_br(data)
        result_selection = self._get_form_param('result_selection', data)
        chart_account = self._get_chart_account_id_br(data)
        
        if main_filter == 'filter_no' and fiscalyear:
            start_period = self.get_first_fiscalyear_period(fiscalyear)
            stop_period = self.get_last_fiscalyear_period(fiscalyear)
        <<<<<<<<<'''
        # Retrieving accounts
        '''>>>>>>>>>>
        filter_type = ('payable', 'receivable')
        if result_selection == 'customer':
            filter_type = ('receivable',)
        if result_selection == 'supplier':
            filter_type = ('payable',)
        <<<<<<<<<'''

        #contracts = self.get_all_analytic_accounts(new_ids, exclude_type=['view', 'template'],
        #                                only_type=filter_type)
        contracts = self.get_all_analytic_accounts(contract_ids, partner_ids, exclude_type=['view', 'template'], 
                                          only_type=None)
        
        if not contracts:
            raise osv.except_osv(_('Error'), _('No contracts to print.'))

        if main_filter == 'filter_date':
            start = start_date
            stop = stop_date
        else:
            start = start_period
            stop = stop_period

        # when the opening period is included in the selected range of periods and
        # the opening period contains move lines, we must not compute the initial balance from previous periods
        # but only display the move lines of the opening period
        # we identify them as:
        #  - 'initial_balance' means compute the sums of move lines from previous periods
        #  - 'opening_balance' means display the move lines of the opening period
        '''>>>>>>>>>>>
        init_balance = main_filter in ('filter_no', 'filter_period')
        initial_balance_mode = init_balance and self._get_initial_balance_mode(start) or False

        initial_balance_lines = {}
        if initial_balance_mode == 'initial_balance':
            initial_balance_lines = self._compute_partners_initial_balances(contracts,
                                                                            start_period,
                                                                            partner_filter=partner_ids,
                                                                            exclude_reconcile=False)
        <<<<<<<'''
        ledger_lines = self._compute_contract_ledger_lines(contracts,
                                                          main_filter,
                                                          #target_move,
                                                          start,
                                                          stop,
                                                          partner_filter=partner_ids,
                                                          analytic_journal_filter=analytic_journal_ids, 
                                                          filter_selection_line=filter_selection_line, 
                                                          detail_by=detail_by)
        objects = []
        for contract in self.pool.get('account.analytic.account').browse(self.cursor, self.uid, contracts):
            contract.ledger_lines = ledger_lines.get(contract.id, {})
            
            ledg_lines_pids = ledger_lines.get(contract.id, {}).keys()
            if detail_by == 'journal':
                contract.elements_order = self._order_journals(ledg_lines_pids)
                #contract.elements_order = self._order_partners(ledg_lines_pids, init_bal_lines_pids)
                #contract.elements_order = ledg_lines_pids
            else:
                contract.elements_order = self._order_dates(ledg_lines_pids)
            objects.append(contract)
            
        self.localcontext.update({
            #'fiscalyear': fiscalyear,
            'start_date': start_date,
            'stop_date': stop_date,
            'start_period': start_period,
            'stop_period': stop_period,
            'partner_ids': partner_ids,
            #'chart_account': chart_account,
            #'initial_balance_mode': initial_balance_mode,
        })

        return super(ContractLedgerWebkit, self).set_context(objects, data, contract_ids,
                                                            report_type=report_type)

    #def _compute_contract_ledger_lines(self, accounts_ids, main_filter, target_move, start, stop, partner_filter=False):
    def _compute_contract_ledger_lines(self, contract_ids, main_filter, start, stop, 
                                       partner_filter=False, analytic_journal_filter=False, filter_selection_line=False, detail_by=False):
        res = defaultdict(dict)

        for contract_id in contract_ids:
            move_line_ids = self._get_analytic_line_ids(    contract_id,
                                                            main_filter,
                                                            start,
                                                            stop,
                                                            #target_move,
                                                            partner_filter=partner_filter,
                                                            analytic_journal_filter=analytic_journal_filter,
                                                            filter_selection_line=filter_selection_line,
                                                            detail_by=detail_by)
            
            if not move_line_ids:
                continue
            if detail_by == 'journal':
                for journal_id in move_line_ids:
                    journal_line_ids = move_line_ids.get(journal_id, [])
                    lines = self._get_analytic_move_line_datas(list(set(journal_line_ids)))
                    res[contract_id][journal_id] = lines
            else:
                for date in move_line_ids:
                    date_ids = move_line_ids.get(date, [])
                    lines = self._get_analytic_move_line_datas(list(set(date_ids)))
                    res[contract_id][date] = lines
            '''
            for partner_id in move_line_ids:
                partner_line_ids = move_line_ids.get(partner_id, [])
                lines = self._get_move_line_datas(list(set(partner_line_ids)))
                res[acc_id][partner_id] = lines'''
        return res


HeaderFooterTextWebKitParser('report.openforce_relate_contract_ledger',
                             'account.analytic.account',
                             'addons/openforce_financial_report/report/templates/contract_ledger.mako',
                             parser=ContractLedgerWebkit)