# -*- coding: utf-8 -*-
#################################################################################
#    Autor: Alessandro Camilli a.camilli@yahoo.it
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

from osv import fields, orm
import openerp.addons.decimal_precision as dp
from tools.translate import _

class stock_picking(orm.Model):
    
    _inherit = 'stock.picking'
    
    def _prepare_shipping_invoice_line(self, cr, uid, picking, invoice, context=None):
        
        result = {}
        if picking.carriage_condition_id.delivery_cost_on_shipping == True:
            result = super(stock_picking, self)._prepare_shipping_invoice_line(cr, uid, picking, invoice, context=None)
            
            # Test if already exists in sale order one line of cost delivery. In this case take that value
            orders_controlled = []
            for line_move in picking.move_lines:
                if line_move.sale_line_id.order_id.id not in orders_controlled:
                    orders_controlled.append(line_move.sale_line_id.order_id.id)
                    for line_sale in line_move.sale_line_id.order_id.order_line:
                        if result and line_sale.product_id.id == result['product_id']:
                            result.update({'price_unit': line_sale.price_subtotal})
            
        return result
    