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

class res_partner(orm.Model):
    
    _inherit = 'res.partner'
    
    def _get_progressive_code(self,cr,uid,context=None):
        res = {}
        res = self.pool.get('ir.sequence').get(cr, uid, 'res.partner.ref'),
        return res[0]
    
    def _get_trasportation_reason(self,cr,uid,context=None):
        res = {}
        res = self.pool.get('stock.picking.transportation_reason').search(cr, uid, [('name','=','VENDITA')])
        return res[0]
    
    _defaults = {
        'ref': _get_progressive_code,
        'transportation_reason_id' : _get_trasportation_reason,
      }
'''
    def create(self, cr, uid, vals, *args, **kwargs):
        
        # P.IVA o Codice fiscale immesso
        if 'vat' in vals and not vals['vat'] \
                and 'fiscalcode' in vals and not vals['fiscalcode']:
            raise osv.except_osv(_('Error!'), _('Inserire P.IVA o Codice Fiscale') )
        
        res_id = super(res_partner,self).create(cr, uid, vals, *args, **kwargs)
        return res_id'''