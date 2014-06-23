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

    def _get_discount_invoice(self, cr, uid, move_line):
        '''Return the discount for the move line'''
        discount = 0.0
        if move_line.purchase_line_id.id:
            discount = move_line.purchase_line_id.discount
        elif move_line.sale_line_id.id:
            discount = move_line.sale_line_id.discount
        return discount
    
    def _get_discount2_invoice(self, cr, uid, move_line):
        '''Return the discount for the move line'''
        discount = 0.0
        if move_line.purchase_line_id.id:
            discount = move_line.purchase_line_id.discount2
        elif move_line.sale_line_id.id:
            discount = move_line.sale_line_id.discount2
        return discount
    
    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):
        """ Gets price unit for invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: The price unit for the move line
        """
        price_unit = super(stock_picking, self)._get_price_unit_invoice(cr, uid, move_line, type)
        
        if move_line.purchase_line_id.id:
            price_unit = move_line.purchase_line_id.price_unit
        elif move_line.sale_line_id.id:
            price_unit = move_line.sale_line_id.price_unit
        
        return price_unit
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        result = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,
            invoice_vals, context=None)
        
        result['discount'] = self._get_discount_invoice(cr, uid, move_line)
        result['discount2'] = self._get_discount2_invoice(cr, uid, move_line)
        result['price_unit'] = self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type'], context=None)
        return result
    