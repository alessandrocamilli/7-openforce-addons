# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
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
import jasper_reports
from osv import osv,fields 
import pooler
import datetime

def delivery_partner_product_report_parser( cr, uid, ids, data, context ):
    return {
        'parameters': {	
            'from_date': data['form']['from_date'],
            'to_date': data['form']['to_date'],
            'commercial_name': data['form']['commercial_name'],
            'sql_where': data['form']['sql_where'],
            #'from_account': data['form']['from_account'],
            #'to_account': data['form']['to_account'],
            #'lingua': data['lang'],
        },
   }

jasper_reports.report_jasper(
    'report.delivery_partner_product_report',
    'account.invoice',
    parser=delivery_partner_product_report_parser
)