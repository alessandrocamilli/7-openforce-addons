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

class wizard_assign_ddt_by_journal(osv.osv_memory):

    _inherit = "wizard.assign.ddt.by.journal"
        
    _columns={
        'ddt_number_manual': fields.char('DDT number manual', size=64),
        'ddt_date_manual': fields.date('DDT date manual'),
    }

    def assign_ddt_by_journal(self, cr, uid, ids, context=None):
        form = {}
        for wiz_obj in self.read(cr,uid,ids):
            form['ddt_number_manual'] = wiz_obj['ddt_number_manual']
            form['ddt_date_manual'] = wiz_obj['ddt_date_manual']
        
        picking_obj = self.pool.get('stock.picking')
        for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            if picking.ddt_number:
                raise osv.except_osv('Error', _('DTT number already assigned'))
            
            if form['ddt_number_manual']:
                ddt_number = form['ddt_number_manual']
            else:
                # Assign nr ddt from journal's sequence
                if picking.stock_journal_id.ddt_sequence:
                    ddt_number = self.pool.get('ir.sequence').get(cr, uid, picking.stock_journal_id.ddt_sequence.code)
                else:
                    ddt_number = self.pool.get('ir.sequence').get(cr, uid, 'stock.ddt')
                
            if form['ddt_date_manual']:
                ddt_date = form['ddt_date_manual']
            else:
                ddt_date = time.strftime('%Y-%m-%d')
                
            picking.write({
                'ddt_number': ddt_number,
                'ddt_date': ddt_date,
                })
        return {
            'type': 'ir.actions.act_window_close',
        }

wizard_assign_ddt_by_journal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
