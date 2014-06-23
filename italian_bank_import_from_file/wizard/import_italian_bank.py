# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012
#    Associazione OpenERP Italia (<http://www.openerp-italia.org>)
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
#############################################################################

from osv import fields,osv
from tools.translate import _
import time
import psycopg2
from StringIO import StringIO


class wizard_import_italian_bank(osv.osv_memory):
    
    _name = "wizard.import.italian.bank"
    
    _description = 'Use this wizard to import italian bank from ufficial file txt'
    
    _columns={
        'file_txt_to_import': fields.binary('File TXT to import', required=True, help="Se il file è troppo grande, dividerlo facendo attenzione \
                affinchè la prima riga del nuovo file inizi con il previsso 11, ovvero con l'intestazione della nuova banca."),
    }

    
    def import_italian_bank(self, cr, uid, ids, data, context=None):
        
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            #data['form']['type'] = wiz_obj['type']
            data['form']['file_txt_to_import'] = wiz_obj['file_txt_to_import']
        
            self.pool.get('l10n_it_abicab.utility.import').import_from_abicab(cr, uid, ids, data, context=None)

        return {'type': 'ir.actions.act_window_close'}
    
    
wizard_import_italian_bank()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: