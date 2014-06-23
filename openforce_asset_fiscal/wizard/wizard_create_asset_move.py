# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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

from osv import fields,osv
from tools.translate import _
import time

class wizard_create_asset_move(osv.osv_memory):
    
    def _get_invoice_type(self, cr, uid, context=None):
        import pdb
        pdb.set_trace()
        if context is None:
            context = {}
        return context.get('invoice_type')

    _name = "wizard.create.asset.move"
    _columns = {
        'invoice_type': fields.char('Invoice_type', size=64, readonly=True),
        'move_type': fields.selection([('variation','Variation')],"Move type"),
        'move_type_sale': fields.selection([('sale','Sale'),
                                                ('disposal','Disposal'),
                                                ('variation_negative','Negative variation')],
                                                "Move type"),
        'move_type_purchase': fields.selection([('purchase','Purchase'),
                                                ('improvement','Improvement'),
                                                ('variation_positive','Positive variation')],
                                               "Move type"),
        #'category_id': fields.many2one('account.asset.category', 'Category', required=True),
        'category_id': fields.many2one('account.asset.category', 'Category'),
        'asset_id': fields.many2one('account.asset.asset', 'Asset', 
                domain="[('category_id','=', category_id)]"),
                #domain="[('category_id','=', category_id)]", required=True),
        'account_depreciation_id': fields.many2one('account.account', 'Depr. Account'),
        'amount_depreciation': fields.float('Amount depreciation'),
        'amount_gain_loss': fields.float('Amount gain or loss'),
        'account_gain_id': fields.many2one('account.account', 'Gain Account'),
        'account_loss_id': fields.many2one('account.account', 'Loss Account'),
    }
    
    _default = {
        'invoice_type': _get_invoice_type        
    }
    
    def default_get(self, cr, uid, fields, context=None):
        import pdb
        pdb.set_trace()
        asset_category_obj = self.pool.get('account.asset.category')
        res = super(wizard_create_asset_move, self).default_get(cr, uid, fields, context=context)
        
        invoice_line = self.pool.get('account.invoice.line').browse(cr, uid, context['active_id'], context=context)
        if invoice_line.invoice_id.type == 'in_invoice':
            invoice_type = 'in_invoice'
        else:
            invoice_type = 'out_invoice'
        res['invoice_type'] = invoice_type
        
        asset_categories = asset_category_obj.search(cr, uid, [('account_asset_id','=',invoice_line.account_id.id)])
        if asset_categories :
            res['category_id'] = asset_categories[0]
        return res
    
    def move_type_choice(self, cr, uid, ids, context=None):
        import pdb
        pdb.set_trace()
        view_res = self.pool.get('ir.ui.view').search(cr, uid, [('name','=','Create asset move'),('model','=','wizard.create.asset.move')])

        result = {
            'view_type' : 'form',
            'view_mode' : 'form',
            'view_id' : view_res,
            'res_model' : 'wizard.create.asset.move',
            'type' : 'ir.actions.act_window',
            'target' : 'new',
            'context' : context,
        }
        return result
    
    def create_move(self, cr, uid, ids, context=None):
        import pdb
        pdb.set_trace()
        print 'XXX'
        '''
        picking_obj = self.pool.get('stock.picking')
        for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if picking.ddt_number:
                raise osv.except_osv('Error', _('DTT number already assigned'))
            picking.write({
                'ddt_number': self.pool.get('ir.sequence').get(cr, uid, 'stock.ddt'),
                'ddt_date': time.strftime('%Y-%m-%d'),
                })
        '''
        return {
            'type': 'ir.actions.act_window_close',
        }
    
    def onchange_move_type_sale(self, cr, uid, ids, move_type, context=None):
        res ={}
        import pdb
        pdb.set_trace()
        
        return res

    def onchange_move_type_purchase(self, cr, uid, ids, move_type, context=None):
        res ={}
        import pdb
        pdb.set_trace()
        
        return res

wizard_create_asset_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
