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
{
    'name': 'Openforce Relate Reports',
    'description': """
Relate Reports - Webkit
==========================

 
""",
    'version': '1.0',
    'author': 'Alessandro Camilli',
    'license': 'AGPL-3',
    'category': 'Finance',
    'website': 'http://www.openforce.it',
    #'images': [
    #    'images/ledger.png',],
    'depends': ['account', 'openforce_relate', 'report_webkit'],
    'init_xml': [],
    'demo_xml' : [],
    'update_xml': [
                   'data/relate_webkit_header.xml',
                   'report/report.xml',
                   'wizard/relate_common_report_view.xml',
                   'wizard/contract_ledger_wizard_view.xml',
                   'report_menus.xml',
                   ],
    
    'active': False,
    'installable': True,
    'application': True,
}
