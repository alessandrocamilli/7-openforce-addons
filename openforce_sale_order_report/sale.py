# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
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
#############################################################################

from osv import fields, osv

class sale_order(osv.osv):
    
    _inherit = "sale.order"
    
    def print_quotation(self, cr, uid, ids, context=None):
        
        result = super(sale_order, self).print_quotation(cr, uid, ids, context=None)
        #import pdb
        #pdb.set_trace()
        for order in self.browse(cr, uid, ids, context=None):
            # Quotation
            if order.state is 'draft' or 'sent':
                report_name = "openforce_sale_quote_report"
            # Order
            else:
                report_name = "openforce_sale_order_report"
        
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': result['datas'], 'nodestroy': True}
    
