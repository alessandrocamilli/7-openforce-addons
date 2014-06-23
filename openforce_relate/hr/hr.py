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

from osv import fields, orm
from openerp.tools.translate import _

class hr_employee(orm.Model):
    
    _inherit = "hr.employee"
    _columns = {
        'relate_trip_product_id': fields.many2one('product.product', 'Product', help="Specifies employee's designation as a product with type 'service'."),
        'relate_trip_journal_id': fields.many2one('account.analytic.journal', 'Analytic Journal'),
        'relate_trip_uom_id': fields.related('product_id', 'uom_id', type='many2one', relation='product.uom', string='Unit of Measure', store=True, readonly=True),
        'relate_trip_cost_from_timesheet_coeff': fields.float('Cost from timesheet - Coeff.'),
        'relate_follower_contract': fields.boolean('Contract')
    }
    
    def on_change_follower_contract(self, cr, uid, ids, relate_follower_contract, context=None):
        '''
        Update the option follower to all contracts
        '''
        for emp in self.browse(cr, uid, ids):
            if emp.user_id:
                contracts_ids = self.pool.get('account.analytic.account').search(cr, uid, [('id', '!=', False)])
                for contract in self.pool.get('account.analytic.account').browse(cr, uid, contracts_ids):
                    foll_ids = []
                    for follower in contract.message_follower_ids:
                        foll_ids.append(follower.id)
                    # Add employee to all contract
                    if relate_follower_contract:
                        if emp.user_id.partner_id.id not in foll_ids:
                            val = [(4, emp.user_id.partner_id.id )]
                    # Remove employee from contract
                    else:
                        if emp.user_id.partner_id.id in foll_ids:
                            val = [(3, emp.user_id.partner_id.id )]
                
                    self.pool.get('account.analytic.account').write(cr, uid, [contract.id], {'message_follower_ids': val})
                    
        return True