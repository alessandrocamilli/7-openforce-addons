# -*- encoding: utf-8 -*-
import time
from report import report_sxw
from osv import osv

class report_webkit_html(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(cr, uid, name, context=context)
                
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.result_acc = []
        self.localcontext.update({
            'partners' : self._get_partners,
            'accounts' : self.lines,
            'test': 'alex-prova',
            'time': time,
            'cr':cr,
            'uid': uid,
        })
    
    def _get_partners(self, move):
        res=[]
        partner_obj=self.pool.get('res.partner')
        partners_ids = partner_obj.search(self.cr, self.uid, [
            ('customer', '=', 'True'),
            ], order='name')
        for partner in partner_obj.browse(self.cr, self.uid, partners_ids):
            res.append(partner)
        return res
    
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
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
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
        '''
        ctx = self.context.copy()
        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        '''
        ctx={}
        ctx['date_from'] = '2013-01-01'
        ctx['date_to'] =  '2013-12-31'
        #ctx['state'] = 'draft'
        ctx['fiscalyear'] = 1
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)
        import pdb
        pdb.set_trace()
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                #_process_child(accounts,form['display_account'],parent)
                _process_child(accounts,'not_zero',parent)
        return self.result_acc
        ############################
        
    
        
report_sxw.report_sxw('report.report_test_webkit_partner',
                       'res.partner', 
                       'addons/openforce_test_webkit/report/report_test_webkit_html.mako',
                       parser=report_webkit_html)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
