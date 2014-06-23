# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (alessandrocamilli@openforce.it)
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
{
    'name': 'Openforce Credit and Debit residual',
    'description': """
Compute the credit and debit residual seconds the partner's field credit_limit and debit_limit
 
""",
    'version': '1.0',
    'author': 'Alessandro Camilli',
    'license': 'AGPL-3',
    'category': 'Account',
    'website': 'http://www.openforce.it',
    'depends': ['account',],
    'init_xml': [],
    'demo_xml' : [],
    'data' : [
        'account_view.xml',
        ],
    'active': False,
    'installable': True,
    'application': True,
}
