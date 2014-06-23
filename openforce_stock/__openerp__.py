# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2010 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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
    'name': 'Openforce - Stock',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """ Openforce - Stock version

Functionalities:
- Stock view delivery orders to process

""",
    'author': 'Alessandro Camilli',
    'website': 'a.camilli@yahoo.it',
    'license': 'AGPL-3',
    "depends" : ['web','openforce_sale', 'sale_journal', 'account', 'stock', 'sale', 'l10n_it_sale'],
    "data" : [
        'stock/delivery_to_process_view.xml',
        ],
    "css" : ['static/src/css/stock.css'],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

