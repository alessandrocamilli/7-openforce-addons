# -*- coding: utf-8 -*-
#################################################################################
#    Autor: Alessandro Camilli a.camilli@yahoo.it
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

from osv import fields, orm
import openerp.addons.decimal_precision as dp
from tools.translate import _

class product_supplierinfo(orm.Model):
    _inherit = 'product.supplierinfo'
  
    _columns = {
        'supplier_pricelist_id': fields.related('name','property_product_pricelist_purchase',
            readonly=True, relation='product.pricelist', string='Supplier pricelist', type='many2one' ),
        }
    
    def onchange_supplier(self, cr, uid, ids, supplier_id):
        #import pdb
        #pdb.set_trace()
        partnerinfo_obj = self.pool.get('pricelist.partnerinfo')
        # Update for re-compute discount
        for supp_info in self.browse(cr, uid, ids):
            save_supplier_id = supp_info.name.id
            self.write(cr, uid, [supp_info.id], {'name': supplier_id})
            for pricelist in supp_info.pricelist_ids:
                partnerinfo_obj.write(cr, uid, pricelist.id, {'min_quantity': pricelist.min_quantity})
            #self.write(cr, uid, supp_info.id, {'name': save_supplier_id})
        return {}


class pricelist_partnerinfo(orm.Model):
    _inherit = 'pricelist.partnerinfo'
  
    def _get_discount(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for partnerinfo in self.browse(cr, uid, ids):
            pricelist = partnerinfo.suppinfo_id.name.property_product_pricelist_purchase.id
            product = partnerinfo.suppinfo_id.product_id.id
            partner = partnerinfo.suppinfo_id.name
            qty = 1.0
            if product:
                pricelist_item = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product, qty or 1.0, partner.id)
                pricelist_item_id = pricelist_item['item_id'][pricelist]
                price_item = self.pool.get('product.pricelist.item').browse(cr, uid, pricelist_item_id, context=context)
                if field_name == 'discount2':
                    res[partnerinfo.id] = price_item.discount2_line
                else:
                    res[partnerinfo.id] = price_item.discount_line
        return res
    
    _columns = {
        'discount1': fields.function(_get_discount, string='Discount 1', digits_compute= dp.get_precision('Account'), type='float', store=True),
        'discount2': fields.function(_get_discount, string='Discount 2', digits_compute= dp.get_precision('Account'), type='float', store=True),
        }