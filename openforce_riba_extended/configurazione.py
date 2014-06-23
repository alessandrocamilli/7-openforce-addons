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

from openerp.osv import fields, orm

class riba_configurazione(orm.Model):

    _inherit = "riba.configurazione"

    _columns = {
        'acceptance_account_id' : fields.many2one('account.account', "Acceptance account", 
           # domain=[('type', '=', 'receivable')], help='Account used when Ri.Ba. is accepted by the bank'),
            help='Account used when Ri.Ba. is accepted by the bank'),
        'unsolved_bank_account_id' : fields.many2one('account.account', "Account Bank for unsolved effets and charge", 
            help='Account Bank for unsolved effets and charge'),
        'unsolved_bank_account_accreditation_id' : fields.many2one('account.account', "Account Bank for effectss", 
            help='Account used when Ri.Ba. is accreditation by bank'),
        'unsolved_reverse_sbf_with_payment' : fields.boolean('Reverse SBF with payment',
            help='In the unsolved registration, the lines for reverse SBF will not create'),
        'payment_journal_id' : fields.many2one('account.journal', "Payment journal", 
            domain=[('type', '=', 'bank')],
            help="Journal used when Ri.Ba. is paid"),
        'payment_bank_account_id' : fields.many2one('account.account', "Account Bank for payment", 
            help='Account used when Ri.Ba. is paid by partner'),
        'payment_effects_bank_account_id' : fields.many2one('account.account', "Account Bank for effects", 
            help='Account used when Ri.Ba. is accreditation by bank'),
    }

    _defaults = {
    }
