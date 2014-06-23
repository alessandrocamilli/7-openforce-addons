# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Associazione OpenERP Italia
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields,osv
from tools.translate import _
import netsvc

class wizard_test_webkit(osv.osv_memory):

    _name = "wizard.test.webkit.partner"
    _columns = {
        'type': fields.selection([
            ('customer', 'Customer'),
            ('supplier', 'Supplier'),
            ], 'Partner type', required=True),
        'name': fields.char('Name', size=64),
        'message': fields.char('Message', size=64, readonly=True),
    }

    def print_list_partners(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids)[0]
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
                'res_model': 'wizard.test.webkit.partner',
                'views': [(resource_id,'form')],
                'context': context,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        datas = {'ids': move_ids}
        datas['model'] = 'res.partner'
        datas['type'] = wizard['type']
        datas['name'] = wizard['name']
        res= {
            'type': 'ir.actions.report.xml',
            'datas': datas,
        }
        if wizard['type'] == 'customer':
            res['report_name'] = 'report_test_webkit_partner'
        elif wizard['type'] == 'supplier':
            res['report_name'] = 'report_test_webkit_partner'
        return res

wizard_test_webkit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
