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
from openerp.osv import orm, fields

class stock_picking(orm.Model):
    
    _inherit = "stock.picking"
    
    #
    # TODO: change and create a move if not parents
    #
    def action_done(self, cr, uid, ids, context=None):
        '''
        If date_done manually setup, it mustn't change
        '''
        reset_date ={}
        for picking in self.browse(cr, uid, ids):
            if picking.date_done:
                reset_date[picking.id] = picking.date_done
        
        res = super(stock_picking, self).action_done(cr, uid, ids, context=None)
        
        for picking_id in reset_date:
            self.write(cr, uid, [picking_id], {'date_done': reset_date[picking_id]})
        return True
