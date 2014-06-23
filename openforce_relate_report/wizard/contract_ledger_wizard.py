# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
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
import time
from openerp.tools.translate import _
from openerp.osv import fields, orm, osv

class ContractLedgerWizard(orm.TransientModel):
    """Will launch partner ledger report and pass required args"""

    _inherit = "relate.common.report"
    _name = "relate.contract.ledger.webkit"
    _description = "Contract Ledger Report"
    
    _defaults ={
            'detail_by': 'date'
                }

    def check_report(self, cr, uid, ids, context=None):
        
        res = super(ContractLedgerWizard, self).check_report(cr, uid, ids, context)
        form = self.read(cr, uid, ids)[0]
        #if len(form['contract_ids']) == 0 and len(form['partner_ids']) == 0:
        #    raise osv.except_osv(_('Error!'),_("Specify at least one Contract or Partner"))  
        return res
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(ContractLedgerWizard, self).pre_print_report(cr, uid, ids, data, context)
        if context is None:
            context = {}
        
        # will be used to attach the report on the main account
        
        #data['ids'] = [data['form']['chart_account_id']]
        #vals = self.read(cr, uid, ids,
        #                 context=context)[0]
        #                 ['amount_currency', 'partner_ids'],
        vals = self.read(cr, uid, ids,
                         ['partner_ids'],
                         context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        # we update form with display account value
        data = self.pre_print_report(cursor, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'openforce_relate_contract_ledger',
                'datas': data}
