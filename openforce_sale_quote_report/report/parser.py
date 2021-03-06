# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Alessandro Camilli a.camilli@yahoo.it
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
from tools.translate import _

def form_parser( cr, uid, ids, data, context ):

    return {
        'parameters': {	
            #'type': data['form']['type'],
            #'sale_order_ids': data['form']['sale_order_ids'],
            #'sql_where': data['form']['sql_where'],
        },
   }
jasper_reports.report_jasper(
    'report.openforce_sale_quote_report',
    'sale.order',
    parser=form_parser
)
jasper_reports.report_jasper(
    'report.openforce_sale_quote_report2',
    'sale.order',
    parser=form_parser
)