# -*- coding: utf-8 -*-

#################################################################################
#    Author: Alessandro Camilli a.camilli@yahoo.it
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
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class account_asset_italian_group(osv.osv):
    _name = "account.asset.italian.group"
    _description = "Asset Group italian Fiscal "
    _columns = {
        'name': fields.char('Group name', size=128, required=True, select=1),
        'code': fields.char('Group code', size=64),
    }
    _order = "code"
account_asset_italian_group()

class account_asset_italian_species(osv.osv):
    _name = "account.asset.italian.species"
    _description = "Asset Species italian Fiscal "
    _columns = {
        'name': fields.char('Group name', size=128, required=True, select=1),
        'code': fields.char('Group code', size=64),
    }
    _order = "code"
account_asset_italian_species()

class account_asset_italian_category(osv.osv):
    _name = "account.asset.italian.category"
    _description = "Asset category italian Fiscal "
    _columns = {
        'name': fields.char('Type name', size=128, required=True, select=1),
        'percent': fields.float('Percent'),
        'species_id': fields.many2one('account.asset.italian.species', 'Parent Asset species'),
        'group_id': fields.many2one('account.asset.italian.group', 'Parent Asset group'),
    }
account_asset_italian_category()
