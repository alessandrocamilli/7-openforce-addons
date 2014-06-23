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

from osv import fields, orm

class res_company(orm.Model):
    
    _inherit = "res.company"
    
    _columns = {
        'openforce_header_text': fields.text('Header text'),
        'openforce_footer_text': fields.text('Footer text'),
        'openforce_invoice_header_text': fields.text('Header text'),
        'openforce_invoice_footer_text': fields.text('Footer text'),
        'openforce_sale_header_text': fields.text('Header text'),
        'openforce_sale_footer_text': fields.text('Footer text'),
        'openforce_logo1': fields.binary('Logo 1'),
        'openforce_logo2': fields.binary('Logo 2'),
        'openforce_logo3': fields.binary('Logo 3'),
        'openforce_logo4': fields.binary('Logo 4'),
        'openforce_logo5': fields.binary('Logo 5'),
        'openforce_logo6': fields.binary('Logo 6'),
        }
    