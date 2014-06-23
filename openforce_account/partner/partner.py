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
    
    _columns = {
        'bank_payment_customer': fields.many2one('res.partner.bank', 'Bank Payment Customer', domain="[('company_id', '=', 1)]"),
        'bank_payment_supplier': fields.many2one('res.partner.bank', 'Bank Payment Supplier', domain="[('company_id', '=', 1)]"),
    }
    
    def create(self, cr, uid, vals, *args, **kwargs):
        # No P.IVA duplicata
        if 'vat' in vals and vals['vat']:
            partner_exists = self.pool.get('res.partner').search(cr, uid, [('vat', '=', vals['vat'])])
            if partner_exists:
                partner = self.pool.get('res.partner').browse(cr, uid, partner_exists[0])
                raise osv.except_osv(_('Attenzione !'),_("Esiste un partner con questa Partita IVA : %s - %s") % (partner.name, partner.city))
            
        # No Codice fiscale duplicato
        if 'fiscalcode' in vals and  vals['fiscalcode']:
            partner_exists = self.pool.get('res.partner').search(cr, uid, [('fiscalcode', '=', vals['fiscalcode'])])
            if partner_exists:
                partner = self.pool.get('res.partner').browse(cr, uid, partner_exists[0])
                raise osv.except_osv(_('Attenzione !'),_("Esiste un partner con Codice Fiscale : %s - %s") % (partner.name, partner.city)) 
        
        res_id = super(res_partner,self).create(cr, uid, vals, *args, **kwargs)
        return res_id
    
class res_partner_bank(orm.Model):
    
    _inherit = 'res.partner.bank'
    
    def _check_bank(self, cr, uid, ids, context=None):
        ''' Bic code not required'''
        '''for partner_bank in self.browse(cr, uid, ids, context=context):
            if partner_bank.state == 'iban' and not partner_bank.bank.bic:
                return False'''
        return True
    
    