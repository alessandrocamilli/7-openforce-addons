# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
from tools.translate import _
import netsvc
from datetime import datetime
from time import strptime

class riba_paid(osv.osv_memory):
    
    def _get_payment_journal_id(self, cr, uid, context=None):
        return self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'payment_journal_id', context=context)
    
    def _get_payment_bank_account_id(self, cr, uid, context=None):
        return self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'payment_bank_account_id', context=context)
    
    def _get_payment_effects_bank_account_id(self, cr, uid, context=None):
        return self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'payment_effects_bank_account_id', context=context)    
    
    def _get_effects_amount(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('active_id', False):
            return False
        total = 0
        for line in self.pool.get('riba.distinta.line').browse(cr, uid, context['active_ids'], context=context) :
            total += line.amount
            
        #return self.pool.get('riba.distinta.line').browse(cr, uid, context['active_id'], context=context).amount
        return total
    
    def default_get(self, cr, uid, fields, context=None):
        # Only Ri.ba with same configuration
        configuration_save = 0
        for line in self.pool.get('riba.distinta.line').browse(cr, uid, context['active_ids'], context=context) :
            if configuration_save <> 0 and configuration_save <> line.distinta_id.config.id:
                raise osv.except_osv('Attention!', 'Riba doesn\'t have the same bank !')
            configuration_save = line.distinta_id.config.id
        
        res = super(riba_paid, self).default_get(cr, uid, fields, context=context)
        
        return res

    
    _name = "riba.payment"
    _columns = {
        'payment_journal_id' : fields.many2one('account.journal', "Payment journal", 
            domain=[('type', '=', 'bank')]),
        'payment_bank_account_id' : fields.many2one('account.account', "Effects account"),
        'payment_effects_bank_account_id' : fields.many2one('account.account', "Effects account"),
        'effects_amount': fields.float('Effects amount', readonly=True),
        'date_move': fields.date('Data registrazione', required=True),
        }

    _defaults = {
        'payment_journal_id': _get_payment_journal_id,
        'payment_bank_account_id': _get_payment_bank_account_id,
        'payment_effects_bank_account_id': _get_payment_effects_bank_account_id,
        'effects_amount': _get_effects_amount,
        }
        
    def skip(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            raise osv.except_osv(_('Error'), _('No active ID found'))
        active_ids = context.get('active_ids', False)
        line_pool = self.pool.get('riba.distinta.line')
        line_pool.write(cr, uid, active_ids,
            {'state': 'paid'}, context=context)
        return {'type': 'ir.actions.act_window_close'}
        
    def create_move(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wf_service = netsvc.LocalService("workflow")
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            raise osv.except_osv(_('Error'), _('No active ID found'))
        move_pool = self.pool.get('account.move')
        invoice_pool = self.pool.get('account.invoice')
        move_line_pool = self.pool.get('account.move.line')
        riba_distinta_line_pool = self.pool.get('riba.distinta.line')
        
        wizard = self.browse(cr,uid,ids)[0]
        if not wizard.payment_bank_account_id or not wizard.payment_effects_bank_account_id or not wizard.payment_journal_id:
            raise osv.except_osv(_('Error'), _('Every account is mandatory'))
        # period from date
        period_ids = self.pool.get('account.period').search(cr, uid, [('date_start', '<=', wizard.date_move), ('date_stop', '>=', wizard.date_move)])
        if len(period_ids) > 0:
            period_id = period_ids[0]
        else:
            raise osv.except_osv(_('Error'), _('Date without period'))
        
        move_vals = {
            'ref': _('Maturazione valuta'),
            'journal_id': wizard.payment_journal_id.id,
            'date': wizard.date_move,
            'period_id': period_id,
            }
        move_id = move_pool.create(cr, uid, move_vals, context=context)
        to_be_reconciled= []
        total_amount = 0
        for distinta_line in riba_distinta_line_pool.browse(cr, uid, context['active_ids'], context=context) :
            # Effets line
            due_date = datetime.strptime(distinta_line.due_date, '%Y-%m-%d')
            move_line_id = move_line_pool.create(cr, uid, {
                    'name':  _('Maturazione Ri.Ba. %s ft %s - scad.%s %d') % (distinta_line.partner_id.name[:30], distinta_line.invoice_number, due_date.strftime('%d/%m/%Y') , distinta_line.amount),
                    'account_id': wizard.payment_effects_bank_account_id.id,
                    'credit': distinta_line.amount,
                    'debit': 0.0,
                    'move_id': move_id,
                    'date': wizard.date_move,
                    'period_id': period_id,
                    })
            # Cerco il movimento da riconciliare dell'accettazione
            for acceptance_move_line in distinta_line.acceptance_move_id.line_id:
                if acceptance_move_line.debit > 0 and not acceptance_move_line.reconcile_id:
                    to_be_reconciled.append([acceptance_move_line.id,move_line_id])
            # Riba state : paid. If not already unsolved
            if distinta_line.state != 'unsolved':
                riba_distinta_line_pool.write(cr, uid, distinta_line.id, {'state': 'paid'}, context=context)
            
            total_amount += distinta_line.amount
            
        # Bank line
        bank_move_line_id = move_line_pool.create(cr, uid, {
                    'name':  _('Bank'),
                    'account_id': wizard.payment_bank_account_id.id,
                    'credit': 0.0,
                    'debit': total_amount,
                    'move_id': move_id,
                    'date': wizard.date_move,
                    'period_id': period_id,
                    })
        #move_pool.post(cr, uid, [move_id], context=context)
        # Reconcile bank accredit with effects
        for reconcile_ids in to_be_reconciled:
                move_line_pool.reconcile_partial(cr, uid, reconcile_ids, context=context)
                
        return {
            'name': _('Paid Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id or False,
        }
        
riba_paid()