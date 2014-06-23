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

from openerp.osv import fields,orm
from openerp import tools

class report_relate_line(orm.Model):
    _name = "report.relate.line"
    _description = "Relate task line "
    _auto = False
    _columns = {
        'nbr': fields.integer('# of tasks', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'year': fields.char('Year', size=64, required=False, readonly=True),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True),
        'task_id': fields.many2one('relate.task', 'Task Ref', required=True),
        'project_task_id': fields.many2one('project.task', 'Project Task Ref', required=True),
        'hours_tot': fields.float('Hours Tot', readonly=True),
        'hours_trip': fields.float('Hours Trip', readonly=True),
        'kilometers': fields.float('kilometers'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'date': fields.date('Date', readonly=True),
        'number':  fields.char('Number', size=64),
        'vehicle':  fields.many2one('fleet.vehicle', 'Vehicle', readonly=True),
    }
    _order = 'number desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_relate_line')
        cr.execute("""
            CREATE view report_relate_line as
              SELECT
                    (select 1 ) AS nbr,
                    l.id,
                    to_char(t.date, 'YYYY') as year,
                    to_char(t.date, 'MM') as month,
                    to_char(t.date, 'YYYY-MM-DD') as day,
                    l.task_id,
                    l.project_task_id,
                    pt.project_id as project_id,
                    t.user_id,
                    t.date,
                    t.number,
                    t.vehicle,
                    pt.partner_id,
                    AVG(hours_trip) as hours_trip,
                    AVG(kilometers) as kilometers,
                    SUM(hours) as hours_tot
                                        
              FROM relate_task_line l 
              LEFT JOIN relate_task t ON t.id = l.task_id
              LEFT JOIN project_task pt ON pt.id = l.project_task_id
              LEFT JOIN project_project p ON p.id = pt.project_id
              LEFT JOIN project_task_work ptw ON ptw.relate_task_line_id = l.id

              GROUP BY
              nbr, l.id, year, month, day, l.task_id, l.project_task_id, pt.project_id, t.user_id, t.date, t.number, t.vehicle, pt.partner_id
              ORDER BY
              number desc

        """)

