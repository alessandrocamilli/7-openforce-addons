# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (alessandrocamilli@openforce.it)
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
from osv import osv, fields, orm
from openerp.tools.translate import _

class sale_order(orm.Model):
    
    _inherit = 'sale.order'
    
    def _compute_administrative_block(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for order in self.browse(cr, uid, ids):
            if order.partner_id:
                credit_limit_residual = order.partner_id.credit_limit_residual - order.amount_total
                if credit_limit_residual < 0:
                    administrative_block = True
                else:
                    administrative_block = False
                res[order.id]['administrative_block'] = administrative_block
                res[order.id]['administrative_block_credit_to_expire'] = order.partner_id.credit_to_expire
                res[order.id]['administrative_block_credit_expired'] = order.partner_id.credit_expired
                res[order.id]['administrative_block_credit_limit_residual'] = credit_limit_residual
                res[order.id]['administrative_block_credit_limit'] = order.partner_id.credit_limit
        
        return res
        
    _columns = {
        'administrative_block': fields.function(_compute_administrative_block, method=True, multi='admin_block', 
            type='boolean', string='Administrative Block', store= True),
        'administrative_unblock': fields.boolean("Administrative Unblock", track_visibility='onchange'),
        'administrative_block_credit_to_expire': fields.function(_compute_administrative_block, method=True, multi='admin_block', 
            type='float', string='Historic Credit to Expired', store= True, track_visibility='onchange'),
        'administrative_block_credit_expired': fields.function(_compute_administrative_block, method=True, multi='admin_block', 
            type='float', string='Historic Credit Expired', store= True, track_visibility='onchange'),
        'administrative_block_credit_limit_residual': fields.function(_compute_administrative_block, method=True, multi='admin_block', 
            type='float', string='Historic Credit Limit Residual', store= True, track_visibility='onchange'),
        'administrative_block_credit_limit': fields.function(_compute_administrative_block, method=True, multi='admin_block', 
            type='float', string='Historic Credit Limit', store= True, track_visibility='onchange'),
    }
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        for ord in self.browse(cr, uid, ids):
            if ord.administrative_block and not ord.administrative_unblock:
                raise orm.except_orm(_('Order with administrative block!'),_("Financial permission required to remove block"))
        
        return super(sale_order,self).action_button_confirm(cr, uid, ids, context)
