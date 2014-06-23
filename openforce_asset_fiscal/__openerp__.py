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
    "name" : "Asset fiscal",
    "version" : "1.0",
    "author" : "Alessandro Camilli",
    "category" : "assets ",
    'description': """
        Asset improved for italian fiscal environment
    """,
    "depends" : ["base", 'account_asset'],
    "init_xml" : [
                  'asset_italian_category/account.asset.italian.group.csv',
                  'asset_italian_category/account.asset.italian.species.csv',
                  'asset_italian_category/account.asset.italian.category.csv'
                  ],
    "demo_xml" : [],
    "update_xml" : [
                    'wizard/wizard_create_asset_move_view.xml',
                    'wizard/wizard_asset_invoice_line_view.xml',
                    #'asset_invoice_line_view.xml',
                    'asset_view.xml', 
                    'reports.xml',
                    'account/account_view.xml', 
                    'wizard/registro_beni_ammortizzabili_view.xml',
                    #'asset_italian_category/asset_italian_data.xml',
                    'asset_italian_category/asset_italian_view.xml'
                    ],
    "installable": True,
    "active": True
}