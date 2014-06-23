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

from osv import fields, osv
import time
from lxml import etree
from tools.translate import _
import pdb

class wizard_asset_invoice_line(osv.osv_memory):
    """
    Invoice link asset
    """
    _name = "wizard.asset.invoice.line"
    _inherit = "account.invoice"
    _description = 'Use this wizard to handle link between assets and invoice lines'

    #_columns={
    #    'invoice_lines':fields.many2many('account.move.line', 'account_invoice_line_move_line_rel', 'asset_move_line_id', 'asset_invoice_line_id', 'Invoices')
    #}
   
    def default_get(self, cr, uid, fields, context=None):
        
        res = super(wizard_asset_invoice_line, self).default_get(cr, uid, fields, context=context)
        
        invoice_line = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=',context['active_id'])])
        # Load wizard with active ids
        if context and 'active_ids' in context and context['active_ids']:
            res.update({'invoice_line':  context['active_ids']})
        
        return res
    
wizard_asset_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
