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

class account_invoice(orm.Model):
    
    _inherit = "account.invoice"
    _columns = {
        'salesman_pricelist': fields.many2one('salesman.pricelist', 'Salesman Pricelist'),
    }
    
    def invoice_validate(self, cr, uid, ids, context=None):
        # Generate commission item
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=None)
        commission_obj = self.pool.get('salesman.commission.item')
        for inv in self.browse(cr, uid, ids, context=context):
            for line in inv.invoice_line:
                commission_obj.generate_items_from_commission_invoice(cr, uid, line.salesman_commission_ids, context=None)
        return res
    
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
        
        return {'value': val}
    
    def onchange_salesman_pricelist_id(self, cr, uid, ids, context=None):
        #import pdb
        #pdb.set_trace()
        print "x"
        return {}
    
account_invoice()

class account_invoice_line(orm.Model):
    
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"
    
    _columns = {
        'salesman_commission_ids': fields.one2many('salesman.commission.sale.invoice', 'invoice_line_id', 'Salesmen Commissions'),
    }
    
    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, 
            fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None,
            salesman_pricelist=None, user_id=None, section_id=None):
        
        result = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom_id, qty, name, type, partner_id, 
            fposition_id, price_unit, currency_id, context, company_id)
        
        if product and (salesman_pricelist or section_id or user_id):# the onchange product calls two times. In the second salesman_pricelist,section_id,user_id don't be passed.
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
                            #'uom': uom or result.get('product_uom'),
                            'uom': uom_id,
                            #'date': date_order,
                            })[salesman_pricelist]
                if commission is False:
                    warn_msg = _("Cannot find a SALESMAN pricelist line matching this product and quantity.\n"
                            "You have to change either the product, the quantity or the pricelist.")
    
                    warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
                else:
                    commission_ids.append(commission)
            result['value']['salesman_commission_ids'] = commission_ids
            
        return result
account_invoice_line()