# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Alessandro Camilli (a.camilli@yahoo.it)
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
    'name': 'Purchase order report',
    'version': '0.1',
    'category': 'Localisation/Italy',
    'description': """Report purchase order, redifine send by mail attachments""",
    "author" : "Alessandro Camilli",
    'website': 'http://www.openforce.it',
    'license': 'AGPL-3',
    "depends" : ['purchase'],
    "init_xml" : [
        ],
    "data" : [
        'purchase_view.xml',
        'purchase_data.xml',
        'reports.xml',
        ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
