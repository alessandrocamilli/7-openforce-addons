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


import tools
import base64
from openerp.osv import fields,orm
from tools.translate import _
import datetime

class riba_file_export(orm.TransientModel):

    def act_getfile(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        order_obj = self.pool.get('riba.distinta').browse(cr, uid, active_ids, context=context)[0]
        credit_bank = order_obj.config.bank_id
        name_company = order_obj.config.company_id.partner_id.name
        if not credit_bank.iban:
           raise orm.except_orm('Error', _('No IBAN specified'))
        iban_code = credit_bank.iban
        iban_code = iban_code.replace(" ", "")
        #credit_abi = credit_bank.iban[5:10]
        #credit_cab = credit_bank.iban[10:15]
        #credit_conto = credit_bank.iban[-12:]
        credit_abi = iban_code[5:10]
        credit_cab = iban_code[10:15]
        credit_conto = iban_code[-12:]
        if not credit_bank.codice_sia:
           raise orm.except_orm('Error', _('No SIA Code specified for: ') + name_company)
        credit_sia = credit_bank.codice_sia
        credit_account = credit_bank.iban[15:27]
        dataemissione = datetime.datetime.now().strftime("%d%m%y")
        nome_supporto = datetime.datetime.now().strftime("%d%m%y%H%M%S") + credit_sia
        creditor_address = order_obj.config.company_id.partner_id
        creditor_street = creditor_address.street or ''
        creditor_city = creditor_address.city or ''
        creditor_province = creditor_address.province.code or ''
        if not order_obj.config.company_id.partner_id.vat and not order_obj.config.company_id.partner_id.fiscalcode:
           raise orm.except_orm('Error', _('No VAT or Fiscalcode specified for: ') + name_company)
        array_testata = [
               credit_sia,
               credit_abi,
               credit_cab,
               credit_conto,
               dataemissione,
               nome_supporto,
               'E',
               name_company,
               creditor_address.street or '',
               creditor_address.zip or '' + ' ' + creditor_city,
               order_obj.config.company_id.partner_id.ref or '',
               order_obj.config.company_id.partner_id.vat and order_obj.config.company_id.partner_id.vat[2:] or order_obj.config.company_id.partner_id.fiscalcode,
               ]
        arrayRiba = []
        for line in order_obj.line_ids:
            debit_bank = line.bank_id
            debitor_address = line.partner_id
            debitor_street = debitor_address.street or ''
            debitor_zip = debitor_address.zip or ''
            # Priority to abi-cab of the bank
            if debit_bank.bank_abi and debit_bank.bank_cab:
                debit_abi = debit_bank.bank_abi
                debit_cab = debit_bank.bank_cab
            else:
                if not debit_bank.iban:
                   raise orm.except_orm('Error', _('No IBAN specified for ') + line.partner_id.name)
                iban_code = debit_bank.iban
                iban_code = iban_code.replace(" ", "")
                debit_abi = iban_code[5:10]
                debit_cab = iban_code[10:15]
            debitor_city = debitor_address.city or ''
            debitor_province = debitor_address.province.code or ''
            if not line.due_date: # ??? VERIFICARE
                due_date =  '000000'
            else:
                due_date = datetime.datetime.strptime(line.due_date[:10], '%Y-%m-%d').strftime("%d%m%y")

            if not line.partner_id.vat and not line.partner_id.fiscalcode:
                raise orm.except_orm('Error', _('No VAT or Fiscal code specified for ') + line.partner_id.name)
            Riba = [
                        line.sequence,
                        due_date,
                        line.amount,
                        line.partner_id.name,
                        line.partner_id.vat and line.partner_id.vat[2:] or line.partner_id.fiscalcode,
                        debitor_street,
                        debitor_zip,
                        debitor_city,
                        debitor_province,
                        debit_abi,
                        debit_cab,
                        debit_bank.bank and debit_bank.bank.name or debit_bank.bank_name,
                        line.partner_id.ref or '',
                        #line.move_line_id.name,
                        line.invoice_number,
                        #datetime.datetime.strptime(line.distinta_id.date_created, '%Y-%m-%d').strftime("%d/%m/%Y"),
                        line.invoice_date,
                        ]
            arrayRiba.append(Riba)

        out=base64.encodestring(self._creaFile(array_testata, arrayRiba).encode("utf8"))
        self.write(cr, uid, ids, {'state':'get', 'riba_.txt':out}, context=context)

        model_data_obj = self.pool.get('ir.model.data')
        view_rec = model_data_obj.get_object_reference(cr, uid, 'l10n_it_ricevute_bancarie', 'wizard_riba_file_export')
        view_id = view_rec and view_rec[1] or False

        return {
           'view_type': 'form',
           'view_id' : [view_id],
           'view_mode': 'form',
           'res_model': 'riba.file.export',
           'res_id': ids[0],
           'type': 'ir.actions.act_window',
           'target': 'new',
           'context': context,
        }

    _inherit = "riba.file.export"

    


