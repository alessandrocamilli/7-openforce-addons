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

from osv import fields, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class res_partner(orm.Model):
    
    _inherit = 'res.partner'
    
    _columns = {
        'person_type' : fields.selection([
            ('legal','Legal'),
            ('individual','Individual')], 'Person Type'),
        'person_name': fields.char('Name', size=64),
        'person_surname': fields.char('Surname', size=64),
        'person_date_of_birth': fields.date('Date of birth'),
        'person_city_of_birth': fields.char('City of birth', size=64),
        'person_province_of_birth': fields.many2one('res.province', string='Province'),
        'person_region_of_birth': fields.many2one('res.region', string='Region'),
        'person_country_of_birth': fields.many2one('res.country', string='Country'),
        'person_gender' : fields.selection([
            ('male','Male'),
            ('female','Female')], 'Gender'),
        'person_marital_status' : fields.selection([
            ('single','Single'),
            ('married','Married'),
            ('widower','Widower/Widow'),
            ], 'Marital Status'),
    }
    
    def on_change_person_city(self, cr, uid, ids, city):
        city_obj = self.pool['res.city']
        res = {'value': {}}
        if(city):
            city_id = city_obj.search(
                cr, uid, [('name', '=ilike', city)])
            if city_id:
                city_obj = city_obj.browse(
                    cr, uid, city_id[0])
                res = {'value': {
                    'person_province_of_birth': (
                        city_obj.province_id and city_obj.province_id.id
                        or False
                    ),
                    'person_region_of_birth': city_obj.region and city_obj.region.id or False,
                    #'zip': city_obj.zip,
                    'person_country_of_birth': (
                        city_obj.region and
                        city_obj.region.country_id and
                        city_obj.region.country_id.id or False
                    ),
                    'person_city_of_birth': city.title(),
                }
                }
        return res