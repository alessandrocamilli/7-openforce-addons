# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 NaN Projectes de Programari Lliure, S.L. (http://www.NaN-tic.com)
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
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

{
    'name' : "Payment Term Advanced",
    'version' : "1.0",
    'author': 'Agile Business Group & Domsense',
    'website': 'http://www.agilebg.com',
    'category': 'Accounting',
    'description': """\
This module extends payment terms with the following features:

- Uses 4 decimal digits instead of 2 for Value Amount field, so percentages can have higher precision.
- Allow using Division, apart from Percentage, so one can ensure only one cent remains in the last term.
- Allow to specify the number of months, which is more usual instead of days in some countries.
- Allow to specify two months when we expect no payment to be made, postponing to a specific day in the next month.

This module is based on nan_account_payment_term_extension from NaN tic, thanks!""",
    'license': 'AGPL-3',
    'depends' : [
        'account',
    ],
    'init_xml' : [],
    'update_xml' : [
        'account_view.xml',
    ],
    'test': [
        'test/account_payment_term.yml',
    ],
    'active': False,
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
