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

from osv import fields,osv
from tools.translate import _
import time
import base64
import csv
import os

class stock(osv.osv_memory):
    
    _name = "openforce.utility.stock"
    
    _description = 'Use this wizard to work with stock'
    
    def aligns_price_from_sale_order(self, cr, uid, ids, data, context=None):
         move_ids = self.pool.get('stock.move').search(cr, uid, [('sale_line_id', '!=',  False)])
         if move_ids:
             for move in self.pool.get('stock.move').browse(cr, uid, move_ids):
                 #print move.id 
                 if move.sale_line_id:
                     line = move.sale_line_id
                     new_price = round(line.price_unit *  (1-(line.discount or 0.0)/100.0) * (1-(line.discount2 or 0.0)/100.0) , self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
                     
                     self.pool.get('stock.move').write(cr, uid, [move.id], {'price_unit' : new_price})
                     
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: