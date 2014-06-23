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

class account_payment_term(orm.Model):

    _inherit="account.payment.term"
    
    _description = "Account invoice cash expense"
    _columns = {
        'cash_expense_product_id': fields.many2one('product.product', 'Product for expense'),
    }
    
class res_partner(orm.Model):

    _inherit="res.partner"
    
    _columns = {
        'cash_expense_exclude': fields.boolean('Exclude cash expense'),
    }