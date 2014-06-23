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
from osv import fields, osv


class stock_picking_out(osv.osv):
    
    _inherit = "stock.picking.out"
    
    def _get_mezzo_default(self,cr,uid,context=None):
        res = {}
        res = self.pool.get('stock.picking.mezzo').search(cr, uid, [('name','=','VETTORE')])
        return res
    
    def _get_carriage_condition_default(self,cr,uid,context=None):
        #import pdb
        #pdb.set_trace()
        res = {}
        res = self.pool.get('stock.picking.carriage_condition').search(cr, uid, [('name','=','PORTO FRANCO')])
        return res
    
    def _get_goods_description_default(self,cr,uid,context=None):
        res = {}
        res = self.pool.get('stock.picking.goods_description').search(cr, uid, [('name','=','SCATOLE')])
        return res
    
    def _get_transportation_reason_default(self,cr,uid,context=None):
        res = {}
        res = self.pool.get('stock.picking.transportation_reason').search(cr, uid, [('name','=','VENDITA')])
        return res
    
    def _get_carrier_default(self,cr,uid,context=None):
        res = {}
        res = self.pool.get('delivery.carrier').search(cr, uid, [('name','=','Generico')])
        return res
    
    
    _defaults = {
        'mezzo_id': _get_mezzo_default,
        'carriage_condition_id' : _get_carriage_condition_default,
        'goods_description_id' : _get_goods_description_default,
        'transportation_reason_id' : _get_transportation_reason_default,
        'carrier_id' : _get_carrier_default,
      }
    
def create(self, cr, user, vals, context=None):
        #import pdb
        #pdb.set_trace()
        vals['mezzo_id'] = _get_mezzo_default
        vals['carriage_condition_id'] = _get_carriage_condition_default
        vals['goods_description_id'] = _get_goods_description_default
        vals['transportation_reason_id'] = _get_transportation_reason_default
        vals['carrier_id'] = _get_carrier_default 
        
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        return new_id    
    
stock_picking_out()

