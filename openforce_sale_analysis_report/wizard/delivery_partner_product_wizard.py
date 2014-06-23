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
from osv import fields,osv
import time

class wizard_delivery_partner_product(osv.osv_memory):
    _name='wizard.delivery.partner.product'

    _columns = {
        'from_date' : fields.date('From', required=True),
        'to_date' : fields.date('To', required=True),
        'commercial_id' : fields.many2one('res.users', 'Commercial'),
        }
    _defaults = {
        'from_date': lambda * a: time.strftime('%Y-%m-%d'),
        'to_date': lambda * a: time.strftime('%Y-%m-%d'),
        }
    def start_report(self, cr, uid, ids, data, context=None):
        for wiz_obj in self.read(cr,uid,ids):
            if 'form' not in data:
                data['form'] = {}
            data['form']['from_date'] = wiz_obj['from_date']
            data['form']['to_date'] = wiz_obj['to_date']
            data['form']['commercial_id'] = wiz_obj['commercial_id']
            #data['model'] = 'account.invoice'
            #data['ids']=self.pool.get(data['model']).search(cr,uid,[])
            if data['form']['commercial_id']:
                commercial = self.pool.get('res.users').browse(cr, uid, data['form']['commercial_id'][0])
                data['form']['commercial_name'] = commercial.name
            else:
                data['form']['commercial_name'] = ""
            #----------------------
            # where x sql
            #----------------------
            sql_where = ""
            # sql type and expense
            sql_type =" TRIM(t.type) = 'out_invoice' AND a.expense_type is null "
            sql_where  = sql_where + " " + sql_type
            # sql date
            sql_date =" AND DATE('%s') <= DATE(t.date_invoice) AND DATE('%s') >= DATE(t.date_invoice)" % (data['form']['from_date'], data['form']['to_date'] )
            sql_where  = sql_where + " " + sql_date
            # sql commercial selection
            sql_commercial =""
            if wiz_obj['commercial_id']:
                #sql_commercial = " and t.commercial_partner_id = " + str(wiz_obj['commercial_id'][0]) + " "
                sql_commercial = " and t.user_id = %s " % (commercial.id)
            sql_where  = sql_where + " " + sql_commercial
                
            data['form']['sql_where'] = sql_where
            
            report_name = 'delivery_partner_product_report'

            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': report_name,
                    'datas': data,
            }