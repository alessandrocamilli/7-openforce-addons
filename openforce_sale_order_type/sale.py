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

from osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class sale_order(orm.Model):
    
    _inherit = "sale.order"
    _columns = {
        'type_order': fields.many2one('sale.order.type', 'Type'),
    }

    def onchange_type_order(self, cr, uid, ids, type, context=None):
        res = {}
        if not type:
            return res
        acc_fp_obj = self.pool.get('account.fiscal.position')
        sale_order_type_obj = self.pool.get('sale.order.type')
        type_order = sale_order_type_obj.browse(cr, uid, type)
        
        if type_order.lines_default:
            lines_to_add = []
            for line_def in type_order.lines_default:
                taxes = line_def.product_id.taxes_id
                fpos = context.get('fiscal_position', False) or False
                taxes_ids = acc_fp_obj.map_tax(cr, uid, fpos, taxes)
                line_val = {
                        'state': 'draft',
                        'name': line_def.product_id.name,
                        'product_uom_qty': 1,
                        'product_uom': line_def.product_id.uom_id.id,
                        'product_id': line_def.product_id.id,
                        'price_unit': line_def.price or line_def.product_id.list_price,
                        'tax_id': [(6,0,taxes_ids)],
                        'type': 'make_to_stock'
                        }
                lines_to_add.append(( 0, 0, line_val))
        # Renew values
        if len(lines_to_add) > 0:
            val = {'order_line': lines_to_add}
            res = {'value': val}
            
        return res

    
class sale_order_type(orm.Model):
    
    _name = "sale.order.type"
    _description = "Sale order type "
    
    _columns = {
        'name': fields.char('Name'),
        'lines_default': fields.one2many('sale.order.type.lines_default', 'type_id', 'Default Lines'),
    }
    
class sale_order_type_lines(orm.Model):
    
    _name = "sale.order.type.lines_default"
    _description = "Sale order type - Lines default"
    
    _columns = {
        'type_id': fields.many2one('sale.order.type', 'Type', readonly=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product', required=True ),
        'quantity': fields.float('Quantity', required=True),
        'price': fields.float('Price', digits_compute=dp.get_precision('Product Price')),
    }
