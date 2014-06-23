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

from osv import fields, osv, orm
from openerp import tools
from openerp.tools.translate import _
import logging 
_logger = logging.getLogger(__name__)
from openerp import netsvc
from datetime import datetime

class relate_task(orm.Model):
    
    _name = "relate.task"
    _description = "Relate - Task"
    _inherit = ['mail.thread']
    
    # Compute hours
    def _hours_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        cr.execute("SELECT l.task_id, COALESCE(SUM(hours),0) FROM relate_task_line l \
                    LEFT JOIN project_task_work pwt ON pwt.relate_task_line_id = l.id \
                    WHERE l.task_id IN %s GROUP BY l.task_id",(tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {'hours' : hours.get(task.id, 0.0)}
        return res
    
    # Compute Kilometers
    def _kilometer_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        cr.execute("SELECT task_id, COALESCE(SUM(kilometers),0) FROM relate_task_line \
                    WHERE task_id IN %s GROUP BY task_id",(tuple(ids),))
        km = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {'kilometers' : km.get(task.id, 0.0)}
        return res
    
    _columns = {
        'state' : fields.selection([
            ('draft','Draft'),
            ('confirm','Waiting Approval'),
            ('done','Approved')], 'Status', select=True, required=True, readonly=True, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed timesheet. \
                \n* The \'Confirmed\' status is used for to confirm the timesheet by user. \
                \n* The \'Done\' status is used when users timesheet is accepted by his/her senior.'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'active': fields.boolean('Active'),
        'number':  fields.char('Number', size=64),
        'date': fields.date('Date', select="1", required=True),
        'ref':  fields.char('Ref', size=64),
        'hours': fields.function(_hours_get, string='Hours Tot', multi='hours', help="Computed using the sum of the task work done.",
            ),
        'kilometers': fields.function(_kilometer_get, string='Kilometers', multi='kilometers', help="Computed using the sum of the task work done.",
            ),
        'vehicle': fields.many2one('fleet.vehicle', 'Vehicle'),
        'line_ids': fields.one2many('relate.task.line', 'task_id', 'Task Activities'),
    }
    _defaults = {
        'active': True,
        'state': 'draft',
    }
    
    def button_confirm(self, cr, uid, ids, context=None):
        for relate_task in self.browse(cr, uid, ids, context=context):
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'relate.task', relate_task.id, 'confirm', cr)
        return True
    
    def action_set_to_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_create(uid, self._name, id, cr)
        return True
    
    def create(self, cr, uid, vals, *args, **kwargs):
        if not 'number' in vals or not vals['number']:
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'relate.task') 
        res_id = super(relate_task,self).create(cr, uid, vals, *args, **kwargs)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(relate_task,self).write(cr, uid, ids, vals, context)
        
        # Align date with analytic
        project_task_work_obj = self.pool['project.task.work']
        if 'date' in vals and vals['date']:
            for task in self.browse(cr, uid, ids):
                for line in task.line_ids:
                    domain = [('relate_task_line_id', '=', line.id)]
                    project_task_work_ids = project_task_work_obj.search(cr, uid, domain)
                    if project_task_work_ids:
                        project_task_work_obj.write(cr, uid, project_task_work_ids, {'date': vals['date']})
        return res

    def unlink(self, cr, uid, ids, *args, **kwargs):
        return super(relate_task,self).unlink(cr, uid, ids,*args, **kwargs)
    

class relate_task_line(orm.Model):
    
    _name = "relate.task.line"
    _description = "Relate - Task lines"
    
    # Compute hours
    def _hours_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        #cr.execute("SELECT task_id, COALESCE(SUM(hours),0) FROM project_task_work WHERE task_id IN %s GROUP BY task_id",(tuple(ids),))
        cr.execute("SELECT relate_task_line_id, COALESCE(SUM(hours),0) FROM project_task_work WHERE relate_task_line_id IN %s GROUP BY relate_task_line_id",(tuple(ids),))
        hours = dict(cr.fetchall())
        for task in self.browse(cr, uid, ids, context=context):
            res[task.id] = {
                            'hours' : hours.get(task.id, 0.0),
                            'hours_work' : hours.get(task.id, 0.0) - task.hours_trip
                            }
        return res
    '''
    def _sync_to_relate_task(self, cr, uid, ids, name, args, context=None):
        import pdb
        pdb.set_trace()
        res = {}.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids):
            val = {
                    'user' : line.task_id.user_id.id, 
                    'date' : line.task_id.date, 
                    'number' : line.task_id.number, 
                    'vehicle' : line.task_id.vehicle.id 
                    }
            res[line.id] = val
            #self.write(cr, uid, [line.id], val)
            
        return res
    
    def _onchange_data_from_task(self, cr, uid, ids, context=None):
        res = []
        for task in self.pool.get('relate.task').browse(cr, uid, ids):
            for line in task.line_ids:
                res.append(line.id) # line ids
        return res'''

    _columns = {
        'task_id': fields.many2one('relate.task', 'Task Ref', required=True, ondelete='cascade'),
        'project_task_id': fields.many2one('project.task', 'Project Task Ref', required=True),
        'hours': fields.function(_hours_get, string='Hours Tot', multi='hours', help="Computed using the sum of the task work done.",
            ),
        'hours_work': fields.function(_hours_get, string='Hours Work', multi='hours', help="Computed using the sum of the task work done.",
            ),
        'hours_trip': fields.float('Hours trip'),
        'kilometers': fields.float('kilometers'),
        'partner_id': fields.related('project_task_id', 'partner_id', type='many2one', relation='res.partner',  string="Partner", readonly=True, store=False),
        'project_id': fields.related('project_task_id', 'project_id', type='many2one', relation='project.project',  string="Project", readonly=True, store=False),
        'project_task_work_ids': fields.one2many('project.task.work', 'relate_task_line_id', 'Work Activities'),
        'expense_ids': fields.one2many('account.analytic.line', 'relate_task_line_id', 'Expenses',
                                       domain=[('journal_id.relate_expense', '=', True)]),
        'material_ids': fields.one2many('account.analytic.line', 'relate_task_line_id', 'Materials',
                                       domain=[('journal_id.relate_material', '=', True)]),
        'vehicle_ids': fields.one2many('account.analytic.line', 'relate_task_line_id', 'Vehicles',
                                       domain=[('journal_id.relate_vehicle', '=', True)]),
        
    }
    
    def on_change_project_task_id(self, cr, uid, ids, project_task_id, user_id, date, context=None):
        res ={}
        if project_task_id:
            project_task = self.pool.get('project.task').browse(cr, uid, project_task_id)
            #if project_task and 'value' in res:
            if project_task:
                val = {
                    'partner_id': project_task.partner_id.id or False,
                    'project_id': project_task.project_id.id or False,
                }
                res = {'value': val}
        return res
    
    def on_change_kilometers(self, cr, uid, ids, kilometers, project_task_id, user_id, date, vehicle_id, vehicle_ids, context=None):
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        project_task = self.pool.get('project.task').browse(cr, uid, project_task_id)
        
        if not vehicle_id:
                raise osv.except_osv(_('Error!'),_("Nessun Veicolo specificato"))
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id)
        if not vehicle.relate_cost_per_kilometer:
                raise osv.except_osv(_('Error!'),_("Specificare il costo per km del Veicolo - Vedi anagrafica flotte"))
        if not vehicle.relate_product_id:
                raise osv.except_osv(_('Error!'),_("Specificare un prodotto per il consumo del Veicolo - Vedi anagrafica flotte"))
        
        analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('relate_vehicle','=', True)])
        if not analytic_journal_ids:
            raise osv.except_osv(_('Error!'),_("Nessun giornale analitico di tipo Rapportino-Veicolo"))
        analytic_journal = analytic_journal_obj.browse(cr, uid, analytic_journal_ids[0])
        
        val = {}
        
        if kilometers > 0 :
            default_account = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
            amount = round( -1.00 * kilometers * vehicle.relate_cost_per_kilometer, 2)
            relate_task_line_id = False
            if ids :
                relate_task_line_id = ids[0]
            vals = {
                   'relate_task_line_id' : relate_task_line_id,
                   'user_id' : user_id,
                   'date' : date,
                   'product_id': vehicle.relate_product_id.id,
                   'unit_amount': kilometers,
                   #'hours': 0,
                   'amount': amount,
                   'name': vehicle.relate_product_id.name + ": " + vehicle.name,
                   'journal_id' : analytic_journal.id,
                   'account_id': project_task.project_id.analytic_account_id.id,
                   'general_account_id': vehicle.relate_product_id.property_account_expense or default_account.id or False,
                   }
        # Update/Remove
        line_updated = False
        i = 0
        lines_obj = self.pool.get('account.analytic.line')
        for trip in vehicle_ids:
            analytic_line = False
            if trip[1] :
                analytic_line = lines_obj.browse(cr, uid, trip[1])
                line_product_id = analytic_line.product_id.id
            # Skip products not trip
            is_trip = False
            if  analytic_line and line_product_id == vehicle.relate_product_id.id:
                is_trip = True
            elif trip[2] and 'product_id' in trip[2] and trip[2]['product_id'] == vehicle.relate_product_id.id:
                is_trip = True
                
            if is_trip:
                # Variation existing lines
                if not trip[2] and trip[1]:
                    if kilometers > 0:
                        trip[0] = 1 # update
                        trip[2] = vals
                        line_updated = True
                    else:
                        trip[0] = 2 # delete
                        trip[2] = False
                        line_updated = True
                # New lines
                if trip[2] and 'product_id' in trip[2] and trip[2]['product_id'] == vehicle.relate_product_id.id:
                    if kilometers > 0:
                        trip[2] = vals
                        line_updated = True
                    else:
                        del vehicle_ids[i]
            i+=1            
                
        vehicle_vals = vehicle_ids
        if kilometers > 0 and not line_updated:
            vehicle_vals.append(( 0, 0, vals))
        # Renew values
        val = {'vehicle_ids': vehicle_vals}
        
        res = {'value': val}
        
        return res
        
    def on_change_hours_trip(self, cr, uid, ids, hours_trip, project_task_id, user_id, date, expense_ids, project_task_work_ids, material_ids, context=None):
        '''
        Add line expense from trip hours
        '''
        analytic_line_obj = self.pool.get('account.analytic.line')
        analytic_account_obj = self.pool.get('account.analytic.account')
        project_task = self.pool.get('project.task').browse(cr, uid, project_task_id)
        contract_id = project_task.project_id.analytic_account_id.id
        res ={}
        val = {}
        trip_vals=[]
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', user_id)])
        if employee_ids:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
            if not employee.relate_trip_product_id:
                raise osv.except_osv(_('Error!'),_("Nessun prodotto-Viaggio per il dipendente: configurare correttamente"))
            # to invoice
            invoice_role = analytic_account_obj.get_default_to_invoice(cr, uid, 
                               contract_id, 
                               employee.journal_id.id, 
                               employee.relate_trip_product_id.id, 
                               context)
            line_to_invoice = invoice_role.get('line_to_invoice', False)
            product_to_invoice = invoice_role.get('product_to_invoice', False)
            if hours_trip > 0 :
                default_account = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
                amount = round( 1.00 * hours_trip * employee.relate_trip_product_id.standard_price, 2)
                relate_task_line_id = False
                if ids :
                    relate_task_line_id = ids[0]
                vals = {
                       'relate_task_line_id' : relate_task_line_id,
                       'user_id' : user_id,
                       'date' : date,
                       'product_id': employee.relate_trip_product_id.id,
                       'unit_amount': hours_trip,
                       'hours': hours_trip,
                       'amount': amount,
                       'name': employee.relate_trip_product_id.name,
                       'journal_id' : employee.relate_trip_journal_id.id,
                       'account_id': project_task.project_id.analytic_account_id.id,
                       'general_account_id': employee.relate_trip_product_id.property_account_expense or default_account.id or False,
                       'line_to_invoice': line_to_invoice or False,
                       'product_to_invoice': product_to_invoice or employee.relate_trip_product_id.id or False,
                       }
            
            if employee.relate_trip_product_id and employee.relate_trip_journal_id:
                # Table competence form journal
                if employee.relate_trip_journal_id.relate_expense:
                    lines_trip = expense_ids
                    lines_obj = self.pool.get('account.analytic.line')
                    lines_type = 'expense'
                elif employee.relate_trip_journal_id.relate_material:
                    lines_trip = material_ids
                    lines_obj = self.pool.get('account.analytic.line')
                    lines_type = 'material'
                else:
                    lines_trip = project_task_work_ids
                    lines_obj = self.pool.get('project.task.work')
                    lines_type = 'project_task_work'
                # Update/Remove
                line_updated = False
                i = 0
                for trip in lines_trip:
                    analytic_line = False
                    if trip[1] :
                        analytic_line = lines_obj.browse(cr, uid, trip[1])
                        if analytic_line._name == 'project.task.work':
                            line_product_id = analytic_line.hr_analytic_timesheet_id.product_id.id
                        else:
                            line_product_id = analytic_line.product_id.id
                    # Skip products not trip
                    is_trip = False
                    if  analytic_line and line_product_id == employee.relate_trip_product_id.id:
                        is_trip = True
                    elif trip[2] and 'product_id' in trip[2] and trip[2]['product_id'] == employee.relate_trip_product_id.id:
                        is_trip = True
                        
                    if is_trip:
                        # Variation existing lines
                        if not trip[2] and trip[1]:
                            if hours_trip > 0:
                                #trip[2]['hours'] = hours_trip
                                trip[0] = 1 # update
                                trip[2] = vals
                                line_updated = True
                            else:
                                trip[0] = 2 # delete
                                trip[2] = False
                                line_updated = True
                            print "xxx"
                       
                        # New lines
                        if trip[2] and 'product_id' in trip[2] and trip[2]['product_id'] == employee.relate_trip_product_id.id:
                            if hours_trip > 0:
                                #trip[2]['hours'] = hours_trip
                                trip[2] = vals
                                line_updated = True
                            else:
                                del lines_trip[i]
                    i+=1
                trip_vals = lines_trip
                if hours_trip > 0 and not line_updated:
                    trip_vals.append(( 0, 0, vals))
            # Renew values
            if lines_type == 'material':
                val = {'material_ids': trip_vals}
            elif lines_type == 'expense_ids':
                val = {'material_ids': trip_vals}
            else:
                val = {'project_task_work_ids': trip_vals}
        
        res = {'value': val}
        return res
    
    def create(self, cr, uid, vals, *args, **kwargs):
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        product_obj = self.pool.get('product.product')
        project_task = self.pool.get('project.task').browse(cr, uid, vals['project_task_id'])
        relate_task = self.pool.get('relate.task').browse(cr, uid, vals['task_id'])
        #default_account = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=None)
        default_account = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=None)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', relate_task.user_id.id)])
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
        
        # Add project_task_id to project's task
        if 'project_task_work_ids' in vals:
            for task in vals['project_task_work_ids']:
                if not task[2]:
                    continue
                task[2]['task_id'] = project_task.id
                task[2]['user_id'] = relate_task.user_id.id
                task[2]['date'] = relate_task.date
                task[2]['relate_is_trip'] = False
                if 'product_id' in task[2] and task[2]['product_id'] == employee.relate_trip_product_id.id:
                    task[2]['relate_is_trip'] = True
                #task[2]['relate_is_trip'] = relate_task.date
        # Expense : complete data
        if 'expense_ids' in vals:
            analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('relate_expense','=', True)])
            if not analytic_journal_ids:
                raise osv.except_osv(_('Error!'),_("Nessun giornale analitico di tipo Rapportino-Spesa"))
            for task in vals['expense_ids']:
                if not task[2]:
                    continue
                if task[2]['product_id']:
                    product = product_obj.browse(cr, uid, task[2]['product_id'])
                task[2]['task_id'] = project_task.id
                task[2]['user_id'] = relate_task.user_id.id
                task[2]['date'] = relate_task.date
                task[2]['journal_id'] = analytic_journal_ids[0]
                task[2]['account_id'] = project_task.project_id.analytic_account_id.id
                task[2]['general_account_id'] = product.property_account_expense.id or default_account.id or False
                if task[2]['amount'] > 0: # expense always negative
                   task[2]['amount'] = round(task[2]['amount'] * -1.00, 2) 
        # Material : complete data
        if 'material_ids' in vals:
            analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('relate_material','=', True)])
            if not analytic_journal_ids:
                raise osv.except_osv(_('Error!'),_("Nessun giornale analitico di tipo Rapportino-Materiale"))
            for task in vals['material_ids']:
                if not task[2]:
                    continue
                if task[2]['product_id']:
                    product = product_obj.browse(cr, uid, task[2]['product_id'])
                task[2]['task_id'] = project_task.id
                task[2]['user_id'] = relate_task.user_id.id
                task[2]['date'] = relate_task.date
                task[2]['journal_id'] = analytic_journal_ids[0]
                task[2]['account_id'] = project_task.project_id.analytic_account_id.id
                task[2]['general_account_id'] = product.property_account_expense.id or default_account.id or False
                if task[2]['amount'] > 0: # expense always negative
                   task[2]['amount'] = round(task[2]['amount'] * -1.00, 2)     
            
        res_id = super(relate_task_line,self).create(cr, uid, vals, *args, **kwargs)
        
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        product_obj = self.pool.get('product.product')
        default_account = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
        
        for line in self.browse(cr, uid, ids, context=context):
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', line.task_id.user_id.id)])
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
            # Add project_task_id to project's task
            if 'project_task_work_ids' in vals:
                for task in vals['project_task_work_ids']:
                    if not task[2]: # command upgrade one2many
                        continue
                    task[2]['task_id'] = line.project_task_id.id
                    task[2]['user_id'] = line.task_id.user_id.id
                    task[2]['date'] = line.task_id.date
                    task[2]['relate_is_trip'] = False
                    if 'product_id' in task[2] and task[2]['product_id'] == employee.relate_trip_product_id.id:
                        task[2]['relate_is_trip'] = True
            # Expense : complete data --> receive only field with variations
            if 'expense_ids' in vals:
                analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('relate_expense','=', True)])
                if not analytic_journal_ids:
                    raise osv.except_osv(_('Error!'),_("Nessun giornale analitico di tipo Rapportino-Spesa"))
                for task in vals['expense_ids']:
                    if not task[2]:
                        continue
                    if 'amount' in task[2] and task[2]['amount'] > 0: # expense always negative
                        task[2]['amount'] = round(task[2]['amount'] * -1.00, 2)  
                    product_acc_expense = False
                    if 'product' in task[2] and task[2]['product_id']:
                        product = product_obj.browse(cr, uid, task[2]['product_id'])
                        product_acc_expense = product.property_account_expense.id
                    task[2]['task_id'] = line.project_task_id.id
                    task[2]['user_id'] = line.task_id.user_id.id
                    task[2]['date'] = line.task_id.date
                    task[2]['journal_id'] = analytic_journal_ids[0]
                    task[2]['account_id'] = line.project_task_id.project_id.analytic_account_id.id
                    task[2]['general_account_id'] = product_acc_expense or default_account.id or False
            # Material : complete data --> receive only field with variations
            if 'material_ids' in vals:
                analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('relate_material','=', True)])
                if not analytic_journal_ids:
                    raise osv.except_osv(_('Error!'),_("Nessun giornale analitico di tipo Rapportino-Materiale"))
                for task in vals['material_ids']:
                    if not task[2]:
                        continue
                    if 'amount' in task[2] and task[2]['amount'] > 0: # expense always negative
                        task[2]['amount'] = round(task[2]['amount'] * -1.00, 2)
                    #if not 'product_id' in task[2]:
                    #    >>>>self.browse(cr, uid, )
                    product_acc_expense = False
                    if 'product' in task[2] and task[2]['product_id']:
                        product = product_obj.browse(cr, uid, task[2]['product_id'])
                        product_acc_expense = product.property_account_expense.id
                    task[2]['task_id'] = line.project_task_id.id
                    task[2]['user_id'] = line.task_id.user_id.id
                    task[2]['date'] = line.task_id.date
                    task[2]['journal_id'] = analytic_journal_ids[0]
                    task[2]['account_id'] = line.project_task_id.project_id.analytic_account_id.id
                    task[2]['general_account_id'] = product_acc_expense or default_account.id or False
                    
        res_id = super(relate_task_line,self).write(cr, uid, ids, vals, context)
        return res_id

    def unlink(self, cr, uid, ids, *args, **kwargs):
        return super(relate_task_line,self).unlink(cr, uid, ids,*args, **kwargs)
    
class relate_contract_payment_term(orm.Model):
    
    _name = "relate.contract.payment.term"
    _description = "Relate - Contract Payment term"
    
    def mail_alert(self, cr, uid):
        today = datetime.today()
        line_ids = self.search(cr, uid, [('state', '=', '2binvoiced'),'|',('due_date','<=', today.strftime('%Y-%m-%d')), ('due_date','=', False) ])
        self.send_alert_mail(cr, uid, line_ids)
    
    def send_alert_mail(self, cr, uid, ids, context=None):
        
        mail_obj = self.pool.get('mail.mail')
        mail_message_obj = self.pool.get('mail.message')
        email_template_obj = self.pool.get('email.template')
        email_compose_message_obj = self.pool.get('mail.compose.message')
        server_mail_obj = self.pool.get('ir.mail_server')
        
        # email template
        email_template = False
        email_template_ids = email_template_obj.search(cr, uid, [('model', '=', 'relate.contract.payment.term')])
        if email_template_ids:
            email_template = email_template_obj.browse(cr, uid, email_template_ids[0])
        
        mail_ids= []
        
        for line in self.browse(cr, uid, ids):
            
            contract = line.contract_id
            
            # user's mail server
            if contract.manager_id.email:
                serv_ids = server_mail_obj.search(cr, uid, [('smtp_user', '=', contract.manager_id.email)], order='sequence', limit=1)
                if serv_ids:
                    user_server_mail = server_mail_obj.browse(cr, uid, serv_ids[0])
            
            for follower in contract.message_follower_ids:
                
                if not follower.email:
                    continue
                
                mail_subject = email_compose_message_obj.render_template(cr,uid,_(email_template.subject),'relate.contract.payment.term',line.id)
                mail_body = email_compose_message_obj.render_template(cr,uid,_(email_template.body_html),'relate.contract.payment.term',line.id)
                mail_to = email_compose_message_obj.render_template(cr,uid,_(email_template.email_to),'relate.contract.payment.term',line.id)
                reply_to = email_compose_message_obj.render_template(cr,uid,_(email_template.reply_to),'relate.contract.payment.term',line.id)
                if contract.manager_id.email:
                    mail_from = contract.manager_id.email
                else:
                    mail_from = email_compose_message_obj.render_template(cr,uid,_(email_template.email_from),'relate.contract.payment.term',line.id)
                
                if not mail_from:
                    continue
                
                # body with data line
                
                mail_body += '<h3>Contratto %s </h3>' % (contract.name)
                due_date = datetime.strptime(line.due_date, "%Y-%m-%d")   
                mail_body += '<div><h2> %s </h2></div>' % (line.name, )
                mail_body += '<div><h3> Scadenza %s - Importo %s </h3></div>' % ( due_date.strftime('%d-%m-%Y'), '{:16.2f}'.format(line.amount) )
                
                message_vals = {
                        'type': 'email',
                        'email_from': contract.manager_id.email,
                        'subject' : 'Contratto da fatturare',
                        }
                message_id = mail_message_obj.create(cr, uid, message_vals)
                
                mail_id = mail_obj.create(cr, uid, {
                        'mail_message_id' : message_id,
                        'mail_server_id' : user_server_mail and user_server_mail.id or email_template.mail_server_id and email_template.mail_server_id.id or False,
                        'state' : 'outgoing',
                        'auto_delete' : email_template.auto_delete,
                        'email_from' : mail_from,
                        'email_to' : follower.email,
                        #'reply_to' : reply_to,
                        'body_html' : mail_body,
                        })
                
                mail_ids += [mail_id,]
        
        if mail_ids:
            mail_obj.send(cr, uid, mail_ids)
            print "Xxx"
        
        _logger.info('[SUBSCRIPTION SEND MAIL] Sended %s mails for %s template' % (len(mail_ids), email_template.name))
        res ={}
        
        return res
    
    def button_invoiced(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'relate.contract.payment.term', line.id, 'invoiced', cr)
        return True
    
    def button_invoiced_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state': '2binvoiced'})
            wf_service = netsvc.LocalService('workflow')
            for id in ids:
                wf_service.trg_create(uid, self._name, id, cr)
        return True
    
    
    _columns = {
        'state': fields.selection([
            ('2binvoiced', 'To be invoiced'),
            ('invoiced', 'Invoiced'),
            ], 'Status', readonly=True, track_visibility='onchange', select=True),
        'contract_id': fields.many2one('account.analytic.account', 'Contract'),
        'sequence': fields.integer('Sequence', help="Gives the order in which the items will be checked."),
        'due_date': fields.date('Due date'),
        'name': fields.char('Description', size=128, required=True),
        'amount': fields.float('Amount'),
    }
    _defaults ={
        'state': '2binvoiced',
    }
    _order = "sequence"
    

class relate_config_journal(orm.Model):
    
    _name = "relate.config.journal"
    _description = "Relate - Configuration - Journals"
    
    def _check_one_journal(self, cr, uid, ids, context=None):
        for element in self.browse(cr, uid, ids, context=context):
            element_ids = self.search(cr, uid, [('journal_id','=', element.journal_id.id),('line_product','=', element.line_product.id)], context=context)
            if len(element_ids) > 1:
                return False
        return True
    
    _columns = {
        'journal_id': fields.many2one('account.analytic.journal', 'Journal', required=True),
        'line_product': fields.many2one('product.product', 'Product on line'),
        'line_to_invoice': fields.boolean('To be invoiced'),
        'product_to_invoice': fields.many2one('product.product', 'Product To invoice'),
        'product_for_line_without_product': fields.many2one('product.product', 'Product For line Without Product'),
        'coeff_cost_no_product': fields.float('Coeff. to invoice cost without product'),
    }
    
    _constraints = [
        (_check_one_journal, 'Error! Journal-product already exists.', ['journal_id']),
    ]


class relate_contract_default_invoice(orm.Model):
    
    _name = "relate.contract.default.invoice"
    _description = "Relate - Contract default invoice"
    
    def _check_one_journal(self, cr, uid, ids, context=None):
        for element in self.browse(cr, uid, ids, context=context):
            element_ids = self.search(cr, uid, [('journal_id','=', element.journal_id.id),('line_product','=', element.line_product.id),('contract_id','=', element.contract_id.id)], context=context)
            if len(element_ids) > 1:
                return False
        return True
    
    _columns = {
        'contract_id': fields.many2one('account.analytic.account', 'Contract', required=True, ondelete="cascade"),
        'journal_id': fields.many2one('account.analytic.journal', 'Journal', required=True),
        'line_product': fields.many2one('product.product', 'Product on line'),
        'line_to_invoice': fields.boolean('To be invoiced'),
        'product_to_invoice': fields.many2one('product.product', 'Product To invoice'),
        'product_for_line_without_product': fields.many2one('product.product', 'Product For line Without Product'),
        'coeff_cost_no_product': fields.float('Coeff. to invoice cost without product'),
    }
    
    _constraints = [
        (_check_one_journal, 'Error! Journal-Product already exists.', ['journal_id']),
    ]
    
class project_task_work(orm.Model):
    
    _inherit = "project.task.work"
    _columns = {
        'name': fields.text('Work summary'),  # No size limit with text type
        'relate_task_line_id': fields.many2one('relate.task.line', 'Task Ref', ondelete='cascade'),
        'relate_is_trip': fields.boolean('Is Trip Relate'),
        'line_to_invoice': fields.boolean('To be invoiced'),
        'product_to_invoice': fields.many2one('product.product', 'Product To invoice'),
        'amount_to_invoice': fields.float('Amount to Invoice')
    }
    
    def default_get(self, cr, uid, fields, context=None):
        '''
        Lines Default invoice from contract config
        ''' 
        res = super(project_task_work, self).default_get(cr, uid, fields, context=context)
        
        project_task_id = context.get('project_task_id', False)
        user_id = context.get('user_id', False)
        if project_task_id:
            task = self.pool.get('project.task').browse(cr, uid, project_task_id)
            contract_id = task.project_id.analytic_account_id.id
            # Journal from user
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', user_id)])
            if employee_ids:
                employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
                j_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, [('journal_id', '=', employee.journal_id.id), ('contract_id', '=', contract_id), ('line_product', '=', False)])
                #inv_def_search = [('contract_id','=', contract_id),('journal_id','=', j_ids[0]),('line_product','=', rel.line_id.product_id.id),'|',('contract_id','=', contract_id),('journal_id','=', j_ids[0])]
                #role_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, inv_def_search, order='line_product DESC', limit = 1)
                
                for j_default in self.pool.get('relate.contract.default.invoice').browse(cr, uid, j_ids):
                    
                    if j_default.line_to_invoice:
                        res.update({'line_to_invoice': j_default.line_to_invoice})
                    if j_default.product_to_invoice: 
                        res.update({'product_to_invoice': j_default.product_to_invoice.id})
        return res
    
    def create(self, cr, uid, vals, *args, **kwargs):
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        task_obj = self.pool.get('project.task')
        product_obj = self.pool.get('product.product')
        uom_obj = self.pool.get('product.uom')
        
        vals_line = {}
        context = kwargs.get('context', {})
        # If Trip, It create the analytic line here and avoid to create by super().
        # Super always create the analytic line with product chained to timesheet
        relate_is_trip = vals.get('relate_is_trip', {})
        #if 'ralate_is_trip' in vals and vals['relate_is_trip'] == True:
        if relate_is_trip:
            task_obj = task_obj.browse(cr, uid, vals['task_id'])
            product = product_obj.browse(cr, uid, vals['product_id'])
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', vals['user_id'])])
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
            
            vals_line['name'] = vals['name']
            vals_line['user_id'] = vals['user_id']
            vals_line['product_id'] = vals['product_id']
            vals_line['date'] = vals['date'][:10]
            vals_line['relate_is_trip'] = True

            # Calculate quantity based on employee's product's uom
            vals_line['unit_amount'] = vals['hours']
            
            if 'product_uom_id' not in vals:
                 vals['product_uom_id'] = product.uom_id.id
            if vals['product_uom_id'] != product.uom_id.id :
                vals_line['unit_amount'] = uom_obj._compute_qty(cr, uid, default_uom, vals['hours'], vals['product_uom_id'])
            else:
                vals_line['unit_amount'] = vals['unit_amount'] 
            acc_id = task_obj.project_id and task_obj.project_id.analytic_account_id.id or False
            
            if acc_id:
                vals_line['account_id'] = acc_id
                res = timesheet_obj.on_change_account_id(cr, uid, False, acc_id)
                if res.get('value'):
                    vals_line.update(res['value'])
                vals_line['general_account_id'] = vals['general_account_id']
                vals_line['journal_id'] = vals['journal_id']
                vals_line['amount'] = 0.0
                vals_line['product_uom_id'] = vals['product_uom_id']
                amount = vals_line['unit_amount']
                prod_id = vals['product_id']
                unit = False
                timeline_id = timesheet_obj.create(cr, uid, vals=vals_line, context=context)

                # Compute based on pricetype
                amount_unit = timesheet_obj.on_change_unit_amount(cr, uid, timeline_id,
                    prod_id, amount, False, unit, vals_line['journal_id'], context=context)
                if employee.relate_trip_cost_from_timesheet_coeff:
                    amount_unit['value']['amount'] = round(-1.00 * vals_line['unit_amount'] * employee.product_id.standard_price * employee.relate_trip_cost_from_timesheet_coeff, 2)
                
                if amount_unit and 'amount' in amount_unit.get('value',{}):
                    updv = { 'amount': amount_unit['value']['amount'] }
                    timesheet_obj.write(cr, uid, [timeline_id], updv, context=context)
                vals['hr_analytic_timesheet_id'] = timeline_id
            
                # Avoid to recreate another analytic line
                kwargs['context']['no_analytic_entry'] = True
                 
        res_id = super(project_task_work,self).create(cr, uid, vals, *args, **kwargs)
        
        # Align with analytic_account_line
        task = self.browse(cr, uid, res_id)
        if task.hr_analytic_timesheet_id:
            self.pool.get('account.analytic.line')._align_to_project_task_work(cr, uid, [task.hr_analytic_timesheet_id.line_id.id], name=None, args=None, context=kwargs['context'])
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_task_work,self).write(cr, uid, ids, vals, context)
        #
        # Re-execute write with variations on product policies
        #
        """
        When a project task work gets updated, handle its hr analytic timesheet.
        """
        if context is None:
            context = {}
        timesheet_obj = self.pool.get('hr.analytic.timesheet')
        uom_obj = self.pool.get('product.uom')
        result = {}

        if isinstance(ids, (long, int)):
            ids = [ids]

        for task in self.browse(cr, uid, ids, context=context):
            line_id = task.hr_analytic_timesheet_id
            if not line_id:
                # if a record is deleted from timesheet, the line_id will become
                # null because of the foreign key on-delete=set null
                continue
            
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', task.user_id.id)])
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
            vals_line = {}
            if 'name' in vals:
                vals_line['name'] = '%s: %s' % (tools.ustr(task.task_id.name), tools.ustr(vals['name'] or '/'))
            if 'user_id' in vals:
                vals_line['user_id'] = vals['user_id']
            if 'date' in vals:
                vals_line['date'] = vals['date'][:10]
            if 'hours' in vals:
                vals_line['unit_amount'] = vals['hours']
                prod_id = vals_line.get('product_id', line_id.product_id.id) # False may be set
                
                # Put user related details in analytic timesheet values
                details = self.get_user_related_details(cr, uid, vals.get('user_id', task.user_id.id))
                for field in ('product_id', 'general_account_id', 'journal_id', 'product_uom_id'):
                    if details.get(field, False):
                        if not vals.get(field,False): ## no overrid if trip product is set <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                            vals_line[field] = details[field]
                        else:
                            vals_line[field] = vals[field]
                            
                # Check if user's default UOM differs from product's UOM
                user_default_uom_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.project_time_mode_id.id
                if details.get('product_uom_id', False) and details['product_uom_id'] != user_default_uom_id:
                    vals_line['unit_amount'] = uom_obj._compute_qty(cr, uid, user_default_uom_id, vals['hours'], details['product_uom_id'])

                # Compute based on pricetype
                amount_unit = timesheet_obj.on_change_unit_amount(cr, uid, line_id.id,
                    prod_id=prod_id, company_id=False,
                    unit_amount=vals_line['unit_amount'], unit=False, journal_id=vals_line['journal_id'], context=context)
                
                if amount_unit and 'amount' in amount_unit.get('value',{}):
                    vals_line['amount'] = amount_unit['value']['amount']
                
                if task.relate_is_trip:
                    if employee.relate_trip_cost_from_timesheet_coeff:
                        vals_line['amount'] = round(-1.00 * vals_line['unit_amount'] * employee.product_id.standard_price * employee.relate_trip_cost_from_timesheet_coeff, 2)
                    elif employee.relate_trip_product_id:
                        vals_line['amount']  = round(-1.00 * vals_line['unit_amount'] * employee.relate_trip_product_id.standard_price, 2)
            self.pool.get('hr.analytic.timesheet').write(cr, uid, [line_id.id], vals_line, context=context)
        
        
        return res

    def unlink(self, cr, uid, ids, *args, **kwargs):
        return super(project_task_work,self).unlink(cr, uid, ids,*args, **kwargs)


class account_analytic_journal(orm.Model):
    
    _inherit = "account.analytic.journal"
    
    _columns = {
        'relate_expense': fields.boolean('Relate Expense'),
        'relate_material': fields.boolean('Relate Material'),
        'relate_vehicle': fields.boolean('Relate Vehicle'),
    }
    
class account_analytic_line(orm.Model):
    
    _inherit = "account.analytic.line"
    
    def _check_inv(self, cr, uid, ids, vals):
        '''
        Ometto controllo >> momentaneo<<
        Solo x allineare il valore da fatturare con Default invoice del contratto
        '''
        '''
        select = ids
        if isinstance(select, (int, long)):
            select = [ids]
        if ( not vals.has_key('invoice_id')) or vals['invoice_id' ] == False:
            for line in self.browse(cr, uid, select):
                if line.invoice_id:
                    raise osv.except_osv(_('Error!'),
                        _('You cannot modify an invoiced analytic line!'))
        '''
        return True
    
    def _align_to_project_task_work(self, cr, uid, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids):
            rel_ids = self.pool.get('hr.analytic.timesheet').search(cr, uid, [('line_id', '=', line.id)])
            task_ids = self.pool.get('project.task.work').search(cr, uid, [('hr_analytic_timesheet_id', 'in', rel_ids)])
            for task in self.pool.get('project.task.work').browse(cr, uid, task_ids):
                # compute amounts to invoice
                context.update({'project_task_id': task.task_id.id}) # pass ref to project by context
                product = False
                product_uom = False
                if task.product_to_invoice:
                    product = task.product_to_invoice
                    product_uom = task.product_to_invoice.uom_id.id
                
                invoice_datas = self.get_amount_to_invoice(cr, uid, ids, product, task.hours, product_uom, task.line_to_invoice, False, context=context)
                val = {
                    'relate_task_line_id' : task.relate_task_line_id.id or False,
                    'line_to_invoice' : task.line_to_invoice or False,
                    'product_to_invoice' : task.product_to_invoice.id or False,
                    'amount_to_invoice' : invoice_datas['amount'] or 0.00,
                    'date' : task.relate_task_line_id.task_id.date or False,
                    }
                res[line.id] = val
                self.write(cr, uid, [line.id], val)
        return res
    
    def _get_relate_from_project_task(self, cr, uid, ids, context=None):
        res = []
        for line in self.pool.get('project.task.work').browse(cr, uid, ids):
            if line.hr_analytic_timesheet_id: # in case of unlik line
                res.append(line.hr_analytic_timesheet_id.line_id.id) # ref to analytic line
        return res

    def _balance(self, cr, uid, ids, field_names, args, context=None):
        '''
        compute balance
        '''
        dec_round = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.amount_to_invoice:
                res[line.id] = {'balance' : line.amount_to_invoice - round( -1 * line.amount, dec_round) }
            else:
                res[line.id] = {'balance' : line.amount }
        return res
        
    _columns = {
        'name': fields.text('Account/Contract Name', required=True), # No size limit with text type
        'relate_task_line_id': fields.many2one('relate.task.line', 'Task Ref', ondelete='cascade'),
        'relate_is_trip': fields.boolean('Is Trip Relate'),
        'line_to_invoice': fields.boolean('To invoice'),
        'product_to_invoice': fields.many2one('product.product', 'Product to Invoice', ondelete='cascade'),
        'amount_to_invoice': fields.float('Amount to Invoice'),
        'align_to_project_task_work': fields.function(_align_to_project_task_work,  multi='align', 
            #type='many2one', relation='project.task.work', string='Align', method=True,
            store={
                   'project.task.work': (_get_relate_from_project_task, ['date', 'hours','relate_task_line_id', 'line_to_invoice', 'product_to_invoice', 'amount_to_invoice'], 10),
                   #'relate.task': (_get_relate_from_task, ['date'], 10),
                   #'account.analytic.line': (lambda self,cr,uid,ids,context=None: ids, None, 10),
                  },
            ),
        'balance': fields.function(_balance, string='Balance', multi='balance', store=True),
    }

    
    def default_get_to_invoice(self, cr, uid, journal_id=None, product_id=None, context=None):
        '''
        Default to invoice analytic line
        '''
        project_task_id = context.get('project_task_id', False)
        journal_type = context.get('journal_type', False)
        user_id = context.get('user_id', False)
        product_id = context.get('product_id', False)
        role = {
            'line_to_invoice' : False,
            'product_to_invoice' : False,
            }
        # Journal to search role
        j_search = []
        if journal_type == 'vehicle':
            j_search.append(('relate_vehicle', '=', True))
        if journal_type == 'material':
            j_search.append(('relate_material', '=', True))
        if journal_type == 'expense':
            j_search.append(('relate_expense', '=', True))
        j_ids = self.pool.get('account.analytic.journal').search(cr, uid, j_search)
        
        # Role from contract + journal
        if j_ids[0] and project_task_id :
            task = self.pool.get('project.task').browse(cr, uid, project_task_id)
            contract_id = task.project_id.analytic_account_id.id
            
            #inv_def_search = [('contract_id','=', contract_id),('journal_id','=', j_ids[0]),('line_product','=', rel.line_id.product_id.id),'|',('contract_id','=', contract_id),('journal_id','=', j_ids[0])]
            #role_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, inv_def_search, order='line_product DESC', limit = 1)
            role_ids = self.pool.get('relate.contract.default.invoice').search(cr, uid, [('journal_id', '=', j_ids[0]), ('contract_id', '=', contract_id)])
            if role_ids:
                role_inv = self.pool.get('relate.contract.default.invoice').browse(cr, uid, role_ids[0])
                role = {
                    'line_to_invoice' : role_inv.line_to_invoice or False,
                    'product_to_invoice' : role_inv.product_to_invoice or False,
                    }
            
        return role
    
    def get_amount_to_invoice(self, cr, uid, ids, product, qty, product_uom_id, line_to_invoice, coeff_cost_no_product=0, context=None):
        result = {
               'price_unit' : 0.00,
               'discount': 0.00,
               'discount2': 0.00,
               'amount': 0.00,
               }
        if not line_to_invoice or not product:
            return result
        # Retrive pricelist from contract
        pricelist = False
        contract_id = context.get('contract_id', False)
        project_task_id = context.get('project_task_id', False)
        if contract_id:
            contract = self.pool.get('account.analytic.account').browse(cr, uid, contract_id)
            pricelist = contract.pricelist_id.id
            partner_id = contract.partner_id.id
            if not partner_id:
                raise osv.except_osv(_('Error!'),_("Nessun partner specificato nel contratto"))
        elif project_task_id:
            task = self.pool.get('project.task').browse(cr, uid, project_task_id)
            pricelist = task.project_id.analytic_account_id.pricelist_id.id
            partner_id = task.project_id.analytic_account_id.partner_id.id
            if not partner_id:
                raise osv.except_osv(_('Error!'),_("Nessun partner specificato nel contratto"))
                
        if product:
            price = False
            if not pricelist:
                raise osv.except_osv(_('Error!'),_("Nessun listino configurato sul contratto"))
            else:
                price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                        product.id, qty or 1.0, partner_id, {
                            'uom': product_uom_id,
                            #'date': date_order, x ora niente
                            })[pricelist]
                if price is False:
                    raise osv.except_osv(_('Error!'),_("Cannot find a pricelist line matching this product and quantity.\n"
                            "You have to change either the product, the quantity or the pricelist."))
                # Retrieve price from amount of line
                if price == 0 and product.standard_price == 0 and ids[0]:
                    line = self.browse(cr, uid, ids[0])
                    price = round( (line.amount * -1 ) / line.unit_amount , self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
                    if price > 0:
                        price = round( price * coeff_cost_no_product, self.pool.get('decimal.precision').precision_get(cr, uid, 'Account'))
                    
            result.update({'price_unit': price})
            result.update({'amount': round(1.00 * price * qty , self.pool.get('decimal.precision').precision_get(cr, uid, 'Account'))})
        return result
    
    def on_change_relate_product_id(self, cr, uid, ids, product_id, line_to_invoice, context=None):
        res ={}
        val={}
        if product_id:
            # journal will be retrieve from journal_type in the context
            default_invoice = self.default_get_to_invoice(cr, uid, False, product_id, context)
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            invoice_datas = self.get_amount_to_invoice(cr, uid, ids, product, 1.0, product.uom_id.id, default_invoice.get('line_to_invoice', False), context=context)
            val = {
                   'product_uom_id': product.uom_id.id,
                   'name': product.name,
                   'unit_amount': 1.00,
                   'amount': product.standard_price,
                   'amount_to_invoice': invoice_datas['amount'],
                   'line_to_invoice': default_invoice.get('line_to_invoice', False),
                   'product_to_invoice': default_invoice.get('product_to_invoice', product.id),
                   }
        res = {'value': val}
        return res
    
    def on_change_relate_quantity(self, cr, uid, ids, product_id, quantity, product_uom_id, line_to_invoice, context=None):
        uom_obj = self.pool.get('product.uom')
        res ={}
        val={}
        if product_id and quantity:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            unit_amount = quantity
            amount  = 0
            if product_uom_id != product.uom_id.id :
                unit_amount = uom_obj._compute_qty(cr, uid, product.uom_id.id, quantity, product_uom_id)
            invoice_datas = self.get_amount_to_invoice(cr, uid, ids, product, unit_amount, product.uom_id.id, line_to_invoice, context=context)
            val = {
                   'product_uom_id': product.uom_id.id,
                   'name': product.name,
                   'amount': round( 1.00 * product.standard_price * unit_amount, self.pool.get('decimal.precision').precision_get(cr, uid, 'Account') ),
                   'amount_to_invoice': invoice_datas['amount'],
                   'product_to_invoice': product.id,
                   }
        res = {'value': val}
        return res
    
    
    def create(self, cr, uid, vals, context=None):
        res_id = super(account_analytic_line, self).create(cr, uid, vals, context=context)        
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_analytic_line, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, *args, **kwargs):
        res = super(account_analytic_line, self).unlink(cr, uid, ids, *args, **kwargs)
        return res
