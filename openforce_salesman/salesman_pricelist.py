# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from osv import fields, orm, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import time

class salesman_pricelist_type(orm.Model):
    _name = "salesman.pricelist.type"
    _description = "Pricelist Type"
    _columns = {
        'name': fields.char('Name',size=64, required=True, translate=True),
        'key': fields.char('Key', size=64, required=True, help="Used in the code to select specific prices based on the context. Keep unchanged."),
    }
salesman_pricelist_type()

class salesman_pricelist(orm.Model):
    
    _name = "salesman.pricelist"
    _description = "Salesman - Pricelist"
    _columns = {
        'name': fields.char('Pricelist Name',size=64, required=True, translate=True),
        'active': fields.boolean('Active', help="If unchecked, it will allow you to hide the pricelist without removing it."),
        'version_id': fields.one2many('salesman.pricelist.version', 'pricelist_id', 'Pricelist Versions'),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'level_child_commission': fields.integer('Level child until to get commission'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        result= []
        if not all(ids):
            return result
        for pl in self.browse(cr, uid, ids, context=context):
            name = pl.name + ' ('+ pl.currency_id.name + ')'
            result.append((pl.id,name))
        return result
    
    def _get_currency(self, cr, uid, ctx):
        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id
    
    _defaults = {
        'active': lambda *a: 1,
        "currency_id": _get_currency
    }
    
    def price_get_multi(self, cr, uid, user_id, section_id, pricelist_ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param pricelist_ids:
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """
        def _create_parent_category_list(id, lst):
            if not id:
                return []
            parent = product_category_tree.get(id)
            if parent:
                lst.append(parent)
                return _create_parent_category_list(parent, lst)
            else:
                return lst
        # _create_parent_category_list

        if context is None:
            context = {}

        date = time.strftime('%Y-%m-%d')
        if 'date' in context:
            date = context['date']

        currency_obj = self.pool.get('res.currency')
        product_obj = self.pool.get('product.product')
        product_category_obj = self.pool.get('product.category')
        product_uom_obj = self.pool.get('product.uom')
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        price_type_obj = self.pool.get('product.price.type')
        discount_commission_line_obj = self.pool.get('salesman.pricelist.discount_commission.line')
        
        # product.pricelist.version:
        if not pricelist_ids:
            pricelist_ids = self.pool.get('salesman.pricelist').search(cr, uid, [], context=context)

        pricelist_version_ids = self.pool.get('salesman.pricelist.version').search(cr, uid, [
                                                        ('pricelist_id', 'in', pricelist_ids),
                                                        '|',
                                                        ('date_start', '=', False),
                                                        ('date_start', '<=', date),
                                                        '|',
                                                        ('date_end', '=', False),
                                                        ('date_end', '>=', date),
                                                    ])
        if len(pricelist_ids) != len(pricelist_version_ids):
            raise osv.except_osv(_('Warning!'), _("At least one pricelist has no active version !\nPlease create or activate one."))

        # product.product:
        product_ids = [i[0] for i in products_by_qty_by_partner]
        #products = dict([(item['id'], item) for item in product_obj.read(cr, uid, product_ids, ['categ_id', 'product_tmpl_id', 'uos_id', 'uom_id'])])
        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_dict = dict([(item.id, item) for item in products])

        # product.category:
        product_category_ids = product_category_obj.search(cr, uid, [])
        product_categories = product_category_obj.read(cr, uid, product_category_ids, ['parent_id'])
        product_category_tree = dict([(item['id'], item['parent_id'][0]) for item in product_categories if item['parent_id']])

        results = {}
        for product_id, qty, partner in products_by_qty_by_partner:
            for pricelist_id in pricelist_ids:
                commission = False
                #price = False

                tmpl_id = products_dict[product_id].product_tmpl_id and products_dict[product_id].product_tmpl_id.id or False

                categ_id = products_dict[product_id].categ_id and products_dict[product_id].categ_id.id or False
                categ_ids = _create_parent_category_list(categ_id, [categ_id])
                if categ_ids:
                    categ_where = '(categ_id IN (' + ','.join(map(str, categ_ids)) + '))'
                else:
                    categ_where = '(categ_id IS NULL)'

                #if partner:
                #    partner_where = 'base <> -2 OR %s IN (SELECT name FROM product_supplierinfo WHERE product_id = %s) '
                #    partner_args = (partner, tmpl_id)
                #else:
                #    partner_where = 'base <> -2 '
                #    partner_args = ()
                partner_args = ()

                cr.execute(
                    'SELECT i.*, i.id AS pricelist_item_id, pl.currency_id, pl.id AS pricelist_id '
                    'FROM salesman_pricelist_item AS i, '
                        'salesman_pricelist_version AS v, salesman_pricelist AS pl '
                    'WHERE (product_tmpl_id IS NULL OR product_tmpl_id = %s) '
                        'AND (product_id IS NULL OR product_id = %s) '
                        'AND (' + categ_where + ' OR (categ_id IS NULL)) '
                        #'AND (' + partner_where + ') '
                        'AND price_version_id = %s '
                        'AND (min_quantity IS NULL OR min_quantity <= %s) '
                        'AND i.price_version_id = v.id AND v.pricelist_id = pl.id '
                    'ORDER BY sequence',
                    (tmpl_id, product_id) + partner_args + (pricelist_version_ids[0], qty))
                res1 = cr.dictfetchall()
                uom_price_already_computed = False
                for res in res1:
                    if res:
                        
                        # other pricelist
                        if res['base'] == -1:
                            if not res['base_pricelist_id']:
                                #price = 0.0
                                commission_percent = False
                            else:
                                price_tmp = self.price_get(cr, uid,
                                        [res['base_pricelist_id']], product_id,
                                        qty, context=context)[res['base_pricelist_id']]
                                ptype_src = self.browse(cr, uid, res['base_pricelist_id']).currency_id.id
                                uom_price_already_computed = True
                                price = currency_obj.compute(cr, uid, ptype_src, res['currency_id'], price_tmp, round=False)
                        # subtotal
                        elif res['base'] == -2:
                            # this section could be improved by moving the queries outside the loop:
                            commission_percent = res['commission_percent']
                            commission_pricelist = res['pricelist_id']
                            commission_pricelist_item = res['pricelist_item_id']
                            # Commission from table dicount-commission
                            if res['discount_commission_id']:
                                comm_disc_ids = discount_commission_line_obj.search(cr, uid, [
                                                        ('discount_id' ,'=', res['discount_commission_id']),
                                                        ('discount' ,'=', context['discount']),
                                                        ('discount2' ,'=', context['discount2']),
                                                        ])
                                if comm_disc_ids:
                                    comm_disc = discount_commission_line_obj.browse(cr, uid, comm_disc_ids[0])
                                    commission_percent = comm_disc.commission_percent
                            
                        else:
                            # In other cases to complete
                            '''
                            price_type = price_type_obj.browse(cr, uid, int(res['base']))
                            uom_price_already_computed = True
                            price = currency_obj.compute(cr, uid,
                                    price_type.currency_id.id, res['currency_id'],
                                    product_obj.price_get(cr, uid, [product_id],
                                    price_type.field, context=context)[product_id], round=False, context=context)
                            '''

                        if commission_percent is not False:
                            commission = {
                                'percent': commission_percent,
                                'salesman_id': user_id,
                                'pricelist_id': commission_pricelist,
                                'pricelist_item_id': commission_pricelist_item,
                                'section_id': section_id
                                }
                            break

                    else:
                        # False means no valid line found ! But we may not raise an
                        # exception here because it breaks the search
                        commission = False
                '''
                if price:
                    results['item_id'] = res['id']
                    if 'uom' in context and not uom_price_already_computed:
                        product = products_dict[product_id]
                        uom = product.uos_id or product.uom_id
                        price = product_uom_obj._compute_price(cr, uid, uom.id, price, context['uom'])
                '''
                if results.get(product_id):
                    results[product_id][pricelist_id] = commission
                else:
                    results[product_id] = {pricelist_id: commission}

        return results

    def price_get(self, cr, uid, ids, prod_id, qty, partner=None, user_id=None, section_id=None, context=None):
        res_multi = self.price_get_multi(cr, uid, user_id, section_id, pricelist_ids=ids, products_by_qty_by_partner=[(prod_id, qty, partner)], context=context)
        res = res_multi[prod_id]
        res.update({'item_id': {ids[-1]: res_multi.get('item_id', ids[-1])}})
        return res
    
salesman_pricelist()

class salesman_pricelist_version(orm.Model):
    _name = "salesman.pricelist.version"
    _description = "Salesman - Pricelist Version"
    _columns = {
        'pricelist_id': fields.many2one('salesman.pricelist', 'Price List',
            required=True, select=True, ondelete='cascade'),
        'name': fields.char('Name', size=64, required=True, translate=True),
        'active': fields.boolean('Active',
            help="When a version is duplicated it is set to non active, so that the " \
            "dates do not overlaps with original version. You should change the dates " \
            "and reactivate the pricelist"),
        'items_id': fields.one2many('salesman.pricelist.item',
            'price_version_id', 'Price List Items', required=True),
        'date_start': fields.date('Start Date', help="First valid date for the version."),
        'date_end': fields.date('End Date', help="Last valid date for the version."),
        'company_id': fields.related('pricelist_id','company_id',type='many2one',
            readonly=True, relation='res.company', string='Company', store=True)
    }
    _defaults = {
        'active': lambda *a: 1,
    }

    # We desactivate duplicated pricelists, so that dates do not overlap
    def copy(self, cr, uid, id, default=None, context=None):
        if not default: default= {}
        default['active'] = False
        return super(product_pricelist_version, self).copy(cr, uid, id, default, context)

    def _check_date(self, cursor, user, ids, context=None):
        for pricelist_version in self.browse(cursor, user, ids, context=context):
            if not pricelist_version.active:
                continue
            where = []
            if pricelist_version.date_start:
                where.append("((date_end>='%s') or (date_end is null))" % (pricelist_version.date_start,))
            if pricelist_version.date_end:
                where.append("((date_start<='%s') or (date_start is null))" % (pricelist_version.date_end,))

            cursor.execute('SELECT id ' \
                    'FROM salesman_pricelist_version ' \
                    'WHERE '+' and '.join(where) + (where and ' and ' or '')+
                        'pricelist_id = %s ' \
                        'AND active ' \
                        'AND id <> %s', (
                            pricelist_version.pricelist_id.id,
                            pricelist_version.id))
            if cursor.fetchall():
                return False
        return True

    _constraints = [
        (_check_date, 'You cannot have 2 pricelist versions that overlap!',
            ['date_start', 'date_end'])
    ]

salesman_pricelist_version()


class salesman_pricelist_item(orm.Model):
    def _price_field_get(self, cr, uid, context=None):
        pt = self.pool.get('salesman.pricelist.type')
        ids = pt.search(cr, uid, [], context=context)
        result = []
        for line in pt.browse(cr, uid, ids, context=context):
            result.append((line.id, line.name))

        result.append((-1, _('Other Pricelist')))
        #result.append((-2, _('Partner section of the product form')))
        result.append((-2, _('Subtotal')))
        return result

    _name = "salesman.pricelist.item"
    _description = "Salesman - Pricelist item"
    _order = "sequence, min_quantity desc"
    _defaults = {
        'base': lambda *a: -2,
        'min_quantity': lambda *a: 0,
        'sequence': lambda *a: 5,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        for obj_list in self.browse(cr, uid, ids, context=context):
            if obj_list.base == -1:
                main_pricelist = obj_list.price_version_id.pricelist_id.id
                other_pricelist = obj_list.base_pricelist_id.id
                if main_pricelist == other_pricelist:
                    return False
        return True

    _columns = {
        'name': fields.char('Rule Name', size=64, help="Explicit rule name for this pricelist line."),
        'price_version_id': fields.many2one('salesman.pricelist.version', 'Price List Version', required=True, select=True, ondelete='cascade'),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', ondelete='cascade', help="Specify a template if this rule only applies to one product template. Keep empty otherwise."),
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', help="Specify a product if this rule only applies to one product. Keep empty otherwise."),
        'categ_id': fields.many2one('product.category', 'Product Category', ondelete='cascade', help="Specify a product category if this rule only applies to products belonging to this category or its children categories. Keep empty otherwise."),

        'min_quantity': fields.integer('Min. Quantity', required=True, help="Specify the minimum quantity that needs to be bought/sold for the rule to apply."),
        'sequence': fields.integer('Sequence', required=True, help="Gives the order in which the pricelist items will be checked. The evaluation gives highest priority to lowest sequence and stops as soon as a matching item is found."),
        'base': fields.selection(_price_field_get, 'Based on', required=True, size=-1, help="Base commission for computation."),
        'base_pricelist_id': fields.many2one('salesman.pricelist', 'Other Pricelist'),

        'price_surcharge': fields.float('Price Surcharge',
            digits_compute= dp.get_precision('Product Price'), help='Specify the fixed amount to add or substract(if negative) to the amount calculated with the discount.'),
        #'price_discount': fields.float('Price Discount', digits=(16,4)),
        'commission_percent': fields.float('Commission Percent', digits=(16,4)),
        'discount_commission_id': fields.many2one('salesman.pricelist.discount_commission', 'Table discount-commission', ondelete='cascade' ),
        
        'company_id': fields.related('price_version_id','company_id',type='many2one',
            readonly=True, relation='res.company', string='Company', store=True)
    }

    _constraints = [
        (_check_recursion, 'Error! You cannot assign the Main Pricelist as Other Pricelist in PriceList Item!', ['base_pricelist_id']),
    ]

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        if not product_id:
            return {}
        prod = self.pool.get('product.product').read(cr, uid, [product_id], ['code','name'])
        if prod[0]['code']:
            return {'value': {'name': prod[0]['code']}}
        return {}
salesman_pricelist_item()

class salesman_pricelist_discount(orm.Model):

    _name = "salesman.pricelist.discount_commission"
    _description = "Salesman - Pricelist - discount-commission table"
    _defaults = {
        'active' : 1   
    }

    _columns = {
        'name': fields.char('Rule Name', size=64, help="Explicit Table name"),
        'active': fields.boolean('Active'),
        'line_ids': fields.one2many('salesman.pricelist.discount_commission.line', 'discount_id', 'Discount lines'),
    }
    
class salesman_pricelist_discount_line(orm.Model):
    def _price_field_get(self, cr, uid, context=None):
        pt = self.pool.get('salesman.pricelist.type')
        ids = pt.search(cr, uid, [], context=context)
        result = []
        for line in pt.browse(cr, uid, ids, context=context):
            result.append((line.id, line.name))

        result.append((-1, _('Other Pricelist')))
        #result.append((-2, _('Partner section of the product form')))
        result.append((-2, _('Subtotal')))
        return result

    _name = "salesman.pricelist.discount_commission.line"
    _description = "Salesman - Pricelist - discount-commission line table"
    _order = "discount"
    _defaults = {
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        for obj_list in self.browse(cr, uid, ids, context=context):
            discount_search = [('discount_id','=', obj_list.discount_id.id), 
                               ('discount','=', obj_list.discount), 
                               ('discount2','=', obj_list.discount2), ]
            discount_res = self.search(cr, uid, discount_search)
            if len(discount_res) > 1:
                return False
        return True

    _columns = {
        'discount_id': fields.many2one('salesman.pricelist.discount_commission', 'Discount tables'),
        'discount': fields.float('Discount 1', digits=(6,2)),
        'discount2': fields.float('Discount 2', digits=(6,2)),
        'commission_percent': fields.float('Commission Percent', digits=(6,2)),
    }

    _constraints = [
        (_check_recursion, 'Error! Discounts already exist : %s - %s', ['discount', 'discount2']),
    ]