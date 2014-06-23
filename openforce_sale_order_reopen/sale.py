# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Alessandro Camilli <a.camilli@yahoo.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import fields, orm
from openerp import netsvc
from openerp.tools.translate import _

class sale_order(orm.Model):
    _inherit = "sale.order"
    
    def action_reopen_to_draft(self, cr, uid, ids, *args):
        '''
        set to draft
        '''
        if not len(ids):
            return False
        # invoice
                #cr.execute('select id from sale_order_line where order_id IN %s and state=%s', (tuple(ids), 'cancel'))
        cr.execute('select id from sale_order_line where order_id IN %s ', (tuple(ids), ))
        line_ids = map(lambda x: x[0], cr.fetchall())
        self.write(cr, uid, ids, {'state': 'draft', 'invoice_ids': [], 'shipped': 0})
        
        # picking
        stock_move_ids = []
        for line_order in self.pool.get('sale.order.line').browse(cr, uid, line_ids):
            print "xxx"
            for stock_move in line_order.move_ids:
                picking_out = self.pool.get('stock.picking.out').browse(cr, uid, stock_move.picking_id.id)
                #picking_out.action_reopen(cr, uid, [picking_out.id], context=None)
                picking_out.action_reopen([picking_out.id])
                # Leave only header of picking to recicle at the new order confirm
                for line_new_state in picking_out.move_lines:
                    self.pool.get('stock.move').write(cr, uid, [line_new_state.id], {'state': 'draft'})
                    self.pool.get('stock.move').unlink(cr, uid, [line_new_state.id])
                    #line_new_state.unlink([line_new_state.id])
                stock_move_ids.append(stock_move.id)
                
        
        #self.pool.get('sale.order.line').write(cr, uid, line_ids, {'invoiced': False, 'state': 'draft', 'invoice_lines': [(6, 0, [])]})
        self.pool.get('sale.order.line').write(cr, uid, line_ids, {'invoiced': False, 'state': 'draft', 'invoice_lines': [(6, 0, [])], 'move_ids': [(6, 0, [])]})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            # Deleting the existing instance of workflow for SO
            wf_service.trg_delete(uid, 'sale.order', inv_id, cr)
            wf_service.trg_create(uid, 'sale.order', inv_id, cr)
        return True
    
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        '''
        Avoid to reconfigure delivery datas
        '''
        # Recicle delivery in draft state after reopen
        if order.picking_ids and not picking_id:
            picking_id = order.picking_ids[0].id
            
        res = super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id=picking_id, context=context)
        
        return res
            
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
