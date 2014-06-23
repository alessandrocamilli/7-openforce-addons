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
    'name': 'Openforce - Sale',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """OpenERP Italian Localization -Openforce - Sale version

Functionalities:
- Expense type to print some account in the foot of document
- Print directly fattura accompagnatoria
- Partial picking: on validate shows the complete out picking

""",
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends" : ['account', 'l10n_it_sale', 'delivery', 'stock_journal_ddt_sequence', 
                 'openforce_pricelist_discount_line','sale_journal', 'openforce_sale_date_delivery' ],
    "data" : [
        'reports.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'sale/sale_journal_view.xml',
        'sale/sale_view.xml',
        'stock/picking_view.xml',
        'stock/mezzo_view.xml',
        'stock/mezzo_data.xml',
        'partner/partner_view.xml',
        'acc/account_account_view.xml',
        'acc/account_invoice_view.xml',
        'wizard/assign_ddt.xml',
        'sale_data.xml',
        ],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

