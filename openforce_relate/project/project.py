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

from osv import fields, orm
from openerp.tools.translate import _
import re

class account_analytic_account(orm.Model):
    
    _inherit = 'account.analytic.account'
    
    def project_create(self, cr, uid, analytic_account_id, vals, context=None):
        '''
        Create the first task for the new project
        '''
        project_id = super(account_analytic_account, self).project_create(cr, uid, analytic_account_id, vals, context=context)
        if project_id:
            project = self.pool.get('project.project').browse(cr, uid, [project_id])
            # Create task if exists contract and there isn't tasks
            if project[0].analytic_account_id and len(project[0].tasks) == 0 and project[0].analytic_account_id.type=="contract":
                # Task name 
                task_name = ""
                if project[0].analytic_account_id.template_id and project[0].analytic_account_id.partner_id:
                    task_name = project[0].analytic_account_id.template_id.name + " - " + project[0].analytic_account_id.partner_id.name
                if not task_name:
                    task_name = project[0].analytic_account_id.name
                if not task_name:
                    task_name = "/"
                # Task partner
                task_partner = project[0].analytic_account_id.partner_id.id or False
                
                vals = {
                    'name' : task_name,
                    'project_id' : project_id,
                    'partner_id' : task_partner,
                    #'date_start' : project_id, da fare x GANTT
                    #'date_end' : project_id
                    }
                
                self.pool.get('project.task').create(cr, uid, vals, context)
            
        return project_id
    
class project_task(orm.Model):
    
    _inherit = 'project.task'
    
    def name_get(self, cr, user, ids, context=None):
        #import pdb
        #pdb.set_trace()
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name','')
            code = d.get('contract_ref',False)
            if code:
                name = '[%s] %s' % (code,name)
            #if d.get('variants'):
            #    name = name + ' - %s' % (d['variants'],)
            return (d['id'], name)

        task_id = context.get('task_id', False)
        result = []
        
        for task in self.browse(cr, user, ids, context=context):
            '''
            sellers = filter(lambda x: x.name.id == task_id, task_id.seller_ids)
            if sellers:
                for s in sellers:
                    mydict = {
                              'id': product.id,
                              'name': s.product_name or product.name,
                              'default_code': s.product_code or product.default_code,
                              'variants': product.variants
                              }
                    result.append(_name_get(mydict))
            else:'''
            mydict = {
                      'id': task.id,
                      'name': task.name,
                      'contract_ref': task.contract_ref,
                      #'default_code': product.default_code,
                      #'variants': product.variants
                      }
            result.append(_name_get(mydict))
        return result
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('contract_ref','=',name)]+ args, limit=limit, context=context)
            ##if not ids:
            ##    ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(cr, user, args + [('contract_ref',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('contract_ref','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result
    
    _columns = {
            'contract_ref': fields.related('project_id', 'analytic_account_id', 'code', type='char',   string="Contract Ref", readonly=True),
            }
