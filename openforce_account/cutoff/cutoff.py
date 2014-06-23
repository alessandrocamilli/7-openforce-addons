# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
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
from osv import osv, fields, orm
from openerp.tools.translate import _

class account_cutoff(orm.Model):
    
    _inherit = 'account.cutoff'
    
    def create_move(self, cr, uid, ids, context=None):
        '''
        Add to moves, the flag to account reverse
        '''
        account_move_obj = self.pool['account.move']
        res = super(account_cutoff, self).create_move(cr, uid, ids, context=None)
        if 'res_id' in res and res['res_id']:
            move_id = res.get('res_id')
            account_move_obj.write(cr, uid, [move_id], {'to_be_reversed': True})
        
        return res

    
    