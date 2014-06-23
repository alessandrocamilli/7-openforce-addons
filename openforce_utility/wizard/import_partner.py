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


class wizard_import_partner(osv.osv_memory):
    
    _name = "wizard.openforce.utility.import.partner"
    
    _description = 'Use this wizard to import partner'
    
    _columns={
        'file_txt_to_import': fields.binary('File TXT to import', required=True),
        'is_customer': fields.boolean('Is customer'),
        'is_supplier': fields.boolean('Is supplier'),
        'prefisso_partita_IVA': fields.char('Prefisso p.IVA'),
        'field_separator_csv': fields.char('Field separator for csv'),
    }
    
    _defaults={
        'prefisso_partita_IVA': 'IT',
        'field_separator_csv': ';',
    }
    
    def import_partner(self, cr, uid, ids, data, context=None):
        
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            #data['form']['type'] = wiz_obj['type']
            data['form']['file_txt_to_import'] = wiz_obj['file_txt_to_import']
            data['form']['is_customer'] = wiz_obj['is_customer']
            data['form']['is_supplier'] = wiz_obj['is_supplier']
            data['form']['prefisso_partita_IVA'] = wiz_obj['prefisso_partita_IVA']
            data['form']['field_separator_csv'] = wiz_obj['field_separator_csv']
        
            self.pool.get('openforce.utility.partner').import_from_csv(cr, uid, ids, data, context=None)

        return {'type': 'ir.actions.act_window_close'}
    
wizard_import_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: