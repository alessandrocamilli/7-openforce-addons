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
from osv import fields, osv, orm
from openerp.tools.translate import _

class sale_order(orm.Model):
    _inherit = "sale.order"
    
    _defaults = {
        'contract_required': 1,
    }

    def action_button_confirm(self, cr, uid, ids, context=None):
        
        # Controllo che il cliente abbia sia P.IVA che codice fiscale
        '''
        for order in self.browse(cr, uid, ids):
            if not order.partner_id.vat or not order.partner_id.fiscalcode:
                raise osv.except_osv(_('Attenzione dati Cliente!'),_("Partita IVA e Codice Fiscale devono essere presenti ") )
        '''
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context)