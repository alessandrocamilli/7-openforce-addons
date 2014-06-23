# -*- coding: utf-8 -*-

#################################################################################
#    Author: Alessandro Camilli a.camilli@yahoo.it
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
##############################################################################

from osv import fields, osv
from tools.translate import _
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    
    #_columns =  {
    #}
    
    def link_asset(self, cr, uid, ids, context=None):
        import pdb
        pdb.set_trace()
        
        for inv in self.browse(cr, uid, ids, context=context):
            print 'xx'
        #    if asset.method == 'percent' and len(asset.percent_ids) != asset.method_number:
        #        return False
        
        mod_obj = self.pool.get('ir.model.data')
        if move.parent_production_id:
            res = mod_obj.get_object_reference(cr, uid, 'module_name', 'id_specified_for_the_view')
        return {
            'name': 'Provide your popup window name',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res and res[1] or False],
            'res_model': 'your.popup.model.name',
            'context': "{}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': record_id  or False,##please replace record_id and provide the id of the record to be opened 
        }   
        
    
        return True
account_invoice()

class account_move_line(osv.osv):
    _name = "account.move.line"
    _inherit = "account.move.line"
    
    _columns =  {
        'asset_invoice_line_id': fields.integer('invoice line id link to asset'),
    }
account_move_line()
    
class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    
    _columns =  {
        'asset_move_line_id': fields.many2one('account.move.line', 'Asset move', readonly=True),
    }
account_invoice_line() 