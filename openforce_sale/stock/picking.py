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
import decimal_precision as dp
import datetime
from openerp.osv import orm, fields

class stock_picking_mezzo(orm.Model):
    """
    Mezzo
    """
    _name = "stock.picking.mezzo"
    _description = "Spedizione mezzo"
    _columns = {
    'name':fields.char('Spedizione mezzo', size=64, readonly=False),
    'note': fields.text('Note'),
    }
stock_picking_mezzo()


class stock_picking_out(orm.Model):
    
    _inherit = "stock.picking.out"
    
    def action_ddt_sent(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        
        res ={}
        #res = super(stock_picking_out, self).action_ddt_sent(cr, uid, ids, context)
        
        picking = self.browse(cr, uid, ids[0])
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'openforce_sale', 'openforce_ddt_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'stock.picking',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            #'mark_invoice_as_sent': True,
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
    
    def _total_amount(self, cr, uid, ids, name, args, context=None):
        """ Compute the attendances, analytic lines timesheets and differences between them
            for all the days of a timesheet and the current day
        """
        uom_obj = self.pool.get('product.uom')
        res = {}
        for picking in self.browse(cr, uid, ids, context=context or {}):
            res.setdefault(picking.id, {
                    'total_amount': 0.0,
                })
            for line in picking.move_lines:
                # qty conversion
                if line.product_uom.id != line.product_id.uom_id.id :
                    move_qty = uom_obj._compute_qty(cr, uid, line.product_id.uom_id.id, line.product_qty, line.product_uom.id)
                else:
                    move_qty = line.product_qty
                #res[picking.id]['total_amount'] = move_qty * line.price_unit * (1 - (line.discount or 0.0) / 100.0) * (1 - (line.discount2 or 0.0) / 100.0)
                res[picking.id]['total_amount'] += move_qty * line.price_unit# Price is already net
                
        return res
    
    _columns =  {
        'mezzo_id': fields.many2one('stock.picking.mezzo', 'Mezzo'),
        'weight_manual': fields.float('weight', digits_compute= dp.get_precision('Stock Weight')),
        'weight_net_manual': fields.float('weight net', digits_compute= dp.get_precision('Stock Weight')),
        'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', readonly=True),
        'total_amount': fields.function(_total_amount, string='Tot Amount', method=True, multi='_total_amount', store=True),
    }
    


class stock_picking(orm.Model):
    
    _inherit = "stock.picking"
    
    def _total_amount(self, cr, uid, ids, name, args, context=None):
        """ Compute the attendances, analytic lines timesheets and differences between them
            for all the days of a timesheet and the current day
        """
        uom_obj = self.pool.get('product.uom')
        res = {}
        for picking in self.browse(cr, uid, ids, context=context or {}):
            res.setdefault(picking.id, {
                    'total_amount': 0.0,
                })
            for line in picking.move_lines:
                # qty conversion
                if line.product_uom.id != line.product_id.uom_id.id :
                    move_qty = uom_obj._compute_qty(cr, uid, line.product_id.uom_id.id, line.product_qty, line.product_uom.id)
                else:
                    move_qty = line.product_qty
                res[picking.id]['total_amount'] += move_qty * line.price_unit# Price is already net
                
        return res
    
    # Redefinition of the new fields in order to update the model stock.picking in the orm
    # FIXME: this is a temporary workaround because of a framework bug (ref: lp996816).
    # It should be removed as soon as
    # the bug is fixed
    _columns =  {
        'mezzo_id': fields.many2one('stock.picking.mezzo', 'Mezzo'),
        'weight_manual': fields.float('weight', digits_compute= dp.get_precision('Stock Weight')),
        'weight_net_manual': fields.float('weight net', digits_compute= dp.get_precision('Stock Weight')),
        'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', readonly=True),
        'total_amount': fields.function(_total_amount, string='Tot Amount', method=True, multi='_total_amount', store=True),
    }
    
    # 
    # Hooking invoice:
    # - Relation between picking and invoice
    # - DDT number in the field name of invoice (to print this ref)
    #
    def _invoice_hook(self, cr, uid, picking, invoice_id):
        invoice_pool = self.pool.get('account.invoice')
        invoice_line_pool = self.pool.get('account.invoice.line')
        picking_out_pool = self.pool.get('stock.picking.out')
        
        invoice = invoice_pool.browse(cr, uid, invoice_id)
        picking_out = picking_out_pool.browse(cr, uid, picking.id)
        
        picking_out_pool.write(cr, uid, [picking.id], {
                'invoice_id': invoice_id,
                })
        
        # Ref DDT on name
        if 'ddt_number' in picking_out and picking_out.ddt_number:
            new_name = '%s, %s' % (picking.name, picking_out.ddt_number)
            self.write(cr, uid, picking.id, {'name': new_name})
            
            # Update invoice with ddt number and date
            ddt_anno = int(picking_out.ddt_date[:4])
            ddt_mese = int(picking_out.ddt_date[5:7])
            ddt_giorno = int(picking_out.ddt_date[8:10])
            data_ddt = datetime.date(ddt_anno, ddt_mese, ddt_giorno)
            new_name_invoice = invoice.name +' %s %s' % (picking_out.ddt_number, data_ddt.strftime("%d/%m/%Y") )
            invoice_pool.write(cr, uid, invoice_id, {'name': new_name_invoice}) 
            # Update invoice lines with ddt number and date in origin field
            '''
            line_ids = invoice_line_pool.search(cr, uid, [('invoice_id','=',invoice_id)])
            for line_id in line_ids:
                invoice_line = invoice_line_pool.browse(cr, uid, line_id, context=None)
                if invoice_line.origin == False:
                   invoice_line.origin ='' 
                new_origin_invoice_line = invoice_line.origin + ':ddt_' + new_name_invoice
                invoice_line_pool.write(cr, uid, line_id, {'origin': new_origin_invoice_line})''' 
        return
    
    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        invoice_line = self.pool.get('account.invoice.line').browse(cr, uid, invoice_line_id)
        if move_line.picking_id.ddt_number:
            # Update invoice with ddt number and date
            ddt_anno = int(move_line.picking_id.ddt_date[:4])
            ddt_mese = int(move_line.picking_id.ddt_date[5:7])
            ddt_giorno = int(move_line.picking_id.ddt_date[8:10])
            data_ddt = datetime.date(ddt_anno, ddt_mese, ddt_giorno)
            new_name_invoice = '%s %s' % (move_line.picking_id.ddt_number, data_ddt.strftime("%d/%m/%Y") )
            new_origin_invoice_line = invoice_line.origin + ':ddt_' + new_name_invoice
            
            self.pool.get('account.invoice.line').write(cr, uid, [invoice_line_id], {'origin': new_origin_invoice_line})
        
        return
    
    def action_invoice_create(self, cursor, user, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cursor, user, ids, journal_id,
            group, type, context)
        for picking in self.pool.get('stock.picking.out').browse(cursor, user, ids, context=context):
            self.pool.get('account.invoice').write(cursor, user, res[picking.id], {
                'mezzo_id': picking.mezzo_id.id,
                'carriage_condition_id': picking.carriage_condition_id.id,
                'goods_description_id': picking.goods_description_id.id,
                'transportation_reason_id': picking.transportation_reason_id.id,
                })
        return res
    
