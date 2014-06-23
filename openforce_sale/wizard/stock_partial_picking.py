# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
#    All Rights Reserved
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

import netsvc
import pooler, tools
import decimal_precision as dp
import datetime
from osv import osv, orm, fields
from openerp.tools.translate import _


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    
    def do_partial(self, cr, uid, ids, context=None):
        '''
        Show picking completed and no the picking waiting delivery
        '''
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=None)
        
        partial_picking = self.browse(cr, uid, ids[0])
        picking = partial_picking.picking_id
        # Only picking out
        if picking.type == 'in':
            return res
        
        if picking.state == 'done':
            return res
        
        res_id = picking.backorder_id.id or False
        
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'openforce_sale', 'openforce_stock_picking_form_ddt_inherit')
        return {
        'name': _('Stock picking'),
        'view_type': 'form',
        'view_mode': 'form',
        'view_id': view_ref[1] or False,
        'res_model': 'stock.picking.out',
        'res_id': res_id or False,
        #'context': "{'type':'out_invoice'}",
        'type': 'ir.actions.act_window',
        'nodestroy': True,
        'target': 'current',
        'domain': '[]',
    }
