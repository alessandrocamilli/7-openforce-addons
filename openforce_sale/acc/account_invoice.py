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

class account_invoice(orm.Model):
    
    _inherit = "account.invoice"
    _columns =  {
        'mezzo_id': fields.many2one('stock.picking.mezzo', 'Mezzo'),
        'picking_out_ids': fields.one2many('stock.picking.out', 'invoice_id', 'Pickings out', readonly=True )
    }
    
    def invoice_print(self, cr, uid, ids, context=None):
        #
        # If doesn't exist invoice_type with document:
        # invoice with picking without ddt_number => invoice_delivery
        # invoice without picking => invoice
        result = super(account_invoice, self).invoice_print(cr, uid, ids, context=None)
        for inv in self.browse(cr, uid, ids, context=None):
            document_type = ''
            # Policy - from invoice_type
            if len(inv.picking_out_ids) > 0:
                if inv.picking_out_ids[0].invoice_type_id.document_type:
                    document_type = inv.picking_out_ids[0].invoice_type_id.document_type
                if document_type == '':
                    if inv.picking_out_ids[0].ddt_number:
                        document_type = 'invoice'
                    else:
                        document_type = 'invoice_delivery'
                        
            if document_type == 'invoice_delivery':
                report_name = "openforce_sale_fattura_accompagnatoria_report"
            else:
                report_name = "openforce_sale_fattura_report"
            
        return {'type': 'ir.actions.report.xml', 'report_name': report_name, 'datas': result['datas'], 'nodestroy': True}
    
    
    def action_invoice_sent(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        
        res = super(account_invoice, self).action_invoice_sent(cr, uid, ids, context)
        
        invoice = self.browse(cr, uid, ids[0])
        try:
            #template_id = ir_model_data.get_object_reference(cr, uid, 'account', 'email_template_edi_invoice')[1]
            template_id = ir_model_data.get_object_reference(cr, uid, 'openforce_sale', 'openforce_account_invoice_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'account.invoice',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
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
