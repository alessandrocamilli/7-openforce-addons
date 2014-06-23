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

class salesman_commission_sale_order(orm.Model):
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        commission_item_obj = self.pool.get('salesman.commission.item')
        res ={}
        for comm in self.browse(cr, uid, ids, context=None):
            args = {
                    'pricelist_item_id': comm.pricelist_item_id.id,
                    'subtotal': comm.sale_order_line_id.price_subtotal,
                    }
            commission_amount = commission_item_obj.compute_commission(cr, uid, args, context)
            res[comm.id] = commission_amount
        return res
    
    _name = "salesman.commission.sale.order"
    _description = "Salesman - Commission on sale order"
    _columns = {
        'sale_order_line_id': fields.many2one('sale.order.line', 'Line order', readonly=True, ondelete='cascade'),
        'percent': fields.float('Commission Percent', required=True),
        'amount': fields.function(_amount_line, string='Amount', digits_compute= dp.get_precision('Account')),
        'pricelist_id': fields.many2one('salesman.pricelist', 'Pricelist', readonly=True),
        'pricelist_item_id': fields.many2one('salesman.pricelist.item', 'Pricelist ref', readonly=True),
        'salesman_id': fields.many2one('res.users', 'Salesperson', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'section_id': fields.many2one('crm.case.section', 'Team', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'commission_invoice_ids': fields.many2many('salesman.commission.sale.invoice', 'salesman_commission_order_invoice_rel', 'commission_order', 'commission_invoice', readonly=True),
    }
    
    def create_commission_to_invoice(self, cr, uid, line_order_id=None, line_invoice_id=None, context=None):
        result = {}
        #if not line_order_id or not line_invoice_id:
        if not line_order_id:
            return False
        
        commission_order_ids = self.search(cr, uid, [('sale_order_line_id','=', line_order_id)], context=context)
        commissions = []
        commission_sale_invoice = []
        for commission_order in self.browse(cr, uid, commission_order_ids):
            val = {
                   'invoice_line_id': line_invoice_id,
                   'percent': commission_order.percent,
                   'pricelist_id': commission_order.pricelist_id.id,
                   'pricelist_item_id': commission_order.pricelist_item_id.id,
                   'salesman_id': commission_order.salesman_id.id,
                   'section_id': commission_order.section_id.id,
                   }
            # relationship commission order-commission invoice
            inv_line_id = self.pool.get('salesman.commission.sale.invoice').create(cr, uid, val, context=context)
            commission_sale_invoice.append(inv_line_id)
            rel = {'commission_invoice_ids': [(6, 0, [inv_line_id])] }
            rel_id = self.pool.get('salesman.commission.sale.order').write(cr, uid, [commission_order.id], rel, context=context)
            commissions.append(rel_id)
        result['relations_ids'] = commissions
        result['commission_sale_invoice_ids'] = commission_sale_invoice
        return result
    
salesman_commission_sale_order()

class salesman_commission_sale_invoice(orm.Model):
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        commission_item_obj = self.pool.get('salesman.commission.item')
        res ={}
        for comm in self.browse(cr, uid, ids, context=None):
            args = {
                    'pricelist_item_id': comm.pricelist_item_id.id,
                    'subtotal': comm.invoice_line_id.price_subtotal,
                    }
            commission_amount = commission_item_obj.compute_commission(cr, uid, args, context)
            res[comm.id] = commission_amount
        return res
    
    _name = "salesman.commission.sale.invoice"
    _description = "Salesman - Commission on sale invoice"
    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line', 'Line order', readonly=True),
        'percent': fields.float('Commission Percent', required=True),
        'amount': fields.function(_amount_line, string='Amount', digits_compute= dp.get_precision('Account')),
        'pricelist_id': fields.many2one('salesman.pricelist', 'Pricelist', readonly=True),
        'pricelist_item_id': fields.many2one('salesman.pricelist.item', 'Pricelist ref', readonly=True),
        'salesman_id': fields.many2one('res.users', 'Salesperson', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'section_id': fields.many2one('crm.case.section', 'Team', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'commission_item_ids': fields.many2many('salesman.commission.item', 'salesman_commission_invoice_item_rel', 'commission_invoice', 'commission_item', readonly=True),
    }
salesman_commission_sale_invoice()


class salesman_commission_item(orm.Model):
    
    _name = "salesman.commission.item"
    _description = "Salesman - Commission item"
    _columns = {
        'percent': fields.float('Commission Percent'),
        'amount': fields.float('Commission amount', required=True),
        #'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'invoice_line_id': fields.many2one('account.invoice.line', 'Invoice line', readonly=True),
        'commission_sale_invoice_id': fields.many2one('salesman.commission.sale.invoice', 'Commission Sale invoice', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'period_id': fields.many2one('account.period', 'Competence Period', required=True, domain=[('state','<>','done')], states={'draft':[('readonly',False)]}),
        'salesman_id': fields.many2one('res.users', 'Salesperson', required=True ),
        'section_id': fields.many2one('crm.case.section', 'Team'),
        'paid': fields.boolean('Commission Paid', readonly=True),
        'name': fields.char('Name', size=128 ),
        'invoice_line_qty': fields.related('invoice_line_id', 'quantity', string="Quantity", readonly=True, store=False),
        'invoice_line_price': fields.related('invoice_line_id', 'price_unit', string="Price", readonly=True, store=False),
        'invoice_line_discount1': fields.related('invoice_line_id', 'discount', string="Discount 1", readonly=True, store=False),
        'invoice_line_discount2': fields.related('invoice_line_id', 'discount2', string="Discount 2", readonly=True, store=False),
        'invoice_line_subtotal': fields.related('invoice_line_id', 'price_subtotal', string="Subtotal", readonly=True, store=False),
    }
    
    def generate_items_from_commission_invoice(self, cr, uid, commission_ids_obj, context=None):
        
        commission_invoice_obj = self.pool.get('salesman.commission.sale.invoice')
        res = []
        if not commission_ids_obj:
            return False
        commission_invoice_id = False
        
        #for commission in commission_invoice_obj.browse(cr, uid, commission_ids, context=None):
        for commission in commission_ids_obj:
            commission_invoice_id = commission.id
            val = {
                'commission_sale_invoice_id' : commission.id,   
                'percent' : commission.percent,   
                'amount' : commission.amount,   
                #'invoice_line_id' : commission.invoice_line_id.invoice_id.id,   
                'invoice_line_id' : commission.invoice_line_id.id,   
                'partner_id' : commission.invoice_line_id.invoice_id.partner_id.id,   
                'product_id' : commission.invoice_line_id.product_id.id,   
                'period_id' : commission.invoice_line_id.invoice_id.period_id.id,   
                'salesman_id' : commission.salesman_id.id,   
                'section_id' : commission.section_id.id,
                'name': 'Commission from invoice %s' % (commission.invoice_line_id.invoice_id.number, ) 
                }
            comm_id = self.create(cr, uid, val, context=context)
            res.append(comm_id)
        # update realtion between commission invoice and item generated 
        if commission_invoice_id and len(res) > 0:
            rel = {'commission_item_ids': [(6, 0, res)] }
            rel_id = self.pool.get('salesman.commission.sale.invoice').write(cr, uid, [commission_invoice_id], rel, context=context)
        
        return res
    
    def compute_commission(self, cr, uid, arg, context):
        result = {}
        pricelist_item_obj = self.pool.get('salesman.pricelist.item')
        
        amount_commission = False
        # Base calc
        base = -2
        percent = 0
        if 'pricelist_item_id' in arg:
            pricelist_item = pricelist_item_obj.browse(cr, uid, arg['pricelist_item_id'], context=context)
            if pricelist_item.base:
                base = pricelist_item.base
                percent = pricelist_item.commission_percent
            
        # Compute on subtotal
        if base == -2:
            if 'subtotal' in arg:
                amount_commission = round(arg['subtotal'] * (percent / 100.0), self.pool.get('decimal.precision').precision_get(cr, uid, 'Account'))
        
        return amount_commission
    
salesman_commission_item()

class salesman_salesman(orm.Model):
    
    def _get_partners(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for salesman in self.browse(cr, uid, ids):
            par = []
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('user_id','=', salesman.salesman.id)], context=context)
            for partner in partner_ids: 
                par.append(partner)
            result[salesman.id] = par
        return result
    
    def _check_one_salesman(self, cr, uid, ids, context=None):
        for salesman in self.browse(cr, uid, ids, context=context):
            salesman_ids = self.search(cr, uid, [('salesman','=', salesman.salesman.id)], context=context)
            if len(salesman_ids) > 1:
                return False
        return True
    
    _name = "salesman.salesman"
    _description = "Salesman - Salesman"
    _columns = {
        'salesman': fields.many2one('res.users', 'Salesman', required=True),
        'pricelist': fields.many2one('salesman.pricelist', 'Pricelist' ),
        'partners' : fields.function( _get_partners, type='one2many', obj="res.partner", method=True, string="Salesman's partners" ),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic account'),
    }
    
    _constraints = [(_check_one_salesman, 'Error: Salesman already exists', ['length'])]
    
salesman_salesman()