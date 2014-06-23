# -*- encoding: utf-8 -*-
#################################################################################
#    Autor: Alessandro Camilli (a.camilli@yahoo.it)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#################################################################################
{
    "name" : "Sale margin",
    "version" : "1.0",
    "author" : "Alessandro Camilli",
    "category" : "sales ",
    'description': """
        Report sale with margin
    """,
    "depends" : ["base", 'sale', 'sale_margin', 'openforce_pricelist_discount_line'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['report/sale_report_view.xml', 
                    'security/ir.model.access.csv',
                    'sale_margin_view.xml'],
    "installable": True,
    "active": True
}