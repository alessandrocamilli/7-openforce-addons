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

import pooler, tools
from osv import fields, orm
from tools.translate import _

class account_invoice(orm.Model):
    
    _inherit = "account.invoice"

    def action_number(self, cr, uid, ids, context=None):
        
        for obj_inv in self.browse(cr, uid, ids, context=context):
            
            if obj_inv.supplier_invoice_number:
                duplicate_search = [
                                    ('id','!=', obj_inv.id), 
                                    ('date_invoice','=', obj_inv.date_invoice), 
                                    ('supplier_invoice_number','=', obj_inv.supplier_invoice_number), 
                                    ('number','!=', False), 
                                    ('partner_id','=', obj_inv.partner_id.id), 
                                    ]
                duplicate_ids = self.pool.get('account.invoice').search(cr, uid, duplicate_search)
                
                if len(duplicate_ids) > 0:
                    inv_duplicate = self.browse(cr, uid, duplicate_ids[0])
                    raise orm.except_orm(_('Invoice already exists !'),_("Show number %s") % (inv_duplicate.number,) )
        
        return super(account_invoice, self).action_number(cr, uid, ids, context=None)
