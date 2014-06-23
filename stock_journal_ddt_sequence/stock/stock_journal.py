# -*- coding: utf-8 -*-
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
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _
import time

class stock_journal(osv.osv):
    """ Rel between stock journal and ddt sequence """
    
    _inherit = "stock.journal"
    _columns = {
        'ddt_sequence': fields.many2one(
                        'ir.sequence',
                        'DDT sequence',
                        #domain=[('code','=','stock.ddt')]),
                        ),
    }

    _defaults = {
    }

stock_journal()
