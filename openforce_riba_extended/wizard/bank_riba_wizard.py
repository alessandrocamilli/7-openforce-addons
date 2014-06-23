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
#import time
from dateutil.relativedelta import relativedelta
import datetime 

class wizard_bank_riba_report(osv.osv_memory):

    _name = "wizard.bank.riba.report"
    _inherit = "account.common.account.report"
    
    _columns = {
        
        #'result_selection': fields.selection([('customer','Receivable Accounts'),
        #                                      ('supplier','Payable Accounts'),
        #                                      ('customer_supplier','Receivable and Payable Accounts')],
        #                                      "Partner's", required=True),
        'partner_ids': fields.many2many('res.partner', string='Filter on partner',
                                         help="Only selected partners will be printed. Leave empty to print all partners."),
        'bank_configuration_ids': fields.many2many('riba.configurazione', string='Filter on riba configuration',
                                         help="Only selected bank configurations will be printed. Leave empty to print all bank configurations."),
        
        'date_maturity_from': fields.date("Maturity - Start Date"),
        'date_maturity_to': fields.date("Maturity - End Date "),
        'date_invoice_from': fields.date("Invoice - Start Date"),
        'date_invoice_to': fields.date("Invoice - End Date "),
        
        'report_type': fields.selection([('partner','Partner'), ('portafoglio','Portafoglio'),],
                                              "Report type", required=True),
    }
    
    _defaults = {
        'date_maturity_from': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
        'date_maturity_to': lambda *a: (datetime.date.today() + relativedelta(months=+6)).strftime('%Y-%m-%d'),
        'report_type': 'portafoglio',
    }
  
    def print_report(self, cr, uid, ids, data, context=None):
        
        move_ids = []
        wizard = self.read(cr, uid, ids)[0]
        
        #import pdb
        #pdb.set_trace()
    
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            #data['form']['type'] = wiz_obj['type']
            data['form']['date_maturity_from'] = wiz_obj['date_maturity_from']
            data['form']['date_maturity_to'] = wiz_obj['date_maturity_to']
            if wiz_obj['date_invoice_from']:
                data['form']['date_invoice_from'] = wiz_obj['date_invoice_from']
                data['form']['date_invoice_to'] = wiz_obj['date_invoice_to']
            else:
                data['form']['date_invoice_from'] = ""
                data['form']['date_invoice_to'] = ""
            data['form']['bank_configuration_ids'] = wiz_obj['bank_configuration_ids']
            data['form']['report_type'] = wiz_obj['report_type']
            #data['model'] = 'account.move.line'
            #data['ids']=self.pool.get(data['model']).search(cr,uid,[])
            sql_select =""
            sql_group_by =""
            sql_order_by =""
            #----------------------
            # Partner month
            #----------------------
            if wizard['report_type'] == 'partner':
                
                # select x sql
                sql_select = " cp.name as company_name, \
                    p.id as partner_id, p.ref as partner_code, p.name as partner_name,\
                    rco.name as riba_config_name, \
                    concat(EXTRACT(YEAR FROM DATE(i.date_invoice)), '-', EXTRACT(MONTH FROM DATE(i.date_invoice)) ) as periodo, \
                    SUM(rdml.amount) as riba_importo "
                # group by x sql
                sql_group_by = " cp.name, p.id, p.ref, p.name, rco.name, periodo "
                # order by x sql  
                sql_order_by = " p.id, riba_config_name, periodo "
            
            #----------------------
            # where x sql
            #----------------------
            sql_where = " a.type = 'receivable' and pt.riba is true "
            # sql Date_maturity selection
            sql_date_maturity = ""
            if wiz_obj['date_maturity_from']:
                sql_date_maturity = " and ml.date_maturity >= DATE('" + wiz_obj['date_maturity_from'] + "') and ml.date_maturity <= DATE('"+ wiz_obj['date_maturity_to'] + "')"
            sql_date_invoice = ""
            if wiz_obj['date_invoice_from']:
                sql_date_invoice = " and i.date_invoice >= DATE('" + wiz_obj['date_invoice_from'] + "') and i.date_invoice <= DATE('"+ wiz_obj['date_invoice_to'] + "')"
                    
            sql_where  =  sql_where + " " + sql_date_maturity + " " + sql_date_invoice
            # sql partner selection
            sql_partner =""
            if len(wiz_obj['partner_ids']) > 0:
                for p_id in wiz_obj['partner_ids']:
                    if sql_partner == "":
                        sql_partner = "" + str(p_id)
                    else:
                        sql_partner = sql_partner + "," + str(p_id)
                sql_partner = " and p.id IN (" + sql_partner + ")"
            sql_where  = sql_where + " " + sql_partner
            # sql type account selection
            '''
            sql_account_type = ""
            if wizard['result_selection'] == 'customer':
                sql_account_type = " and a.type = 'receivable'"
            elif wizard['result_selection'] == 'supplier':
                sql_account_type = " and a.type = 'payable'"
            elif wizard['result_selection'] == 'customer_supplier':
                sql_account_type = " and a.type IN ('payable','receivable') "
            sql_where  = sql_where + " " + sql_account_type
            '''    
            data['form']['sql_where'] = sql_where
            
            #----------------------
            # sql
            #----------------------
            data['form']['sql_select'] = sql_select
            data['form']['sql_group_by'] = sql_group_by
            data['form']['sql_order_by'] = sql_order_by
            
            report_name = 'openforce_bank_riba_report_da_presentare'
            #report_name = 'openforce_bank_riba_report_partner_riepilogo_banche'
            '''
            report_name = 'openforce_bank_riba_report_partner'
            if wiz_obj['report_type'] == 'partner':
                report_name = 'openforce_bank_riba_report_partner'
            if wiz_obj['report_type'] == 'portafoglio':
                report_name = 'openforce_bank_riba_report_portafoglio'
            '''
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': report_name,
                    'datas': data,
            }

wizard_bank_riba_report()
