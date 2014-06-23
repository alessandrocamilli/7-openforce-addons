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
    'name': 'Openforce - Base',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """Installing base functions

Functionalities:
- 
- 

""",
    'author': 'OpenERP Italian Community',
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends" : ['account','l10n_it_base', 'l10n_it_abicab', 'l10n_it_fiscalcode', 'l10n_it_partially_deductible_vat',
                 'l10n_it_vat_registries', 
                 'account_financial_report_webkit', 'account_financial_report_horizontal',
                 'openforce_sale', 'openforce_stock', 'openforce_account', 
                 'account_payment_term_advanced', 'jasper_reports', 
                 'account_invoice_entry_date',
                 'account_invoice_sequential_dates', 
                 'account_vat_period_end_statement',
                 'account_cancel', 'sale_journal',
                 'account_invoice_reopen', 'purchase_order_reopen', 'stock_picking_reopen',
                 'account_activity_code_ateco', 'account_vat_dichiarazioni_intento' 
                 ],
    "data" : ['company_view.xml'],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

