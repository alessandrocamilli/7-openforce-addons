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
    'name': 'Openforce - Ri.ba. extended',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """

Functionalities:
- Acceptance account id not only recevaible. It's possible choose any account. 
- View Riba distinta lines 
- Due date and amount distinta line editable
- Amount riba divisible 
- More accounts to specify for unsolved registration
- Payment Riba.
""",
    'author': 'Alessandro Camilli',
    'website': '',
    'license': 'AGPL-3',
    "depends" : ['l10n_it_ricevute_bancarie','l10n_it_abicab'],
    "data" : ['riba_view.xml', 'configurazione_view.xml', 'wizard/bank_riba_wizard_view.xml', 
              'wizard/wizard_payment.xml', 'account/account_view.xml', 'reports.xml',
              "security/ir.model.access.csv"],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

