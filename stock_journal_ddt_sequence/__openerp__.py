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
    "name" : "Stock journal ddt sequence",
    "version" : "1.0",
    "author" : "Alessandro Camilli",
    "category" : "Stock Sales",
    'description': """
        It's possible to assign one ddt sequence to stock journal. 
        In the picking, the ddt field will take the new number by the stock journal.
        
    """,
    "depends" : ["base", "l10n_it_sale"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["stock/stock_journal_view.xml", "wizard/assign_ddt_by_journal.xml", "stock/picking_view.xml"],
    "installable": True,
    "active": True
}