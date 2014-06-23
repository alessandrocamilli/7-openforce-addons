# -*- coding: utf-8 -*-

#################################################################################
#    Author: Alessandro Camilli a.camilli@yahoo.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
import time
import netsvc
from tools.translate import _

import decimal_precision as dp

# Overloaded stock_picking to manage carriers :
class riba_distinta_line(orm.Model):
    
    _inherit = 'riba.distinta.line'
    
    _columns = {
        'distinta_config': fields.related('distinta_id', 'config', 'name', type='char', string='Configuration ', store=True, readonly=True),
        'due_date' : fields.date("Due date", readonly=False),
    }
    
    def confirm(self, cr, uid, ids, context=None):
        '''
        The new confirm method handles amount residual
        '''
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        wf_service = netsvc.LocalService("workflow")
        for line in self.browse(cr, uid, ids, context=context):
            journal = line.distinta_id.config.acceptance_journal_id
            total_credit = 0.0
            move_id= move_pool.create(cr, uid, {
                'ref': 'Ri.Ba. %s - line %s' % (line.distinta_id.name, line.sequence),
                'journal_id': journal.id,
                }, context=context)
            to_be_reconciled = []
            for riba_move_line in line.move_line_ids:
                total_credit += riba_move_line.amount
                move_line_id = move_line_pool.create(cr, uid, {
                    'name': riba_move_line.move_line_id.invoice.number or riba_move_line.move_line_id.ref,
                    'account_id': riba_move_line.move_line_id.account_id.id,
                    'credit': riba_move_line.amount,
                    'debit': 0.0,
                    'move_id': move_id,
                    'partner_id': line.partner_id.id, # per corretto saldo cli
                    }, context=context)
                to_be_reconciled.append([move_line_id, riba_move_line.move_line_id.id])
                # with saldo < 0 : error
                #      saldo > 0 : save move_line_id unreconciled 
                #      saldo = 0 : unlink move unriconciled saved 
                saldo = riba_move_line.amount_residual
                move_line_pool.write(cr, uid, [riba_move_line.move_line_id.id], {'riba_amount_residual': saldo})
                if saldo < 0:
                    raise orm.except_orm(_('Error'),_('%s - Aomunt Riba of %s exceeds value residual (%s) ') % (line.partner_id.name, str(riba_move_line.amount), str(saldo + riba_move_line.amount)))
                if saldo > 0:
                    move_line_unreconcile_id = self.pool.get('riba.move.line.unreconcile').create(cr, uid, {
                    'payment_move_id': move_line_id, 
                    'move_line_id': riba_move_line.move_line_id.id,
                    'amount': riba_move_line.amount,
                    }, context=context)
                if saldo == 0 and riba_move_line.amount != riba_move_line.amount_origin:
                    payments_to_reconcile_ids = self.pool.get('riba.move.line.unreconcile').search(cr, uid, [('move_line_id','=', riba_move_line.move_line_id.id)], context=context)
                    self.pool.get('riba.move.line.unreconcile').unlink(cr, uid, payments_to_reconcile_ids)
            move_line_pool.create(cr, uid, {
                'name': 'Ri.Ba. %s - line %s' % (line.distinta_id.name, line.sequence),
                'account_id': line.acceptance_account_id.id,
                'partner_id': line.partner_id.id,
                'date_maturity': line.due_date,
                'credit': 0.0,
                'debit': total_credit,
                'move_id': move_id,
                }, context=context)
            move_pool.post(cr, uid, [move_id], context=context)
            for reconcile_ids in to_be_reconciled:
                move_line_pool.reconcile_partial(cr, uid, reconcile_ids, context=context)
            line.write({
                'acceptance_move_id': move_id,
                'state': 'confirmed',
                })
            wf_service.trg_validate(
                uid, 'riba.distinta', line.distinta_id.id, 'accepted', cr)
        return True

    def onchange_riba_amount(self, cr, uid, ids, amount, context=None):
        '''
        Change amount distinta line (in draft state)
        '''
        for riba_line in self.browse(cr, uid, ids, context=context):
            move_amount = riba_line.move_line_ids[0].move_line_id.debit
            move_amount_residual = riba_line.move_line_ids[0].move_line_id.debit
            # amount in other lines
            distinta_move_line_ids = self.pool.get('riba.distinta.move.line').search(
                cr, uid, [('move_line_id','=', riba_line.move_line_ids[0].move_line_id.id),('riba_line_id','!=', riba_line.id)], context=context)
            if len(distinta_move_line_ids) > 0 :
                for distinta_move_line in self.pool.get('riba.distinta.move.line').browse(cr, uid, distinta_move_line_ids, context=context):
                    move_amount_residual -= distinta_move_line.amount
            # Control amounts
            if ( round(move_amount_residual, 2) - amount) < 0:
                raise orm.except_orm(_('Error'),_('Residual is %s :Amount Riba exceeds value of move (%s) ') % (str(move_amount_residual), str(move_amount)))
            values = {'amount': amount}
            #self.pool.get('riba.distinta.move.line').write(cr, uid, riba_line.id, values)
            self.pool.get('riba.distinta.move.line').write(cr, uid, riba_line.move_line_ids[0].id, values)
        return {}
    
    
class riba_distinta(orm.Model):
    
    _inherit = 'riba.distinta'
    
    def unlink(self, cr, uid, ids, context=None):
        # for riba with partial amout, it rebuild situation of riba_move_unreconcile
        for distinta in self.browse(cr, uid, ids, context=context):
            for riba_line in distinta.line_ids:
                if riba_line.move_line_ids:
                    riba_move_line_id = riba_line.move_line_ids[0].move_line_id.id
                    arg = [('move_line_id','=', riba_move_line_id)]
                    # The unriconcile move are present
                    riba_unreconcile_ids = self.pool.get('riba.move.line.unreconcile').search(cr, uid, arg, context=context)
                    
                    # Re-build unreconcile moves
                    if not riba_unreconcile_ids:
                        # all riba linked to the same invoice
                        riba_move_line_ids = self.pool.get('riba.distinta.move.line').search(cr, uid, arg, context=context)
                        riba_amount = 0
                        for riba_move in self.pool.get('riba.distinta.move.line').browse(cr, uid, riba_move_line_ids):
                            # skip the line that it is deleting
                            if riba_move.riba_line_id.id == riba_line.id:
                                continue
                            move_line_unreconcile_id = self.pool.get('riba.move.line.unreconcile').create(cr, uid, {
                                #'payment_move_id': riba_payment.id, 
                                'move_line_id': riba_move.move_line_id.id,
                                'amount': riba_move.amount,
                                }, context=context)
                            riba_amount += riba_move.amount
                        # Update residual on credit line
                        credit_move = self.pool.get('account.move.line').browse(cr, uid, riba_move_line_id)
                        new_residual = credit_move.debit - riba_amount
                        self.pool.get('account.move.line').write(cr, uid, [credit_move.id], {'riba_amount_residual': new_residual})
        
        res = super(riba_distinta, self).unlink(cr, uid, ids, context=None)
        return res
        
    def riba_cancel(self, cr, uid, ids, context=None):
        '''
        Tolgo riconciliazione su linee di accettazione e poi cancello
        '''
        reconcile_pool = self.pool.get('account.move.reconcile')
        move_pool = self.pool.get('account.move')

        for distinta in self.browse(cr, uid, ids, context=context):
            recs = []
            for line in distinta.line_ids:
                for move_line in line.acceptance_move_id.line_id:
                    if move_line.reconcile_id:
                        recs += [move_line.reconcile_id.id]
                    if move_line.reconcile_partial_id:
                        recs += [move_line.reconcile_partial_id.id]

                    reconcile_pool.unlink(cr, uid, recs)
        
                    if move_line.move_id:
                        move_pool.button_cancel(cr, uid, [move_line.move_id.id])
        
        return super(riba_distinta, self).riba_cancel(cr, uid, ids, context=context)

class riba_distinta_move_line(orm.Model):

    _inherit = 'riba.distinta.move.line'
    
    def _get_riba_amount_residual(self, cr, uid, ids, amount, arg, context):
        res = {}
        amount_residual = 0
        for line in self.browse(cr, uid, ids, context=context):
            amount_residual = line.move_line_id.debit - line.amount
            if len(line.move_line_id.distinta_line_ids) > 0:
                if len(line.move_line_id.riba_move_unriconcile) > 0 :
                    for riba_unreconcile in line.move_line_id.riba_move_unriconcile:
                        amount_residual = round(amount_residual - riba_unreconcile.amount, 2)
                else:
                    amount_residual = line.amount_origin - line.amount
            res[line.id] = {}
            res[line.id]['amount_residual'] = amount_residual
        return res
    
    _columns = {
        'amount_origin' : fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'amount_residual': fields.function(_get_riba_amount_residual, method=True, string="Residuo", multi="line"),
    }

class riba_move_line_unreconcile(orm.Model):
    
    _name = 'riba.move.line.unreconcile'
    _description = 'Riba move line unreconcile'
    _rec_name = 'amount'
    
    _columns = {
        'payment_move_id': fields.many2one('account.move.line', 'Move line to reconcile'),
        'move_line_id': fields.many2one('account.move.line', 'Credit move line'),
        'amount' : fields.float('Amount', digits_compute=dp.get_precision('Account')),
    }
    