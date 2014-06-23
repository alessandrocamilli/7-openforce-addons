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

import time
from osv import fields, orm

class product_product(orm.Model):
    _inherit = "product.product"

    def default_get(self, cr, uid, fields, context=None):
        
        res = super(product_product, self).default_get(cr, uid, fields, context=context)
        
        res.update({'type':  'product'})
        res.update({'procure_method':  'make_to_order'})
        res.update({'supply_method':  'buy'})
        res.update({'sale_delay':  2})
        
        return res
    
    def create(self, cr, uid, vals, *args, **kwargs):
        if 'default_code' in vals and not vals['default_code']:
              vals['default_code'] = self.pool.get('ir.sequence').get(cr, uid, 'product.product.default_code')
        
        res_id = super(product_product,self).create(cr, uid, vals, *args, **kwargs)
        return res_id