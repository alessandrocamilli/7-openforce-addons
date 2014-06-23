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

from osv import fields,osv
from tools.translate import _
import time
import psycopg2
from StringIO import StringIO

class wizard_import_account(osv.osv_memory):
    
    _name = "wizard.openforce.utility.import.account"
    
    _description = 'Use this wizard to import account'
    
    _columns={
        'file_txt_to_import': fields.binary('File TXT to import', required=True),
        'code_leaving_number_letter': fields.boolean('Leaving only number-letter within code'),
        'code_length_max_view': fields.integer('Code Max Lenght view', required=True, help="The accounts until this length will be considered views"),
        'code_length_sub_account': fields.integer('Code Sub-Account Lenght', required=True ),
    }
    
    _defaults={
        'code_leaving_number_letter': True,
        'code_length_max_view': 4,
        'code_length_sub_account': 2,
    }
    
    def import_account(self, cr, uid, ids, data, context=None):
        
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            #data['form']['type'] = wiz_obj['type']
            data['form']['file_txt_to_import'] = wiz_obj['file_txt_to_import']
            data['form']['code_leaving_number_letter'] = wiz_obj['code_leaving_number_letter']
            data['form']['code_length_max_view'] = wiz_obj['code_length_max_view']
            data['form']['code_length_sub_account'] = wiz_obj['code_length_sub_account']
        
            self.pool.get('openforce.utility.account').import_from_csv(cr, uid, ids, data, context=None)

        return {'type': 'ir.actions.act_window_close'}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: