# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#    All Rights Reserved
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
import time

class wizard_registro_beni_ammortizzabili_report(osv.osv_memory):

    _name = "wizard.cespiti.report"
    _inherit = "account.common.account.report"
    
    _columns = {
                
        'category_ids': fields.many2many('account.asset.category', string='Filter on category',
                                         help="Only selected category will be printed. Leave empty to print all categories."),
    }
    
    #_defaults = {
    #}
  
    def print_report(self, cr, uid, ids, data, context=None):
        
        move_ids = []
        wizard = self.read(cr, uid, ids)[0]
        
        #import pdb
        #pdb.set_trace()
    
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            #data['form']['type'] = wiz_obj['type']
            data['form']['date_from'] = wiz_obj['date_from']
            data['form']['date_to'] = wiz_obj['date_to']
            data['form']['category_ids'] = wiz_obj['category_ids']
            #data['form']['order'] = wiz_obj['order']
            #data['model'] = 'account.move.line'
            #data['ids']=self.pool.get(data['model']).search(cr,uid,[])
            
            #----------------------
            # where x sql
            #----------------------
            sql_where = ""
            # sql Date selection
            sql_date = ""
            if wiz_obj['filter'] == 'filter_date':
                sql_date = " and aml.date >= DATE('" + wiz_obj['date_from'] + "') and aml.date <= DATE('"+ wiz_obj['date_to'] + "')"
                    
            sql_where  =  sql_where + " " + sql_date 
            # sql category selection
            sql_category =""
            if len(wiz_obj['category_ids']) > 0:
                for p_id in wiz_obj['category_ids']:
                    if sql_category == "":
                        sql_category = "" + str(p_id)
                    else:
                        sql_category = sql_category + "," + str(p_id)
                sql_category = " and p.id IN (" + sql_category + ")"
            sql_where  = sql_where + " " + sql_category
                
            data['form']['sql_where'] = sql_where  
            
            #----------------------
            # order by x sql
            #----------------------
            sql_order_by = "a.company_id, a.category_id, a.id, aml.date "
            data['form']['sql_order_by'] = sql_order_by

            
            #report_name = 'account_asset_registro_beni_ammortizzabili_report'
            report_name = 'registro_beni_ammortizzabili_report_webkit'

            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': report_name,
                    'datas': data,
            }

wizard_registro_beni_ammortizzabili_report()
