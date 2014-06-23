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

from osv import fields, osv, orm
from openerp.tools.translate import _


class account_analytic_line(orm.Model):
    _inherit = 'account.analytic.line'
    _columns = {
        'stock_move_id': fields.many2one('stock.move', 'Stock move'),
    }
    
    
class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    
    def do_partial(self, cr, uid, ids, context=None):
        '''
        Create analytic lines for purchase moves
        '''
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context=None)
        
        #import pdb
        #pdb.set_trace()
        # Take picking done
        partial_picking = self.browse(cr, uid, ids[0])
        if partial_picking.picking_id.backorder_id:
            picking = partial_picking.picking_id.backorder_id
        else:
            picking = partial_picking.picking_id
        if picking.type == 'in':
            for move in picking.move_lines:
                if move.purchase_line_id:
                    
                    self.pool.get('stock.move')._create_analytic_lines(cr, uid, [move.id] ,move.purchase_line_id.id)
        return res


class stock_move(orm.Model):
    
    _inherit = 'stock.move'
    _columns = {
        'analytic_lines': fields.one2many('account.analytic.line', 'stock_move_id', 'Analytics line'),
    }
    
    def _create_analytic_lines(self, cr, uid, ids, purchase_line_id, context=None):
        '''
        Create analytic lines for purchase moves
        '''
        #import pdb
        #pdb.set_trace()
        purchase_order_line_obj = self.pool.get('purchase.order.line')
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        
        for move in self.browse(cr, uid, ids):
            
            # purchase move
            if purchase_line_id:
                purchase_line = purchase_order_line_obj.browse(cr, uid, purchase_line_id)
                
                # Journal for purchase
                analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('type','=', 'purchase')])
                if not analytic_journal_ids:
                    raise osv.except_osv(_('Error!'),_("Set the analytic journal for purchase "))
                analytic_journal = analytic_journal_obj.browse(cr, uid, analytic_journal_ids[0])
               # Account 
                default_account = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
                
                if purchase_line.account_analytic_id:
                    analytic_vals = [(0,0, {
                        'stock_move_id': move.id, # link with stock move
                        'name': purchase_line.name,
                        'date': move.date,
                        'account_id': purchase_line.account_analytic_id.id,
                        'unit_amount': move.product_qty,
                        'amount': round(-1.00 * move.product_qty * purchase_line.price_unit * (1 - (purchase_line.discount or 0.0) / 100.0) * (1 - (purchase_line.discount2 or 0.0) / 100.0), self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')) ,
                        'product_id': move.product_id.id,
                        'product_uom_id': move.product_uom.id,
                        'general_account_id': default_account.id or False,
                        'journal_id': analytic_journal.id,
                        #'ref': ref,
                    })]
                    
                    self.write(cr, uid, [move.id], {'analytic_lines' : analytic_vals})
        return True
    

class stock_picking(orm.Model):
    
    _inherit = 'stock.picking'

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        '''Remove analytics line created by stock move to avoid duplication with analytic lines created by invoice'''
        #import pdb
        #pdb.set_trace()
        for line in move_line.analytic_lines:
            self.pool.get('account.analytic.line').unlink(cr, uid, line.id)
            
        return super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)
    