# -*- coding: utf-8 -*-
import time
from report import report_sxw
from osv import osv

class report_salesman_commission(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, data, context):
        super(report_italian_balance, self).__init__(cr, uid, data, context=context)
        
        self.form = self.pool.get(context['active_model']).browse(self.cr, self.uid,context['active_id'] )
        self.context = context        
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.result_acc = []
        self.attivita_acc = []
        self.passivita_acc = []
        self.ricavi_acc = []
        self.costi_acc = []
        self.localcontext.update({
            'accounts' : self.lines,
            'passivita' : self.passivita_lines,
            'attivita' : self.attivita_lines,
            'costi' : self.costi_lines,
            'ricavi' : self.ricavi_lines,
            
            'test': 'alex-prova',
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
    def attivita_lines(self, form, ids=None, done=None):
        self.ricavi_acc = []
        self.costi_acc = []
        self.attivita_acc = []
        self.passivita_acc = []
        self.lines(form, ids=None, done=None)
        return self.attivita_acc
    
    def passivita_lines(self, form, ids=None, done=None):
        self.ricavi_acc = []
        self.costi_acc = []
        self.attivita_acc = []
        self.passivita_acc = []
        self.lines(form, ids=None, done=None)
        return self.passivita_acc
    
    def ricavi_lines(self, form, ids=None, done=None):
        self.ricavi_acc = []
        self.costi_acc = []
        self.attivita_acc = []
        self.passivita_acc = []
        self.lines(form, ids=None, done=None)
        return self.ricavi_acc
    
    def costi_lines(self, form, ids=None, done=None):
        self.ricavi_acc = []
        self.costi_acc = []
        self.attivita_acc = []
        self.passivita_acc = []
        self.lines(form, ids=None, done=None)
        return self.costi_acc
    
    
    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
            account_rec = [acct for acct in accounts if acct['id']==parent][0]
            currency_obj = self.pool.get('res.currency')
            acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
            
            currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
            res = {
                'id': account_rec['id'],
                'type': account_rec['type'],
                'code': account_rec['code'],
                'name': account_rec['name'],
                'level': account_rec['level'],
                'debit': account_rec['debit'],
                'credit': account_rec['credit'],
                'balance': account_rec['balance'],
                'parent_id': account_rec['parent_id'],
                'bal_type': '',
            }
            self.sum_debit += account_rec['debit']
            self.sum_credit += account_rec['credit']
            if disp_acc == 'movement':
                if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
                    if acc_id.user_type.report_type == 'asset':
                        self.attivita_acc.append(res)
                    if acc_id.user_type.report_type == 'liability':
                        self.passivita_acc.append(res)
                    if acc_id.user_type.report_type == 'income':
                        self.ricavi_acc.append(res)
                    if acc_id.user_type.report_type == 'expense':
                        self.costi_acc.append(res)
            elif disp_acc == 'not_zero':
                if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
                    if acc_id.user_type.report_type == 'asset':
                        self.attivita_acc.append(res)
                    if acc_id.user_type.report_type == 'liability':
                        self.passivita_acc.append(res)
                    if acc_id.user_type.report_type == 'income':
                        self.ricavi_acc.append(res)
                    if acc_id.user_type.report_type == 'expense':
                        self.costi_acc.append(res)
            else:
                self.result_acc.append(res)
                if acc_id.user_type.report_type == 'asset':
                    self.attivita_acc.append(res)
                if acc_id.user_type.report_type == 'liability':
                    self.passivita_acc.append(res)
                if acc_id.user_type.report_type == 'income':
                    self.ricavi_acc.append(res)
                if acc_id.user_type.report_type == 'expense':
                    self.costi_acc.append(res)
            if account_rec['child_id']:
                for child in account_rec['child_id']:
                    _process_child(accounts,disp_acc,child)
        
        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}
        
        ctx = self.context.copy()
        
        ctx['fiscalyear'] = self.form.fiscalyear_id.id #form['fiscalyear_id']
        #if form['filter'] == 'filter_period':
        if self.form.filter == 'filter_period':
            ctx['period_from'] = self.form.period_from#form['period_from']
            ctx['period_to'] = self.form.period_to#form['period_to']
        #elif form['filter'] == 'filter_date':
        elif self.form.filter == 'filter_date':
            ctx['date_from'] = self.form.date_from #form['date_from']
            ctx['date_to'] =  self.form.date_to #form['date_to']
        #ctx['state'] = self.form.state #form['target_move']
        
        #parents = ids
        #child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        '''
        accounts = account_obj.read(self.cursor, self.uid, [self.form.chart_account_id.id], ['type','code','name','debit','credit', 'balance', 'parent_id','level','child_id'], ctx)

        accounts_by_id = {}
        for account in accounts:
            if init_balance:
                # sum for top level views accounts
                child_ids = account_obj._get_children_and_consol(self.cursor, self.uid, account['id'], ctx)
                if child_ids:
                    child_init_balances = [init_bal['init_balance'] for acnt_id, init_bal in init_balance.iteritems() if acnt_id in child_ids ]
                    top_init_balance = reduce(add, child_init_balances)
                    account['init_balance'] = top_init_balance
                else:
                    account.update(init_balance[account['id']])
                account['balance'] = account['init_balance'] + account['debit'] - account['credit']
            accounts_by_id[account['id']] = account
        '''
        
        parents=[]
        parents.append(self.form.chart_account_id.id)
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, [self.form.chart_account_id.id], ctx)
        
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                #_process_child(accounts,form['display_account'],parent)
                _process_child(accounts,'movement',parent)
        return self.result_acc
        ############################
        
    
        
report_sxw.report_sxw('report.l10n_it_account_report_balance',
                       'account.account', 
                       'addons/openforce_salesman/report/report_italian_balance.mako',
                       parser=report_salesman_commission)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
