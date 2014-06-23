# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (alessandrocamilli@openforce.it)
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
from osv import osv, fields, orm
from openerp.tools.translate import _

class res_partner(orm.Model):
    
    _inherit = 'res.partner'
   
    def _credit_debit_maturity_get(self, cr, uid, ids, field_names, arg, context=None):
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
        cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit),
                      SUM(CASE WHEN a.type = 'receivable' and DATE(date_maturity) <= current_Date THEN l.debit ELSE 0 END) as credit_expired,
                      SUM(CASE WHEN a.type = 'receivable' and DATE(date_maturity) > current_Date THEN l.debit ELSE 0 END) as credit_to_expire,
                      SUM(CASE WHEN a.type = 'payable' and DATE(date_maturity) <= current_Date THEN l.credit ELSE 0 END) as debit_expired,
                      SUM(CASE WHEN a.type = 'payable' and DATE(date_maturity) > current_Date THEN l.credit ELSE 0 END) as debit_to_expire
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      WHERE a.type IN ('receivable','payable')
                      AND l.partner_id IN %s
                      AND l.reconcile_id IS NULL
                      AND """ + query + """
                      GROUP BY l.partner_id, a.type
                      """,
                   (tuple(ids),))
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for pid,type,val,c_expired, c_to_expire, d_expired, d_to_expire in cr.fetchall():
            if val is None: val=0
            if type == 'receivable':
                res[pid]['credit_expired'] = c_expired
                res[pid]['credit_to_expire'] = c_to_expire
            else:
                res[pid]['debit_expired'] = d_expired
                res[pid]['debit_to_expire'] = d_to_expire
                
        return res
    
    def _credit_debit_limit_residual_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for partner in self.browse(cr, uid, ids):
            res[partner.id]['credit_limit_residual'] = partner.credit_limit - partner.credit_expired - partner.credit_to_expire
            res[partner.id]['debit_limit_residual'] = partner.debit_limit - partner.debit_expired - partner.debit_to_expire
        return res
    
    _columns = {
        'credit_to_expire': fields.function(_credit_debit_maturity_get,
             string='Total Receivable To Expire', multi='dc_m', help="Amount this customer owes you. To expire."),
        'credit_expired': fields.function(_credit_debit_maturity_get,
             string='Total Receivable Expired', multi='dc_m', help="Amount this customer owes you. Expired"),
        'debit_to_expire': fields.function(_credit_debit_maturity_get,
             string='Total Payable To Expire', multi='dc_m', help="Amount this customer owes you. To expire."),
        'debit_expired': fields.function(_credit_debit_maturity_get,
             string='Total Payable Expired', multi='dc_m', help="Amount this customer owes you. Expired"),
        'credit_limit_residual': fields.function(_credit_debit_limit_residual_get,
             string='Total Credit Limit Residual', multi='dc_limit_residual', help="Amount Residual of Credit Limit"),
        'debit_limit_residual': fields.function(_credit_debit_limit_residual_get,
             string='Total Debit Limit Residual', multi='dc_limit_residual', help="Amount Residual of Debit Limit"),
    }
    