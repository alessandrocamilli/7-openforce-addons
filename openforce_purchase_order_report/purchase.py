# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
#    All Rights Reserved
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

import netsvc
import pooler, tools

from osv import fields, osv, orm

class purchase_order(orm.Model):
    
    _inherit = "purchase.order"
    
    def wkf_send_rfq(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        ir_model_data = self.pool.get('ir.model.data')
        
        res = super(purchase_order, self).wkf_send_rfq(cr, uid, ids, context)
        
        p_order = self.browse(cr, uid, ids[0])
        # Request
        if p_order.state in ['draft', 'sent']:
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'openforce_purchase_order_report', 'openforce_purchase_order_req_email_template')[1]
            except ValueError:
                template_id = False
        # Order
        else:
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'openforce_purchase_order_report', 'openforce_purchase_order_email_template')[1]
            except ValueError:
                template_id = False
        
        # wizard composer    
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        
        res.update({
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        })
        
        return res
    