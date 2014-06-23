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
{
    'name': 'Openforce - Relate',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """Openforce - Relate

Functionalities:
- Create the first task for the new project chained to contract
- Relate of works divided by timesheet, expense and materials
""",
    'author': 'Openforce',
    'website': 'http://www.openforce.it',
    'license': 'AGPL-3',
    "depends" : ['web', 'analytic' ,'project','project_timesheet', 'fleet', 'hr', 'hr_attendance', 'email_template', 'openforce_hr'],
    "css" : ['static/src/css/analytic.css'],
    "data" : [
        'security/security.xml',
        'hr/hr_view.xml',
        'fleet/fleet_view.xml',
        'security/ir.model.access.csv',
        'account/account_view.xml',
        'analytic/analytic_view.xml',
        'relate_data.xml',
        'relate_view.xml',
        'relate_sequence.xml',
        'relate_workflow.xml',
        'report/relate_line_report_view.xml',
        ],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: