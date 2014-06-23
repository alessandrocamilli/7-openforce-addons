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
from tools.translate import _

class stock_move(orm.Model):
    
    _inherit = 'stock.move'
    
    # Compute Discounts
    def _get_discounts(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        for move in self.browse(cr, uid, ids):
            res.setdefault(move.id, {
                'discount': 0.0,
                'discount2': 0.0,
            })
            if move.sale_line_id:
                res[move.id]['discount'] = move.sale_line_id.discount
                res[move.id]['discount2'] = move.sale_line_id.discount2
            elif move.purchase_line_id:
                res[move.id]['discount'] = move.purchase_line_id.discount
                res[move.id]['discount2'] = move.purchase_line_id.discount2
        return res
    
    _columns = {
                'discount': fields.function(_get_discounts, string='Discount 1', method=True, multi='_get_discounts', store=True),
                'discount2': fields.function(_get_discounts, string='Discount 2', method=True, multi='_get_discounts', store=True),
                }
    