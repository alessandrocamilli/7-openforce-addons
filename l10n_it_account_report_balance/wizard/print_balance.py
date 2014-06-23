# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from osv import osv, fields

class wizard_it_print_balance(osv.osv_memory):
    _name = 'wizard.it.print.balance'
    _description = 'Account Common Account Report'
    _inherit = "account.common.report"
    _columns = {
        'filter': fields.selection([('filter_date','Date')
                                    ],'Type filter', required=True),
        'display_account': fields.selection([('all','All'), ('movement','With movements'),
                                            ('not_zero','With balance is not equal to 0'),
                                            ],'Display Accounts', required=True),

    }
    _defaults = {
        'display_account': 'movement',
        'filter': 'filter_date',
    }

    def print_balance(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids)[0]
        '''
        move_obj = self.pool.get('res.partner')
        obj_model_data = self.pool.get('ir.model.data')
        move_ids = move_obj.search(cr, uid, [
            #('journal_id', 'in', [j.id for j in wizard.journal_ids]),
            #('name', 'like', wizard.name),
            (wizard.type, '=', 'True'),
            ], order='name')
        if not move_ids:
            self.write(cr, uid,  ids, {'message': _('No partners found in the current selection')})
            model_data_ids = obj_model_data.search(cr, uid, [('model','=','ir.ui.view'), ('name','=','wizard_openforce_test_webkit_partner')])
            resource_id = obj_model_data.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
            return {
                'name': _('No documents'),
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.it.print.balance',
                'views': [(resource_id,'form')],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        
        datas = {'ids': move_ids}
        '''
        datas = {}
        datas['model'] = 'account.move'
        #datas['type'] = wizard['type']
        #datas['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        datas['form'] = self.read(cr, uid, ids)[0]
        '''
        res= {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }
        res['report_name'] = 'l10n_it_account_report_balance'
        '''
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'l10n_it_account_report_balance',
            'datas': datas,
            }
        #return res

wizard_it_print_balance()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
