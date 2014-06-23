# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Alessandro Camilli
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

from osv import fields, orm, osv
from openerp.tools.translate import _

class account_analytic_account(orm.Model):
    
    _inherit = "account.analytic.account"
    _columns = {
        'relate_payment_term_ids': fields.one2many('relate.contract.payment.term', 'contract_id', 'Payment terms', help="Specifies payment terms"),
        'relate_default_invoice_ids': fields.one2many('relate.contract.default.invoice', 'contract_id', 'Default Invoice', help="Specifies default to invoice"),
    }
    
    def get_default_to_invoice(self, cr, uid, 
                               contract_id, 
                               journal_id, 
                               line_product_id, 
                               context=None):
        '''
        Return the invoice values seconds default invoice rules
        Params:
        contract_id
        journal_id
        line_product_id
        '''
        relate_contract_default_invoice_obj = self.pool['relate.contract.default.invoice']
        res = {}
        # Params Required
        if not contract_id or not journal_id or not line_product_id:
            return res
        # First search with specific product
        inv_def_search = [('contract_id','=', contract_id),
                          ('journal_id','=', journal_id),
                          ('line_product','=', line_product_id)]
        invoice_default_ids = relate_contract_default_invoice_obj.search(cr, uid, 
                                                    inv_def_search, 
                                                    order='line_product DESC',
                                                    limit = 1)
        # Second search generic(only journal)
        if not invoice_default_ids:
            inv_def_search = [('contract_id','=', contract_id),
                          ('journal_id','=', journal_id)]
            invoice_default_ids = relate_contract_default_invoice_obj.search(cr, uid, inv_def_search, order='line_product DESC', limit = 1)
        if invoice_default_ids:
            invoice_default = self.pool.get('relate.contract.default.invoice').browse(cr, uid, invoice_default_ids[0])
            res ={
                   'line_to_invoice': invoice_default.line_to_invoice or False,
                   'product_to_invoice': invoice_default.product_to_invoice.id or False,
                   }
        return res
        
    
    def recompute_setting_invoice_datas(self, cr, uid, ids, context=None):
        '''
        replace existing invoice datas in contract's analytic lines second default setting
        '''
        vals_reset = {
               'line_to_invoice': False,
               'product_to_invoice': False,
               'amount_to_invoice': 0.0
                }
        
        # remove all setting
        for contract in self.browse(cr, uid, ids):
            c_line_ids=[]
            for contract_line in contract.line_ids:
                c_line_ids.append(contract_line.id)
            # resetting project_task_work
            rel_ids = self.pool.get('hr.analytic.timesheet').search(cr, uid, [('line_id','in', c_line_ids)])
            if rel_ids:
                for rel in self.pool.get('hr.analytic.timesheet').browse(cr, uid, rel_ids):
                    work_ids = self.pool.get('project.task.work').search(cr, uid, [('hr_analytic_timesheet_id','=', rel.id)])
                    if work_ids:
                        self.pool.get('project.task.work').write(cr, uid, work_ids, vals_reset) 
            # resetting account analytic lines    
            self.pool.get('account.analytic.line').write(cr, uid, c_line_ids, vals_reset)                                                     
                
        # New default setting
        for contract in self.browse(cr, uid, ids):
            c_line_ids=[]
            for contract_line in contract.line_ids:
                c_line_ids.append(contract_line.id)
            # Set context 
            context['contract_id'] = contract.id
            # project_task_work ( amount will be set to the corrispondent analytic line
            rel_ids = self.pool.get('hr.analytic.timesheet').search(cr, uid, [('line_id','in', c_line_ids)])
            if rel_ids:
                for rel in self.pool.get('hr.analytic.timesheet').browse(cr, uid, rel_ids):
                    work_ids = self.pool.get('project.task.work').search(cr, uid, [('hr_analytic_timesheet_id','=', rel.id)])
                    for work in self.pool.get('project.task.work').browse(cr, uid, work_ids):
                        inv_def_search = [('contract_id','=', contract.id),('journal_id','=', rel.line_id.journal_id.id),('line_product','=', rel.line_id.product_id.id),'|',('contract_id','=', contract.id),('journal_id','=', rel.line_id.journal_id.id)]
                        invoice_default_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, inv_def_search, order='line_product DESC', limit = 1)
                        if invoice_default_ids:
                            invoice_default = self.pool.get('relate.contract.default.invoice').browse(cr, uid, invoice_default_ids[0])
                            # Compute amount : priority to default product
                            product_to_invoice = False
                            product_to_invoice_uom = False
                            coeff_cost_no_product = False
                            if invoice_default.product_to_invoice:
                                product_to_invoice = invoice_default.product_to_invoice
                                product_to_invoice_uom = invoice_default.product_to_invoice.uom_id.id
                                coeff_cost_no_product = invoice_default.coeff_cost_no_product
                            elif analytic_line.product_id:
                                product_to_invoice = analytic_line.product_id
                                product_to_invoice_uom = analytic_line.product_uom_id.id
                                coeff_cost_no_product = analytic_line.coeff_cost_no_product
                            elif invoice_default.product_for_line_without_product:
                                product_to_invoice = invoice_default.product_for_line_without_product
                                product_to_invoice_uom = invoice_default.product_for_line_without_product.uom_id.id
                                coeff_cost_no_product = invoice_default.coeff_cost_no_product
                            else:
                                product_to_invoice = False
                                product_to_invoice_uom = False
                                coeff_cost_no_product = False
                            if not product_to_invoice:
                                continue
                            amount_to_invoice = self.pool.get('account.analytic.line').get_amount_to_invoice(cr, uid, ids, product_to_invoice, work.hours, product_to_invoice_uom, invoice_default.line_to_invoice, coeff_cost_no_product, context=context)
                            new_vals ={
                                   'line_to_invoice': invoice_default.line_to_invoice or False,
                                   'product_to_invoice': invoice_default.product_to_invoice.id or False,
                                   'amount_to_invoice': amount_to_invoice['amount'] or 0.0
                                   }
                            self.pool.get('project.task.work').write(cr, uid, [work.id], new_vals)
            # analytic
            for analytic_line in contract.line_ids:
                # First search with specific product
                inv_def_search = [('contract_id','=', contract.id),('journal_id','=', analytic_line.journal_id.id),('line_product','=', analytic_line.product_id.id)]
                invoice_default_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, inv_def_search, order='line_product DESC', limit = 1)
                # Second search generic(only journal)
                if not invoice_default_ids:
                    inv_def_search = [('contract_id','=', contract.id),('journal_id','=', analytic_line.journal_id.id)]
                    invoice_default_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, inv_def_search, order='line_product DESC', limit = 1)
                if invoice_default_ids:
                    invoice_default = self.pool.get('relate.contract.default.invoice').browse(cr, uid, invoice_default_ids[0])
                    # Compute amount : priority to default product
                    coeff_cost_no_product = 0
                    if invoice_default.product_to_invoice:
                        product_to_invoice = invoice_default.product_to_invoice
                        product_to_invoice_uom = invoice_default.product_to_invoice.uom_id.id
                        coeff_cost_no_product = invoice_default.coeff_cost_no_product
                    elif analytic_line.product_id:
                        product_to_invoice = analytic_line.product_id
                        product_to_invoice_uom = analytic_line.product_uom_id.id
                        coeff_cost_no_product = invoice_default.coeff_cost_no_product
                    elif invoice_default.product_for_line_without_product:
                        product_to_invoice = invoice_default.product_for_line_without_product
                        product_to_invoice_uom = invoice_default.product_for_line_without_product.uom_id.id
                        coeff_cost_no_product = invoice_default.coeff_cost_no_product
                    else:
                        product_to_invoice = False
                        product_to_invoice_uom = False
                        coeff_cost_no_product = False
                    if not product_to_invoice:
                        continue
                    amount_to_invoice = self.pool.get('account.analytic.line').get_amount_to_invoice(cr, uid, [analytic_line.id], product_to_invoice, analytic_line.unit_amount, product_to_invoice_uom, invoice_default.line_to_invoice, coeff_cost_no_product, context=context)
                    new_vals ={
                           'line_to_invoice': invoice_default.line_to_invoice or False,
                           'product_to_invoice': product_to_invoice.id or False,
                           'amount_to_invoice': amount_to_invoice['amount'] or 0.0
                           }
                    self.pool.get('account.analytic.line').write(cr, uid, [analytic_line.id], new_vals)
        # Setting new defaults
        return True
    
    def onchange_code(self, cr, uid, ids, code, context=None):
        '''
        No duplicate code
        '''
        res ={}
        if ids:
            code_search = [('id', '!=', ids[0]), ('code', '=', code)]
        else:
            code_search = [('code', '=', code)]
        
        code_ids = self.search(cr, uid, code_search)
        if code_ids:
            contract = self.browse(cr, uid, code_ids[0])
            raise osv.except_osv(_('Error!'),_("Code already exists: %s") % (contract.name) )
            
        return res
    

    def default_get(self, cr, uid, fields, context=None):
        # Lines Default invoice from config
        res = super(account_analytic_account, self).default_get(cr, uid, fields, context=context)
        
        if not context.get('project_creation_in_progress'):
            default_line_ids = self.pool.get('relate.config.journal').search(cr, uid, [('id', '!=', False)])
            lines_default = []
            
            for line in self.pool.get('relate.config.journal').browse(cr, uid, default_line_ids):
                val = {
                    'journal_id': line.journal_id.id,
                    'line_product': line.line_product.id or False,
                    'line_to_invoice': line.line_to_invoice,
                    'product_to_invoice': line.product_to_invoice.id or False,
                    'product_for_line_without_product': line.product_for_line_without_product.id or False,
                    'coeff_cost_no_product': line.coeff_cost_no_product or False,
                    }
                lines_default.append( (0, 0, val))
            
            # Followers 
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('relate_follower_contract', '=', True)])
            followers = []
            for emp in self.pool.get('hr.employee').browse(cr, uid, employee_ids):
                if emp.user_id:
                    followers.append(emp.user_id.partner_id.id)
                if followers:
                    res.update({ 'message_follower_ids': [(6, 0, followers)]})
            
            res.update({'relate_default_invoice_ids': lines_default})
        return res