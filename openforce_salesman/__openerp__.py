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
{
    'name': 'Openforce - Salesman',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """Openforce - Salesman

Functionalities:
- Salesesman own group
- Pricelist for commissions

""",
    'author': 'Openforce',
    'website': 'http://www.openforce.it',
    'license': 'AGPL-3',
    "depends" : ['account', 'crm', 'sale_stock','openforce_sale'],
    "data" : [
        'security/security.xml',
        #'wizard/report_commission_view.xml',
        'security/ir.model.access.csv',
        'account/account_view.xml',
        'sale/sale_view.xml',
        'salesman_view.xml',
        'salesman_pricelist_view.xml',
        'reports.xml',
        ],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

