# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 Alessandro Camilli
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
import jasper_reports
from osv import osv,fields 
import pooler
import datetime

def form_parser( cr, uid, ids, data, context ):
    return {
        'parameters': {     
            'date_maturity_from': data['form']['date_maturity_from'],
            'date_maturity_to': data['form']['date_maturity_to'],
            'date_invoice_from': data['form']['date_invoice_from'],
            'date_invoice_to': data['form']['date_invoice_to'],
            'bank_configuration_ids': data['form']['bank_configuration_ids'],
            'report_type': data['form']['report_type'],
            'sql_where': data['form']['sql_where'],
            'sql_select': data['form']['sql_select'],
            'sql_group_by': data['form']['sql_group_by'],
            'sql_order_by': data['form']['sql_order_by'],
            #'from_account': data['form']['from_account'],
            #'to_account': data['form']['to_account'],
            #'lingua': data['lang'],
        },
   }

jasper_reports.report_jasper(
    'report.openforce_bank_riba_report_partner',
    'account.move.line',
    parser=form_parser
)
jasper_reports.report_jasper(
    'report.openforce_bank_riba_report_partner_riepilogo_banche',
    'account.move.line',
    parser=form_parser
)
jasper_reports.report_jasper(
    'report.openforce_bank_riba_report_portafoglio',
    'account.move.line',
    parser=form_parser
)
jasper_reports.report_jasper(
    'report.openforce_bank_riba_report_da_presentare',
    'account.move.line',
    parser=form_parser
)
