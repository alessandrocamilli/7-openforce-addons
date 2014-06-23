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

from osv import osv, orm
from osv import fields
from tools.translate import _

class account_journal(orm.Model):
    
    _inherit = "account.journal"
    _columns = {
        'selection_sequence': fields.integer('Selection sequence', help="Order to choose the default journal"),
    }
    _defaults = {
        'selection_sequence': 5
    }
    _order = 'selection_sequence, code'


class account_fiscal_position(orm.Model):
    
    _inherit = "account.fiscal.position"
    
    _columns = {
        'sale_invoice_journal_id': fields.many2one('account.journal', 'Default Journal Sale Invoice'),
        'purchase_invoice_journal_id': fields.many2one('account.journal', 'Default Journal Purchase Invoice'),
    }     

class account_invoice(orm.Model):
    '''
    Select default journal second the right sequence
    '''
    
    _inherit = "account.invoice"
    
    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = super(account_invoice,self)._get_journal(cr, uid, context)
        
        type_inv = context.get('type', 'out_invoice')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        type2journal = {'out_invoice': 'sale', 'in_invoice': 'purchase', 'out_refund': 'sale_refund', 'in_refund': 'purchase_refund'}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('type', '=', type2journal.get(type_inv, 'sale')),
                                            ('company_id', '=', company_id)],
                                                order='selection_sequence', limit=1)
        
        return res and res[0] or False
    
    def onchange_fiscal_position(self, cr, uid, ids, fiscal_position_id=False, type=None, context=None):
        if not context:
            context = {}
        result = {}
        default = {}
        fiscal_position_obj = self.pool['account.fiscal.position']
        if fiscal_position_id:
            fiscal_position = fiscal_position_obj.browse(cr, uid, fiscal_position_id, context=context)
            if type == 'purchase' and fiscal_position.purchase_invoice_journal_id:
                default['journal_id'] = fiscal_position.purchase_invoice_journal_id.id
            if type == 'sale' and fiscal_position.sale_invoice_journal_id:
                default['journal_id'] = fiscal_position.sale_invoice_journal_id.id
        # default with second
        if not default:
            if type == 'purchase':
                context.update({'type' : 'in_invoice'})
            if type == 'sale':
                context.update({'type' : 'out_invoice'})
            default['journal_id'] = self._get_journal(cr, uid, context)
        
        result['value'] = default
        
        return result
    
