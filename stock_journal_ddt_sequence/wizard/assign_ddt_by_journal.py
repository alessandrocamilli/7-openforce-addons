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

from osv import fields,osv
from tools.translate import _
import time

class wizard_assign_ddt_by_journal(osv.osv_memory):

    _name = "wizard.assign.ddt.by.journal"

    def assign_ddt_by_journal(self, cr, uid, ids, context=None):
        
        picking_obj = self.pool.get('stock.picking')
        for picking in picking_obj.browse(cr, uid, context.get('active_ids', []), context=context):
            
            if picking.ddt_number:
                raise osv.except_osv('Error', _('DTT number already assigned'))
            
            # Assign nr ddt from journal's sequence
            if picking.stock_journal_id.ddt_sequence:
                picking.write({
                    'ddt_number': self.pool.get('ir.sequence').get(cr, uid, picking.stock_journal_id.ddt_sequence.code),
                    'ddt_date': time.strftime('%Y-%m-%d'),
                    })
            else:
                picking.write({
                    'ddt_number': self.pool.get('ir.sequence').get(cr, uid, 'stock.ddt'),
                    'ddt_date': time.strftime('%Y-%m-%d'),
                    })
        return {
            'type': 'ir.actions.act_window_close',
        }

wizard_assign_ddt_by_journal()

