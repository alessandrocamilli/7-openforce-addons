##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm

class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
                if line.purchase_price:
                    res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0*(100.0-line.discount2)/100.0) -(line.purchase_price*line.product_uos_qty), 2)
                else:
                    res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0*(100.0-line.discount2)/100.0) -(line.product_id.standard_price*line.product_uos_qty), 2)
        return res

    _columns = {
        'margin': fields.function(_product_margin, string='Margin',
              store = True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: