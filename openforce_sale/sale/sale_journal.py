# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
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

import time
from osv import fields, osv

class sale_journal(osv.osv):
    _inherit = "sale_journal.invoice.type"
    
    def _check_one_default(self, cr, uid, ids, context=None):
        for type in self.browse(cr, uid, ids, context=context):
            type_ids = self.search(cr, uid, [('default','=', True)], context=context)
            if len(type_ids) > 1:
                return False
        return True

    _columns = {
        'document_type': fields.selection([('invoice', 'Invoice'), ('invoice_delivery', 'Invoice Delivery')], 'Document type', required=True),
        'require_DDT': fields.boolean('Require DDT', help="If required is possible to assign DDT number to delivery order"),
        'default': fields.boolean('Default', help="Default for delivery order and invoice"),
    }
    
    _defaults = {
        'require_DDT': False,
        'invoicing_method': 'invoice'
    }
    
    _constraints = [(_check_one_default, 'Error: Only one default permitted', '')]