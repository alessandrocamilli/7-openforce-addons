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

class sale_order(orm.Model):
    
    _inherit = "sale.order"
    _columns = {
        'salesman_pricelist': fields.many2one('salesman.pricelist', 'Salesman Pricelist'),
    }
    
    def onchange_user_id(self, cr, uid, ids, user_id, context=None):
        if not user_id:
            return {'value': {'salesman_pricelist': False}}
        
        salesman_ids = self.pool.get('salesman.salesman').search(cr, uid, [('salesman','=', user_id)], context=context)
        if not salesman_ids:
            return {'value': {'salesman_pricelist': False}}
        salesman = self.pool.get('salesman.salesman').browse(cr, uid, salesman_ids[0])
        if not salesman.pricelist:
            return {'value': {'salesman_pricelist': False}}
        val = {
            'salesman_pricelist': salesman.pricelist.id,
        }
        
        #xxx = self.pool.get('sale.order.line').compute_commission_line(cr, uid, ids, context)
        
        # Change on lines
        sale_order_line_obj = self.pool.get('sale.order.line')
        commission_ids = []
        line = {}
        
        partner_id = context.get('partner_id', False)
        section_id = context.get('section_id', False)
        date_order = context.get('date_order', False)
        salesman_pricelist = salesman.pricelist.id
        lines = context.get('order_line', False)
        new_lines = []
        for line_order in lines:
            print "xxx"
            
            
            if line_order[1]:
                line = self.pool.get('sale.order.line').browse(cr, uid, line_order[1])
                vals = {
                       'product_id': line.product_id.id,
                       'product_uom': line.product_uom.id,
                       'product_uom_qty': line.product_uom_qty,
                       'discount': line.discount,
                       'discount2': line.discount2
                       }
                line_order[2] = vals
                
            uom = line_order[2]['product_uom']
            qty_uos=0
            uos= False
            name=''
            lang=False
            update_tax=True
            packaging=False
            fiscal_position=False
            flag=False
            context['user_id'] = user_id
            context['salesman_pricelist'] = salesman_pricelist
            context['section_id'] = section_id
            
            line_id = line_order[1]
            result_line = sale_order_line_obj.product_id_change(cr, uid, [line_id], salesman_pricelist, line_order[2]['product_id'], line_order[2]['product_uom_qty'],
                uom, qty_uos, uos, name, partner_id,
                lang, update_tax, date_order, packaging, fiscal_position, flag, context)
            res_commission = result_line['value']['salesman_commission_ids']
            new_commission = []
            new_commission.append((5, False, False))
            new_commission.append((0, False, res_commission[0]))
            new_lines.append( (1, line_id, {'salesman_commission_ids': new_commission}) )
        
        if new_lines:
            val['order_line'] = new_lines
        
        val['salesman_pricelist'] = salesman.pricelist.id
        #val = {
        #    'salesman_pricelist': salesman.pricelist.id,
        #}
        
        return {'value': val}
    
    def onchange_salesman_pricelist_id(self, cr, uid, ids, context=None):
        #import pdb
        #pdb.set_trace()
        #print "x"
        return {}
    
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        res = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None)
        #import pdb 
        #pdb.set_trace
        
        return res
    
sale_order()

class sale_order_line(orm.Model):
    
    _name = "sale.order.line"
    _inherit = "sale.order.line"
    
    _columns = {
        'salesman_commission_ids': fields.one2many('salesman.commission.sale.order', 'sale_order_line_id', 'Salesmen Commissions', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
    }
    
    def create(self, cr, uid, vals, *args, **kwargs):
        res_id = super(sale_order_line,self).create(cr, uid, vals, *args, **kwargs)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        return super(sale_order_line,self).write(cr, uid, ids, vals, context)

    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        user_id = context.get('user_id', False)
        salesman_pricelist = context.get('salesman_pricelist', False)
        section_id = context.get('section_id', False)
        discount = context.get('discount', False)
        discount2 = context.get('discount2', False)
        
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        
        if product and (salesman_pricelist or section_id or user_id):# the onchange product calls two times. In the second salesman_pricelist,section_id,user_id don't be passed.
            if not uom:
                uom = result.get('product_uom')
            commission_ids = self.get_commission_line(cr, uid, user_id, salesman_pricelist, section_id, product, qty, uom, partner_id, date_order, discount, discount2)
            
            result['value']['salesman_commission_ids'] = commission_ids
            
        return result
    
    def discount1_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = {'value':{}}
        user_id = context.get('user_id', False)
        salesman_pricelist = context.get('salesman_pricelist', False)
        section_id = context.get('section_id', False)
        discount = context.get('discount', False)
        discount2 = context.get('discount2', False)
        '''
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        '''
        if product and (salesman_pricelist or section_id or user_id):# the onchange product calls two times. In the second salesman_pricelist,section_id,user_id don't be passed.
            if not uom:
                uom = result.get('product_uom')
            commission_ids = self.get_commission_line(cr, uid, user_id, salesman_pricelist, section_id, product, qty, uom, partner_id, date_order, discount, discount2)
            
            result['value']['salesman_commission_ids'] = commission_ids
            
        return result
    
    def discount2_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = {'value':{}}
        user_id = context.get('user_id', False)
        salesman_pricelist = context.get('salesman_pricelist', False)
        section_id = context.get('section_id', False)
        discount = context.get('discount', False)
        discount2 = context.get('discount2', False)
        '''
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        '''
        if product and (salesman_pricelist or section_id or user_id):# the onchange product calls two times. In the second salesman_pricelist,section_id,user_id don't be passed.
            if not uom:
                uom = result.get('product_uom')
            commission_ids = self.get_commission_line(cr, uid, user_id, salesman_pricelist, section_id, product, qty, uom, partner_id, date_order, discount, discount2)
            
            result['value']['salesman_commission_ids'] = commission_ids
            
        return result
    
    def get_commission_line(self, cr, uid, user_id, salesman_pricelist, section_id, product, qty, uom, partner_id, date_order, discount, discount2):

        commission_ids = []
        warning_msgs = {}
        if not salesman_pricelist:
            commission_ids = []
            #warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
            #        'Please set one before choosing a product.')
            #warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            # Ciclo x livello previsto dal listino
            commission = self.pool.get('salesman.pricelist').price_get(cr, uid, [salesman_pricelist],
                    product, qty or 1.0, partner_id, user_id, section_id,{
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        'discount': discount,
                        'discount2': discount2
                        })[salesman_pricelist]
            if commission is False:
                warn_msg = _("Cannot find a SALESMAN pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                commission_ids.append(commission)
        return commission_ids
    
    
    def invoice_line_create(self, cr, uid, ids, context=None):
        
        commission_order_obj = self.pool.get('salesman.commission.sale.order')
        create_ids = super(sale_order_line, self).invoice_line_create(cr, uid, ids, context=None)
        for line_order_id in ids:
            for line_invoice_id in create_ids:
                res = commission_order_obj.create_commission_to_invoice(cr, uid, line_order_id, line_invoice_id, context=context)
        # create_ids contiene l'array con gli id delle righe create        
        return create_ids
sale_order_line()