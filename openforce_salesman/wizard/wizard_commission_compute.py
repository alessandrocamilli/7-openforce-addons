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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class salesman_commission_compute_wizard(osv.osv_memory):
    _name = "salesman.commission.compute.wizard"
    _description = "salesman.commission.compute.wizard"
    _columns = {
       'period_id': fields.many2one('account.period', 'Period', required=True, help="Choose the period for which you want to automatically post the depreciation lines of running assets"),
    }
   
    def _get_period(self, cr, uid, context=None):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        return False
 
    _defaults = {
        'period_id': _get_period,
    }

    def commission_compute(self, cr, uid, ids, context):
        ass_obj = self.pool.get('salesman.commission.item')
        '''
        asset_ids = ass_obj.search(cr, uid, [('state','=','open')], context=context)
        data = self.browse(cr, uid, ids, context=context)
        period_id = data[0].period_id.id
        created_move_ids = ass_obj._compute_entries(cr, uid, asset_ids, period_id, context=context)
        '''
        #>> deve andare nelle provvigioni del periodo scelto
        return {
            'type': 'ir.actions.act_window_close',
        }
        '''
        return {
            'name': _('Created Asset Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'domain': "[('id','in',["+','.join(map(str,created_move_ids))+"])]",
            'type': 'ir.actions.act_window',
        }'''

salesman_commission_compute_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
