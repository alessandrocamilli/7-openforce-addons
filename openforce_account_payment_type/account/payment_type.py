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

from osv import fields, orm

class account_payment_term_type(orm.Model):
    """
    Payment type
    """
    _name = "account.payment.term.type"
    _description = "Payment term type"
    _columns = {
	'name':fields.char('Payment type', size=64, required=True, readonly=False),
	'note': fields.text('Note'),
    }
    
class account_payment_term(orm.Model):
    
    _inherit = "account.payment.term"
    _columns =  {
        'type_id': fields.many2one('account.payment.term.type', 'Type', required =True),
    }
