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

class riba_unsolved(osv.osv_memory):
    
    def _get_unsolved_bank_account_id(self, cr, uid, context=None):
        unsolved_bank_account_id = self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'unsolved_bank_account_id', context=context)
        bank_account_id = self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'bank_account_id', context=context)
        if unsolved_bank_account_id:
            return unsolved_bank_account_id
        else:
            return bank_account_id
    
    def _get_unsolved_effects_account_id(self, cr, uid, context=None):
        unsolved_effects_account_id = self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'unsolved_bank_account_accreditation_id', context=context)
        effects_account_id = self.pool.get('riba.configurazione').get_default_value_by_distinta_line( cr, uid, 'acceptance_account_id', context=context)
        if unsolved_effects_account_id:
            return unsolved_effects_account_id
        else:
            return effects_account_id
        
    _inherit = 'riba.unsolved'
    _defaults = {
        'bank_account_id': _get_unsolved_bank_account_id,
        'effects_account_id': _get_unsolved_effects_account_id,
        }
    
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
        distinta_line = self.pool.get('riba.distinta.line').browse(cr, uid, active_id, context=context)
        wizard = self.browse(cr,uid,ids)[0]
        if not distinta_line.distinta_id.config.unsolved_reverse_sbf_with_payment:
            if not wizard.unsolved_journal_id or not wizard.effects_account_id or not wizard.riba_bank_account_id or not wizard.overdue_effects_account_id or not wizard.bank_account_id or not wizard.bank_expense_account_id:
                raise osv.except_osv(_('Error'), _('Every account is mandatory'))
        else:
            if not wizard.unsolved_journal_id or not wizard.overdue_effects_account_id or not wizard.bank_account_id or not wizard.bank_expense_account_id:
                raise osv.except_osv(_('Error'), _('Every account is mandatory'))
        
        unsolved_move_lines = [
                (0,0, {
                    'name':  _('Overdue Effects'),
                    'account_id': wizard.overdue_effects_account_id.id,
                    'debit': wizard.overdue_effects_amount,
                    'credit': 0.0,
                    'partner_id': distinta_line.partner_id.id,
                    'date_maturity': distinta_line.due_date,
                    }),
                (0,0, {
                    'name':  _('Bank'),
                    'account_id': wizard.bank_account_id.id,
                    'credit': wizard.bank_amount,
                    'debit': 0.0,
                    }),
                (0,0, {
                    'name':  _('Expenses'),
                    'account_id': wizard.bank_expense_account_id.id,
                    'debit': wizard.expense_amount,
                    'credit': 0.0,
                    }),
                ]
        
        if distinta_line.distinta_id.config.unsolved_reverse_sbf_with_payment:
            unsolved_line = (0,0, {
                    'name':  _('Effects'),
                    'account_id': wizard.effects_account_id.id,
                    'credit': wizard.effects_amount,
                    'debit': 0.0,
                    })
            unsolved_move_lines.append(unsolved_line)
            unsolved_line = (0,0, {
                    'name':  _('Ri.Ba. Bank'),
                    'account_id': wizard.riba_bank_account_id.id,
                    'debit': wizard.riba_bank_amount,
                    'credit': 0.0,
                    }) 
            unsolved_move_lines.append(unsolved_line)
        
        move_vals = {
            'ref': _('Unsolved Ri.Ba. %s - line %s') % (distinta_line.distinta_id.name, distinta_line.sequence),
            'journal_id': wizard.unsolved_journal_id.id,
            'line_id': unsolved_move_lines
            }
        move_id = move_pool.create(cr, uid, move_vals, context=context)
        # reconcile effects
        
        to_be_reconciled = []
        for move_line in move_pool.browse(cr, uid, move_id, context=context).line_id:
            if move_line.account_id.id == wizard.overdue_effects_account_id.id:
                for riba_move_line in distinta_line.move_line_ids:
                    invoice_pool.write(cr, uid, riba_move_line.move_line_id.invoice.id, {
                        'unsolved_move_line_ids': [(4, move_line.id)],
                        }, context=context)
            if distinta_line.distinta_id.config.unsolved_reverse_sbf_with_payment:
                if move_line.account_id.id == wizard.effects_account_id.id and move_line.credit > 0.0 :
                    to_be_reconciled.append(move_line.id)
            # No reconciliation for moves already reconciled
            to_reconcile = False
            if distinta_line.distinta_id.config.unsolved_reverse_sbf_with_payment:
                for acceptance_move_line in distinta_line.acceptance_move_id.line_id:
                    if acceptance_move_line.debit > 0.0 and not acceptance_move_line.reconcile_id:
                        to_be_reconciled.append(acceptance_move_line.id)
                        to_reconcile = True
            if to_reconcile:
                move_line_pool.reconcile_partial(cr, uid, to_be_reconciled, context=context)
        
        distinta_line.write({
            'unsolved_move_id': move_id,
            'state': 'unsolved',
            })
        wf_service.trg_validate(
            uid, 'riba.distinta', distinta_line.distinta_id.id, 'unsolved', cr)
        return {
            'name': _('Unsolved Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_id or False,
        }

riba_unsolved()
