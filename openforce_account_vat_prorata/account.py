# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (alessandrocamilli@openforce.it)
#    Copyright (C) 2014
#    Openforce (<http://www.openforce.it>)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class account_tax(orm.Model):
    _inherit = "account.tax"
    _columns = {
        'prorata_base_non_deductible': fields.boolean('Base Non Deductible', help="Base will consider inn the denominator in the prorata compute"),
        'prorata_base_exclude_from_compute': fields.boolean('Exclude from compute', help="Base will not consider in the prorata compute"),
        }
  
class statement_credit_undeductible_prorata_account_line(orm.Model):
    _name='statement.credit.undeductible.prorata.account.line'
    
    def _get_period_ref(self, cr, uid, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids):
            period_ref = ""
            for period in line.statement_id.period_ids:
                if period_ref:
                    period_ref += ", "
                period_ref += period.name
            res[line.id] = period_ref.replace('/', '-')
            val = {
                'period_ref': period_ref
                }
        return res
    
    _columns = {
        'account_id': fields.many2one('account.account', 'Account', required=True),
        'statement_id': fields.many2one('account.vat.period.end.statement', 'VAT statement'),
        'amount': fields.float('Amount', digits_compute= dp.get_precision('Account'), required=True),
        'prorata_statement_id': fields.many2one('account.vat.prorata.statement', 'Pro-Rata VAT statement'),
        'period_ref': fields.function(_get_period_ref, method=True,  
            type='char', string='Period Ref'),
        }
    
class account_vat_period_end_statement(orm.Model):
    _inherit = "account.vat.period.end.statement"
    
    def _compute_total_vat_end_period_amount(self, cr, uid, ids, field_name, arg, context):
        res={}
        for i in ids:
            statement = self.browse(cr, uid, i)
            
            debit_vat_amount = 0.0
            credit_vat_amount = 0.0
            credit_undeductible_vat_amount = 0.0
            for debit_line in statement.debit_vat_account_line_ids:
                debit_vat_amount += debit_line.amount
            for credit_line in statement.credit_vat_account_line_ids:
                credit_vat_amount += credit_line.amount
            for credit_undeductible_line in statement.credit_vat_undeducible_prorata_account_line_ids:
                credit_undeductible_vat_amount += credit_undeductible_line.amount
            tot_end_vat_amount = (debit_vat_amount - credit_vat_amount + credit_undeductible_vat_amount)
            res[i] = tot_end_vat_amount
        return res
    
    def _compute_authority_vat_amount(self, cr, uid, ids, field_name, arg, context):
        res = super(account_vat_period_end_statement, self)._compute_authority_vat_amount(cr, uid, ids, field_name, arg, context=context)
        # Credit undeductible to consider
        for st_id, st_amount in res.iteritems():
            statement = self.browse(cr, uid, st_id)
            credit_undeductible_vat_amount = 0.0
            for credit_undeductible_line in statement.credit_vat_undeducible_prorata_account_line_ids:
                    credit_undeductible_vat_amount += credit_undeductible_line.amount
            res[st_id] += credit_undeductible_vat_amount
            
        return res
    
    _columns = {
         'credit_vat_undeducible_prorata_account_line_ids': fields.one2many('statement.credit.undeductible.prorata.account.line', 'statement_id', 'Credit VAT Undeductible Pro-Rata', help='', states={'confirmed': [('readonly', True)], 'paid': [('readonly', True)], 'draft': [('readonly', False)]}),       
         'total_vat_end_period_amount': fields.function(_compute_total_vat_end_period_amount, method=True, string='Total VAT Amount'),
         # for new recompute with prorata
         'authority_vat_amount': fields.function(_compute_authority_vat_amount, method=True, string='Authority VAT Amount'),
        }
    
    def compute_amounts(self, cr, uid, ids, context=None):
        '''
        Line of Pro-Rata in the generic account section
        '''
        account_vat_prorata_statement_obj = self.pool['account.vat.prorata.statement']
        statement_credit_undeductible_prorata_line_obj = self.pool['statement.credit.undeductible.prorata.account.line']
        decimal_precision_obj = self.pool['decimal.precision']
        
        res = super(account_vat_period_end_statement, self).compute_amounts(cr, uid, ids, context=context)
        
        for end_st in self.browse(cr, uid, ids):
            # First Fiscal year of period for competence
            competence_fiscalyear_id = end_st.period_ids[0].fiscalyear_id.id
            
            domain = [('fiscalyear_id', '=', competence_fiscalyear_id), ('state', '=', 'open')]
            prorata_st_ids = account_vat_prorata_statement_obj.search(cr, uid, domain)
            if not prorata_st_ids:
                continue
            prorata_st = account_vat_prorata_statement_obj.browse(cr, uid, prorata_st_ids[0])
            
            tot_vat_credit = 0
            tot_vat_credit_deductible = 0
            tot_vat_credit_non_deductible = 0
            if prorata_st.prorata_presumed:
                for line in end_st.credit_vat_account_line_ids:
                    tot_vat_credit += line.amount
                if tot_vat_credit > 0:
                    tot_vat_credit_deductible = round(tot_vat_credit * (float(prorata_st.prorata_presumed) / 100), decimal_precision_obj.precision_get(cr, uid, 'Account'))
                    tot_vat_credit_non_deductible = round(tot_vat_credit - tot_vat_credit_deductible, decimal_precision_obj.precision_get(cr, uid, 'Account'))
            
            if prorata_st.end_vat_period_account_id and tot_vat_credit_non_deductible > 0:
                # Unlink pro-rata account from generic section
                domain = [('statement_id', '=', end_st.id), ('account_id', '=', prorata_st.end_vat_period_account_id.id)]
                gen_acc_ids = statement_credit_undeductible_prorata_line_obj.search(cr, uid, domain)
                statement_credit_undeductible_prorata_line_obj.unlink(cr, uid, gen_acc_ids)
                # Add pro-rata account
                val= {
                    'statement_id' : end_st.id,
                    'account_id' : prorata_st.end_vat_period_account_id.id,
                    'amount' : tot_vat_credit_non_deductible,
                    'prorata_statement_id' : prorata_st.id
                    }
                statement_credit_undeductible_prorata_line_obj.create(cr, uid, val)
                
        return res

class account_vat_prorata_statement(orm.Model):
    
    _name = "account.vat.prorata.statement"
    _description = "Account Vat Pro-Rata"
    
    
    def _check_one_fiscalyear(self, cr, uid, ids, context=None):
        for element in self.browse(cr, uid, ids, context=context):
            element_ids = self.search(cr, uid, [('fiscalyear_id','=', element.fiscalyear_id.id)], context=context)
            if len(element_ids) > 1:
                return False
        return True
    
    def _tot_base(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        tot_deductible = 0
        tot_non_deductible = 0
        for statement in self.browse(cr, uid, ids):
            # Deductible
            for line in statement.base_deductible_line_ids:
                tot_deductible += line.base_amount
            # NON Deductible
            for line in statement.base_non_deductible_line_ids:
                tot_non_deductible += line.base_amount
                
            res[statement.id] = {
                    'total_deductible' : tot_deductible,
                    'total_non_deductible' : tot_non_deductible,
                    }
        return res
    
    _columns = {
        'state' : fields.selection([
            ('draft','Draft'),
            ('open','Running'),
            ('close','Closed')], 'Status', select=True, required=True, readonly=True, track_visibility='onchange',
            help=' * The \'Draft\' status is used when any End Vat statement is done. \
                \n* The \'Open\' status is used in the actualy year \
                \n* The \'Done\' status is used when the account year is closed'),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'prorata_presumed': fields.integer('Pro-Rata presumed', help="Computed from previous fiscal year"),
        'end_vat_period_account_id': fields.many2one('account.account', 'End Vat Period Account', required=True),
        'registration_balance': fields.many2one('account.move', 'VAT Balance Statement move', readonly=True),
        'prorata_effective': fields.integer('Pro-Rata effective', help="Computed at the end of this fiscal year", readonly=True),
        'base_deductible_line_ids': fields.one2many('account.vat.prorata.base.deductible.line', 'statement_id', 'Base Deductible', help='', readonly=True),
        'base_non_deductible_line_ids': fields.one2many('account.vat.prorata.base.non.deductible.line', 'statement_id', 'Base Non Deductible', help='', readonly=True ),
        'total_deductible': fields.function(_tot_base, string='Tot Base Deductible', multi='tot_base'),
        'total_non_deductible': fields.function(_tot_base, string='Tot Base Non Deductible', multi='tot_base'),
        
        'end_vat_period_line_ids': fields.one2many('statement.credit.undeductible.prorata.account.line', 'prorata_statement_id', 'Lines of End Vat Period', help='' ,readonly=True),
    }
    _defaults = {
        'state': 'draft',
    }
    _constraints = [
        (_check_one_fiscalyear, 'Error! Fiscal Year already exists.', ['fiscalyear_id']),
    ]

    def compute_prorata(self, cr, uid, ids, context=None):
        
        account_tax_obj = self.pool['account.tax']
        account_tax_code_obj = self.pool['account.tax.code']
        base_deductible_line_obj = self.pool['account.vat.prorata.base.deductible.line']
        base_non_deductible_line_obj = self.pool['account.vat.prorata.base.non.deductible.line']
        
        # unlink lines already exists
        for statement in self.browse(cr, uid, ids):
            domain = [('statement_id', '=', statement.id)]
            base_deductible_line_ids = base_deductible_line_obj.search(cr, uid, domain)
            base_deductible_line_obj.unlink(cr, uid, base_deductible_line_ids)
            base_deductible_non_line_ids = base_non_deductible_line_obj.search(cr, uid, domain)
            base_non_deductible_line_obj.unlink(cr, uid, base_deductible_non_line_ids)
        
        # Tax code selection 
        # ... Deductible
        cr.execute("SELECT c.id as tax_code_id, t.id as tax_id FROM account_tax t \
            LEFT JOIN account_tax_code c ON c.id = t.base_code_id \
            WHERE t.active = True AND c.id is not Null  AND t.base_sign > 0 \
                AND t.prorata_base_exclude_from_compute is not True \
                AND t.prorata_base_non_deductible is not True \
            GROUP BY c.id, t.id")
        tax_code_deductible_ids = [code[0] for code in cr.fetchall()]
        # ... NON Deductible
        cr.execute("SELECT c.id as tax_code_id, t.id as tax_id FROM account_tax t \
            LEFT JOIN account_tax_code c ON c.id = t.base_code_id \
            WHERE t.active = True AND c.id is not Null AND t.base_sign > 0 \
                AND t.prorata_base_exclude_from_compute is not True \
                AND t.prorata_base_non_deductible is True \
            GROUP BY c.id, t.id")
        tax_code_non_deductible_ids = [code[0] for code in cr.fetchall()]
        
        base_deductible_line = []
        base_non_deductible_line = []
        for statement in self.browse(cr, uid, ids):
            
            for period in statement.fiscalyear_id.period_ids:
                if period.special:
                    continue
                context.update({'period_id':  period.id})
                name = "xx"
                args = {}
                # Deductibles
                tax_codes = account_tax_code_obj._sum_period(cr, uid, tax_code_deductible_ids, name, args, context)
                for tax_code in tax_codes.iteritems():
                    val = {
                        'statement_id' : statement.id,
                        'period_id' : period.id,
                        'tax_code_id' : tax_code[0], # account_id
                        'base_amount' : tax_code[1], # value
                        }
                    #base_deductible_line.append((0, 0, val))
                    base_deductible_line_obj.create(cr, uid, val)
                # NON Deductible
                if not tax_code_non_deductible_ids:
                    raise orm.except_orm(_('Any tax with Base Pro-Rata Non deductible!'),_("You must set almost one tax with Base Pro-Rata Non Deductible "))
                tax_codes = account_tax_code_obj._sum_period(cr, uid, tax_code_non_deductible_ids, name, args, context)
                for tax_code in tax_codes.iteritems():
                    val = {
                        'statement_id' : statement.id,
                        'period_id' : period.id,
                        'tax_code_id' : tax_code[0], # account_id
                        'base_amount' : tax_code[1], # value
                        }
                    #base_non_deductible_line.append((0, 0, val))
                    base_non_deductible_line_obj.create(cr, uid, val)
            
            # Compute Pro-Rata
            # Arrotondamento matematico all'unità. Occorre considerare 3 decimali
            prorata_to_round = '{:16.3f}'.format( statement.total_deductible / ( statement.total_deductible + statement.total_non_deductible ) * 100 )
            prorata = round(float(prorata_to_round), 0)
            
            self.write(cr, uid, [statement.id], {'prorata_effective': prorata, 'base_deductible_line_ids': base_deductible_line, 'base_non_deductible_line_ids': base_non_deductible_line })
        
        return True
    
    def condition_set_to_draft(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if len(line.end_vat_period_line_ids) > 0:
                raise orm.except_orm(_('Pro-Rata in End Vat Period!'),_("It's not possible set to draft a statement already present in a End Vat Period Statement "))
                return False 
        return True

    
class account_vat_prorata_base_deductible_line(orm.Model):
    _name='account.vat.prorata.base.deductible.line'
    _columns = {
        'statement_id': fields.many2one('account.vat.prorata.statement', 'Prorata VAT statement', ondelete="cascade"),
        'period_id': fields.many2one('account.period', 'Period', readonly=True),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', readonly=True),
        'base_amount': fields.float('Base amount', digits_compute= dp.get_precision('Account'), readonly=True),
        }
class account_vat_prorata_base_non_deductible_line(orm.Model):
    _name='account.vat.prorata.base.non.deductible.line'
    _columns = {
        'statement_id': fields.many2one('account.vat.prorata.statement', 'Prorata VAT statement', ondelete="cascade"),
        'period_id': fields.many2one('account.period', 'Period', readonly=True),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', readonly=True),
        'base_amount': fields.float('Base amount', digits_compute= dp.get_precision('Account'), readonly=True),
        }
    