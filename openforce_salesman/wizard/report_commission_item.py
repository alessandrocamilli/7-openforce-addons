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

class report_commission(osv.osv_memory):
    
    _name = 'wizard.salesman.report.commission.item'
    _description = 'Commission Report'
    
    _columns = {
        'period_from': fields.many2one('account.period', 'Period from', required=True),
        'period_to': fields.many2one('account.period', 'Period to', required=True),
        
        'salesman_ids': fields.many2many('salesman.salesman', string='Filter on salesman',
                                         help="Only selected salesmen will be printed. Leave empty to print all salesman."),
        'partner_ids': fields.many2many('res.partner', string='Filter on partner',
                                         help="Only selected partners will be printed. Leave empty to print all partners."),
        'team_ids': fields.many2many('crm.section', string='Filter on teams',
                                         help="Only selected teams will be printed. Leave empty to print all teams."),
        
        'order_by': fields.selection([('salesman_period','Salesman-Period'), ('period_salesman','Period-Salesman'),
                                            ],'Order by', required=True),
        'group_by': fields.selection([('invoice','Invoice'),
                                            ],'Group by', required=True),

    }
    _defaults = {
    }

    def print_report(self, cr, uid, ids, data, context=None):
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
        datas['model'] = 'wizard.salesman.report.commission.item'
        #datas['type'] = wizard['type']
        #datas['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        datas['form'] = self.read(cr, uid, ids)[0]
        '''
        res= {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }
        res['report_name'] = 'salesman_report_commission_item'
        '''
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'salesman_report_commission_item',
            'datas': datas,
            }
        #return res

report_commission()

#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
