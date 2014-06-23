# -*- coding: utf-8 -*-

#################################################################################
#    Author: Alessandro Camilli a.camilli@yahoo.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_asset(osv.osv):
    _name = "account.asset.asset"
    _inherit = "account.asset.asset"
    
    def _amount_residual_fiscal(self, cr, uid, ids, name, args, context=None):
        
        ##
        ## >> calcolare tenendo conto delle variazioni su account_move_line
        ##   e del depreciation line fiscal
        ##
        cr.execute("""SELECT
                l.asset_id as id, SUM(abs(l.debit-l.credit)) AS amount
            FROM
                account_move_line l
            WHERE
                l.asset_id IN %s GROUP BY l.asset_id """, (tuple(ids),))
        res=dict(cr.fetchall())
        for asset in self.browse(cr, uid, ids, context):
            res[asset.id] = asset.purchase_value - res.get(asset.id, 0.0) - asset.salvage_value
        for id in ids:
            res.setdefault(id, 0.0)
        return res
    
    def _fiscal_method_number(self, cr, uid, ids, name, args, context=None):
        
        for asset in self.browse(cr, uid, ids, context):
            if asset.fiscal_method == 'percent':
                res[asset.id] = len(asset.fiscal_percent_ids)
        return res
    
    _columns =  {
        'fiscal': fields.boolean('Fiscal asset plan', readonly=True, states={'draft':[('readonly',False)]}),
        'fiscal_asset_ref_id': fields.many2one('account.asset.asset', 'Parent Asset civil', 
                readonly=True, states={'draft':[('readonly',False)]}, 
                domain="[('fiscal','=', False)]" ),
        'child_fiscal_ids': fields.one2many('account.asset.asset', 'fiscal_asset_ref_id', 'Children Fiscal Assets'),
        'pre_owned': fields.boolean('Pre-owned', readonly=True, states={'draft':[('readonly',False)]}),
        'method': fields.selection([('linear','Linear'),('degressive','Degressive'),('percent','percent')], 'Computation Method', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Choose the method to use to compute the amount of depreciation lines.\n"\
            "  * Linear: Calculated on basis of: Gross Value / Number of Depreciations\n" \
            "  * Degressive: Calculated on basis of: Residual Value * Degressive Factor"),
        'percent_ids': fields.one2many('account.asset.percent.plan.line', 'asset_id', 'Percent Plan Line'),
        'start_date': fields.date('Date start utilization', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'fiscal_method': fields.selection([('linear','Linear'),('degressive','Degressive'),('percent','percent')], 'Computation Method', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Choose the method to use to compute the amount of depreciation lines.\n"\
            "  * Linear: Calculated on basis of: Gross Value / Number of Depreciations\n" \
            "  * Degressive: Calculated on basis of: Residual Value * Degressive Factor"),
        'a': fields.one2many('account.asset.percent.plan.line.fiscal', 'asset_id', 'Percent Plan Line'),
        'fiscal_method_time': fields.selection([('number','Number of Depreciations'),('end','Ending Date')], 'Time Method', required=True, readonly=True, states={'draft':[('readonly',False)]},
                                  help="Choose the method to use to compute the dates and number of depreciation lines.\n"\
                                       "  * Number of Depreciations: Fix the number of depreciation lines and the time between 2 depreciations.\n" \
                                       "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond."),
        'fiscal_percent_ids': fields.one2many('account.asset.percent.plan.line.fiscal', 'asset_id', 'Percent Plan Line'),
        'fiscal_prorata':fields.boolean('Prorata Temporis', readonly=True, states={'draft':[('readonly',False)]}, help='Indicates that the first depreciation entry for this asset have to be done from the purchase date instead of the first January'),
        'fiscal_method_number': fields.integer('Number of Depreciations', readonly=True, states={'draft':[('readonly',False)]}, help="The number of depreciations needed to depreciate your asset"),
        'fiscal_method_period': fields.integer('Number of Months in a Period', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The amount of time between two depreciations, in months"),
        'fiscal_method_progress_factor': fields.float('Degressive Factor', readonly=True, states={'draft':[('readonly',False)]}),
        'fiscal_value_residual': fields.function(_amount_residual_fiscal, method=True, digits_compute=dp.get_precision('Account'), string='Residual Value'),
        'fiscal_depreciation_line_ids': fields.one2many('account.asset.depreciation.line.fiscal', 'asset_id', 'Fiscal Depreciation Lines', readonly=True, states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'pre_owned_asset_coefficient_first_line': fields.related('category_id', 'pre_owned_asset_coefficient_first_line', string="Pre-owned asset coefficient first line", readonly=True, store=False),
        'new_asset_coefficient_first_line': fields.related('category_id', 'new_asset_coefficient_first_line', string="N asset coefficient first line", readonly=True, store=False),
    }
    '''
    def _check_percent_number_lines(self, cr, uid, ids, context=None):
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.method == 'percent' and len(asset.percent_ids) != asset.method_number:
                return False
        return True
    
    _constraints = [
        (_check_percent_number_lines, 'Number of Lines must be the same of the method number' , ['method_number']),
    ]'''
    
    def _compute_entries(self, cr, uid, ids, period_id, context=None):
        # remove fiscal assets 
        
        i = 0
        for asset in self.pool.get('account.asset.asset').browse(cr, uid, ids):
            if asset.fiscal:
                ids.pop(i)
            i += 1
        result = []
        period_obj = self.pool.get('account.period')
        depreciation_obj = self.pool.get('account.asset.depreciation.line')
        period = period_obj.browse(cr, uid, period_id, context=context)
        depreciation_ids = depreciation_obj.search(cr, uid, [('asset_id', 'in', ids), ('depreciation_date', '<=', period.date_stop), ('depreciation_date', '>=', period.date_start), ('move_check', '=', False)], context=context)
        return depreciation_obj.create_move(cr, uid, depreciation_ids, context=context)
    
    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        res = super(account_asset, self)._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None)
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = amount_to_depr / asset.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (amount_to_depr / asset.method_number) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
                # Coeff. for first line percents
                if i == 1:
                    if asset.pre_owned == False:
                        amount = amount * asset.category_id.new_asset_coefficient_first_line
                    else:
                        amount = amount * asset.category_id.pre_owned_asset_coefficient_first_line
            elif asset.method == 'degressive':
                amount = residual_amount * asset.method_progress_factor
                if asset.prorata:
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
                # Coeff. for first line percents
                if i == 1:
                    if asset.pre_owned == False:
                        amount = amount * asset.category_id.new_asset_coefficient_first_line
                    else:
                        amount = amount * asset.category_id.pre_owned_asset_coefficient_first_line
            elif asset.method == 'percent':
                period = 1
                for line in asset.percent_ids:
                    if period != i:
                        period += 1
                        continue
                    if line.value:
                        if line.value == 'percent':
                            amount = float(amount_to_depr * line.value_amount)
                        else:
                            amount = residual_amount
                    period += 1
        return amount
    
    def create(self, cr, uid, vals, context=None):
        #import pdb
        #pdb.set_trace()
        if 'purchase_date' in vals:
            vals['start_date'] = vals['purchase_date']
        else:
            vals['start_date'] = datetime.now().strftime('%Y-%m-%d')
        
        asset_id = super(account_asset, self).create(cr, uid, vals, context=None)
        asset_percent_plan_line_obj = self.pool.get('account.asset.percent.plan.line')
        asset_percent_plan_line_fiscal_obj = self.pool.get('account.asset.percent.plan.line.fiscal')
        category_percent_plan_line_obj = self.pool.get('account.asset.category.percent.plan.line')
        # assign same percents of category 
        for asset in self.pool.get('account.asset.asset').browse(cr, uid, [asset_id]):
            # delete old plan
            asset_percent_plan_ids = asset_percent_plan_line_obj.search(cr, uid, [('asset_id', '=', asset.id)])
            if asset_percent_plan_ids:
                asset_percent_plan_line_obj.unlink(cr, uid, asset_percent_plan_ids, context=context)
            asset_percent_plan_fiscal_ids = asset_percent_plan_line_fiscal_obj.search(cr, uid, [('asset_id', '=', asset.id)])
            if asset_percent_plan_fiscal_ids:
                asset_percent_plan_line_fiscal_obj.unlink(cr, uid, asset_percent_plan_fiscal_ids, context=context)
            # New lines form category percents
            if asset.fiscal_method == 'percent':
                nr_line = 1
                category_percent_plan_ids = category_percent_plan_line_obj.search(cr, uid, [('category_id', '=', asset.category_id.id)])
                for category_line in category_percent_plan_line_obj.browse(cr, uid, category_percent_plan_ids, context=context):
                    # Coeff. for first line percents
                    coeff_line = 1
                    if nr_line == 1 and asset.pre_owned == True and asset.category_id.pre_owned_asset_coefficient_first_line != 0:
                        coeff_line = asset.category_id.pre_owned_asset_coefficient_first_line
                    if nr_line == 1 and asset.pre_owned == False and asset.category_id.new_asset_coefficient_first_line != 0:
                        coeff_line = asset.category_id.new_asset_coefficient_first_line
                    asset_vals = { 
                                  'value' : category_line.value,
                                  'value_amount' : category_line.value_amount * coeff_line,
                                  'asset_id' : asset.id,
                                  'sequence' : category_line.sequence
                                  }
                    asset_percent_plan_line_obj.create(cr, uid, asset_vals, context=context)
                    asset_percent_plan_line_fiscal_obj.create(cr, uid, asset_vals, context=context)
                    nr_line += 1
            # re-compute new board
            self.compute_depreciation_board(cr, uid, [asset.id], context=context)
            self.compute_depreciation_board_fiscal(cr, uid, [asset.id], context=context)
        # re-setting method number witn pecent lines 
        for asset in self.browse(cr, uid, [asset_id], context=context):
            if asset.method == 'percent' and len(asset.percent_ids) != asset.method_number and len(asset.percent_ids)>0:
                self.pool.get('account.asset.asset').write(cr, uid, asset.id, {'method_number': len(asset.percent_ids)}, context=context)
        
        return asset_id
        
       
    def onchange_category_id(self, cr, uid, ids, category_id, context=None):
        res = super(account_asset, self).onchange_category_id(cr, uid, ids, category_id, context=None)
        '''
        asset_percent_plan_line_obj = self.pool.get('account.asset.percent.plan.line')
        asset_percent_plan_line_fiscal_obj = self.pool.get('account.asset.percent.plan.line.fiscal')
        category_percent_plan_line_obj = self.pool.get('account.asset.category.percent.plan.line')
        category_percent_plan_ids = category_percent_plan_line_obj.search(cr, uid, [('category_id', '=', category_id)])
        
        # assign same percents of category 
        for asset in self.pool.get('account.asset.asset').browse(cr, uid, ids):
            # delete old plan
            asset_percent_plan_ids = asset_percent_plan_line_obj.search(cr, uid, [('asset_id', '=', asset.id)])
            if asset_percent_plan_ids:
                asset_percent_plan_line_obj.unlink(cr, uid, asset_percent_plan_ids, context=context)
            asset_percent_plan_fiscal_ids = asset_percent_plan_line_fiscal_obj.search(cr, uid, [('asset_id', '=', asset.id)])
            if asset_percent_plan_fiscal_ids:
                asset_percent_plan_line_fiscal_obj.unlink(cr, uid, asset_percent_plan_fiscal_ids, context=context)
            # New lines form category percents
            if res['value']['method'] == 'percent':
                nr_line = 1
                for category_line in category_percent_plan_line_obj.browse(cr, uid, category_percent_plan_ids, context=context):
                    # Coeff. for first line percents
                    if nr_line == 1 and asset.category_id.pre_owned_asset_coefficient_first_line != 0:
                        coeff_line = asset.category_id.pre_owned_asset_coefficient_first_line
                    else:
                        coeff_line = 1
                        
                    asset_vals = {
                                  'value' : category_line.value,
                                  'value_amount' : category_line.value_amount * coeff_line,
                                  'asset_id' : asset.id,
                                  'sequence' : category_line.sequence
                                  }
                    asset_percent_plan_line_obj.create(cr, uid, asset_vals, context=context)
                    asset_percent_plan_line_fiscal_obj.create(cr, uid, asset_vals, context=context)
                    nr_line += 1
            '''
        # Otehr params
        asset_categ_obj = self.pool.get('account.asset.category')
        if category_id:
            category_obj = asset_categ_obj.browse(cr, uid, category_id, context=context)
            res['value']['fiscal_method'] = category_obj.method
            res['value']['fiscal_method_number'] = category_obj.method_number
            res['value']['fiscal_method_time'] = category_obj.method_time
            res['value']['fiscal_method_period'] = category_obj.method_period
            res['value']['fiscal_method_progress_factor'] = category_obj.method_progress_factor
            res['value']['fiscal_method_end'] = category_obj.method_end
            res['value']['fiscal_prorata'] = category_obj.prorata
            '''
            # re-compute new board
            self.compute_depreciation_board(cr, uid, ids, context=context)
            self.compute_depreciation_board_fiscal(cr, uid, ids, context=context)
            '''
        return res
    
    def onchange_fiscal_percent_ids(self, cr, uid, ids, percent_ids, context=None):
        # percents changed
        percents_changed = {}
        for perc in percent_ids:
            if perc[2] != False:
                percents_changed.update({perc[1] : perc[2]['value_amount']})
        # Number of depreciation must be the same of percent lines number
        res ={}
        for asset in self.browse(cr, uid, ids, context=context):
            number_of_lines = len(asset.fiscal_percent_ids)
            self.write(cr, uid, asset.id, {'fiscal_method_number': number_of_lines}, context=context)
            # Sum of perc <= 1
            tot_percent = 0
            for percent in asset.percent_ids:
                if percent.id in percents_changed:
                    tot_percent += percents_changed[percent.id]
                else:
                    tot_percent += percent.value_amount
            if tot_percent > 1:
                raise osv.except_osv(_('Error!'),_("Sum of percents is major than 1"))
        return True
    
    def onchange_percent_ids(self, cr, uid, ids, percent_ids, context=None):
        # percents changed
        percents_changed = {}
        for perc in percent_ids:
            if perc[2] != False:
                percents_changed.update({perc[1] : perc[2]['value_amount']})
        # Number of depreciation must be the same of percent lines number        
        res ={}
        for asset in self.browse(cr, uid, ids, context=context):
            number_of_lines = len(asset.percent_ids)
            self.write(cr, uid, asset.id, {'method_number': number_of_lines}, context=context)
            # Sum of perc <= 1
            tot_percent = 0
            for percent in asset.percent_ids:
                if percent.value == 'percent':
                    if percent.id in percents_changed:
                        tot_percent += percents_changed[percent.id]
                    else:
                        tot_percent += percent.value_amount
            if tot_percent > 1:
                raise osv.except_osv(_('Error!'),_("Sum of percents is major than 1"))
        return True
    
        
    def onchange_progress_factor(self, cr, uid, ids, context=None):
        # to refresh view
        res ={}
        
        return res
    
    def _compute_board_amount_fiscal(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        #by default amount = 0
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.fiscal_method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.fiscal_prorata:
                    amount = amount_to_depr / asset.fiscal_method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (amount_to_depr / asset.fiscal_method_number) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (amount_to_depr / asset.fiscal_method_number) / total_days * (total_days - days)
                # Coeff. for first line percents
                if i == 1:
                    if asset.pre_owned == False:
                        amount = amount * asset.category_id.new_asset_coefficient_first_line
                    else:
                        amount = amount * asset.category_id.pre_owned_asset_coefficient_first_line
            elif asset.fiscal_method == 'degressive':
                amount = residual_amount * asset.fiscal_method_progress_factor
                if asset.fiscal_prorata:
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (residual_amount * asset.fiscal_method_progress_factor) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (residual_amount * asset.fiscal_method_progress_factor) / total_days * (total_days - days)
                # Coeff. for first line percents
                if asset.pre_owned == False:
                    amount = amount * asset.category_id.new_asset_coefficient_first_line
                else:
                    amount = amount * asset.category_id.pre_owned_asset_coefficient_first_line
            elif asset.fiscal_method == 'percent':
                period = 1
                for line in asset.fiscal_percent_ids:
                    if period != i:
                        period += 1
                        continue
                    if line.value:
                        if line.value == 'percent':
                            amount = float(amount_to_depr * line.value_amount)
                        else:
                            amount = residual_amount
                    period += 1
        return amount

    def _compute_board_undone_dotation_nb_fiscal(self, cr, uid, asset, depreciation_date, total_days, context=None):
        undone_dotation_number = asset.fiscal_method_number
        if asset.fiscal_method == 'percent':
            undone_dotation_number = len(asset.fiscal_percent_ids)
        if asset.fiscal_method_time == 'end':
            end_date = datetime.strptime(asset.fiscal_method_end, '%Y-%m-%d')
            undone_dotation_number = 0
            while depreciation_date <= end_date:
                depreciation_date = (datetime(depreciation_date.year, depreciation_date.month, depreciation_date.day) + relativedelta(months=+asset.fiscal_method_period))
                undone_dotation_number += 1
        if asset.fiscal_prorata:
            undone_dotation_number += 1
        return undone_dotation_number
        
    def compute_depreciation_board_fiscal(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line.fiscal')
        currency_obj = self.pool.get('res.currency')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.fiscal_value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.fiscal_value_residual
            if asset.fiscal_prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            else:
                # depreciation_date = 1st January of purchase year
                purchase_date = datetime.strptime(asset.purchase_date, '%Y-%m-%d')
                #if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids[0],context=context).depreciation_date, '%Y-%m-%d')
                    depreciation_date = (last_depreciation_date+relativedelta(months=+asset.fiscal_method_period))
                else:
                    depreciation_date = datetime(purchase_date.year, 1, 1)
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            total_days = (year % 4) and 365 or 366

            undone_dotation_number = self._compute_board_undone_dotation_nb_fiscal(cr, uid, asset, depreciation_date, total_days, context=context)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                i = x + 1
                amount = self._compute_board_amount_fiscal(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                # compute amount into company currency
                amount = currency_obj.compute(cr, uid, current_currency, company_currency, amount, context=context)
                residual_amount -= amount
                vals = {
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount,
                     'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.fiscal_method_period))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True

account_asset()

class account_asset_percent_plan_line(osv.osv):
    _name = "account.asset.percent.plan.line"
    _description = "Asset Percent Plan Line "
    _columns = {
        'value': fields.selection([('percent', 'Percent'),
                                   ('balance', 'Balance')], 'Computation',
                                   required=True, help="""Select here the kind of valuation related to this plan line. Note that you should have your last line with the type 'Balance' to ensure that the whole amount will be treated."""),

        'value_amount': fields.float('Amount', digits_compute=dp.get_precision('Percent'), help="For percent enter a ratio between 0-1."),
        'asset_id': fields.many2one('account.asset.asset', 'Asset', required=True, select=True, ondelete='cascade'),
        'sequence': fields.integer('Sequence', size=64, required=True, help="Gives the sequence order when displaying a list of percent."),
    }
    _defaults = {
        'value': 'balance'
    }
    _order = "sequence"

    def _check_percent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.value == 'percent' and ( obj.value_amount < 0.0 or obj.value_amount > 1.0):
            return False
        return True

    _constraints = [
        (_check_percent, 'Percentages for Line must be between 0 and 1, Example: 0.02 for 2%.', ['value_amount']),
    ]

account_asset_percent_plan_line()

class account_asset_percent_plan_line_fiscal(osv.osv):
    _name = "account.asset.percent.plan.line.fiscal"
    _description = "Asset Percent Plan Line Fiscal "
    _columns = {
        'value': fields.selection([('percent', 'Percent'),
                                   ('balance', 'Balance')], 'Computation',
                                   required=True, help="""Select here the kind of valuation related to this plan line. Note that you should have your last line with the type 'Balance' to ensure that the whole amount will be treated."""),

        'value_amount': fields.float('Amount', digits_compute=dp.get_precision('Percent'), help="For percent enter a ratio between 0-1."),
        'asset_id': fields.many2one('account.asset.asset', 'Asset', required=True, select=True, ondelete='cascade'),
        'sequence': fields.integer('Sequence', size=64, required=True, help="Gives the sequence order when displaying a list of percent."),
    }
    _defaults = {
        'value': 'balance'
    }
    _order = "sequence"

    def _check_percent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.value == 'percent' and ( obj.value_amount < 0.0 or obj.value_amount > 1.0):
            return False
        return True

    _constraints = [
        (_check_percent, 'Percentages for Line must be between 0 and 1, Example: 0.02 for 2%.', ['value_amount']),
    ]
    
account_asset_percent_plan_line_fiscal()


class account_asset_category(osv.osv):
    _name = "account.asset.category"
    _inherit = "account.asset.category"
    
    _columns =  {
        #'fiscal': fields.boolean('Fiscal asset plan'),
        'method': fields.selection([('linear','Linear'),('degressive','Degressive'),('percent','percent')], 'Computation Method', required=True, help="Choose the method to use to compute the amount of depreciation lines.\n"\
            "  * Linear: Calculated on basis of: Gross Value / Number of Depreciations\n" \
            "  * Degressive: Calculated on basis of: Residual Value * Degressive Factor"),
        'percent_ids': fields.one2many('account.asset.category.percent.plan.line', 'category_id', 'Percent Plan Line'),
        'account_gain_id': fields.many2one('account.account', 'Gain Account', required=True),
        'account_loss_id': fields.many2one('account.account', 'Loss Account', required=True),
        'pre_owned_asset_coefficient_first_line': fields.float('coefficient for first line of pre-owned asset'),
        'new_asset_coefficient_first_line': fields.float('coefficient for first line of new asset'),
    }
    _defaults = {
        'pre_owned_asset_coefficient_first_line': 1,
        'new_asset_coefficient_first_line': 2
    }
    
    def _check_percent_number_lines(self, cr, uid, ids, context=None):
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.method == 'percent' and len(asset.percent_ids) != asset.method_number:
                return False
        return True
    
    _constraints = [
        (_check_percent_number_lines, 'Number of Lines must be the same of the method number' , ['method_number']),
    ]
    
    def onchange_method(self, cr, uid, ids, method, context=None):
        '''
        Setting percents with method number/method period
        '''
        result = {'value':{}}
        #import pdb
        #pdb.set_trace()
        if method == 'percent':
            if context.get('method_time') == 'number':
                divisor = context.get('method_number', 1) 
            else:
                divisor = context.get('method_period', 1)
            if divisor > 0:
                percent_line = round(1 / float(divisor), 2)
                percent_lines = []
                percent_residual = 1.0
                seq = 0
                while percent_residual > 0:
                    seq += 1
                    if (percent_residual - percent_line) < 0:
                        value_amount = percent_residual
                        value = 'balance'
                    else:
                        value_amount = percent_line
                        value = 'percent'
                    val = {
                        'sequence' : seq,
                        'value' : value,  
                        'value_amount' : value_amount,  
                        }
                    percent_lines.append(0, 0, val)
                result['value']['percent_ids'] = commission_ids
        return {}
    
account_asset_category()

class account_asset_category_percent_plan_line(osv.osv):
    _name = "account.asset.category.percent.plan.line"
    _description = "Category Asset Percent Plan Line "
    _columns = {
        'value': fields.selection([('percent', 'Percent'),
                                   ('balance', 'Balance')], 'Computation',
                                   required=True, help="""Select here the kind of valuation related to this plan line. Note that you should have your last line with the type 'Balance' to ensure that the whole amount will be treated."""),

        'value_amount': fields.float('Amount', digits_compute=dp.get_precision('Percent'), help="For percent enter a ratio between 0-1."),
        'category_id': fields.many2one('account.asset.category', 'Asset', required=True, select=True, ondelete='cascade'),
        'sequence': fields.integer('Sequence', size=64, required=True, help="Gives the sequence order when displaying a list of percent."),
    }
    _defaults = {
        'value': 'balance'
    }
    _order = "sequence"

    def _check_percent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if obj.value == 'percent' and ( obj.value_amount < 0.0 or obj.value_amount > 1.0):
            return False
        return True

    _constraints = [
        (_check_percent, 'Percentages for Line must be between 0 and 1, Example: 0.02 for 2%.', ['value_amount']),
    ]

account_asset_category_percent_plan_line()

class account_asset_depreciation_line_fiscal(osv.osv):
    _name = 'account.asset.depreciation.line.fiscal'
    _description = 'Asset depreciation line fiscal'

    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        # The limit is the last date of depreciation of civilistic line
        res = {} 
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        for line in self.browse(cr, uid, ids, context=context):
            last_posted_depreciation_line = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', line.asset_id.id), ('move_check', '=', True)], order='depreciation_date desc', limit = 1)
            if len(last_posted_depreciation_line) == 0:
                res[line.id] = False
                break
            last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,last_posted_depreciation_line[0],context=context).depreciation_date, '%Y-%m-%d')
            limit_depreciation_date = last_depreciation_date + relativedelta(months = line.asset_id.fiscal_method_period)
            fiscal_depreciation_date = datetime.strptime(line.depreciation_date, '%Y-%m-%d')
            if fiscal_depreciation_date <= limit_depreciation_date:
                res[line.id] = True
            else:
                res[line.id] = False
        return res

    _columns = {
        'name': fields.char('Depreciation Name', size=64, required=True, select=1),
        'sequence': fields.integer('Sequence', required=True),
        'asset_id': fields.many2one('account.asset.asset', 'Asset', required=True),
        'parent_state': fields.related('asset_id', 'state', type='char', string='State of Asset'),
        'amount': fields.float('Current Depreciation', digits_compute=dp.get_precision('Account'), required=True),
        'remaining_value': fields.float('Next Period Depreciation', digits_compute=dp.get_precision('Account'),required=True),
        'depreciated_value': fields.float('Amount Already Depreciated', required=True),
        'depreciation_date': fields.date('Depreciation Date', select=1),
        'move_id': fields.many2one('account.move', 'Depreciation Entry'),
        'move_check': fields.function(_get_move_check, method=True, type='boolean', string='Posted', store=True)
    }
    
account_asset_depreciation_line_fiscal()

class account_asset_italian_group(osv.osv):
    _name = "account.asset.italian.group"
    _description = "Asset Group italian Fiscal "
    _columns = {
        'name': fields.char('Group name', size=64, required=True, select=1),
        'code': fields.char('Group code', size=64),
    }
    _order = "code"
account_asset_italian_group()

class account_asset_italian_species(osv.osv):
    _name = "account.asset.italian.species"
    _description = "Asset Species italian Fiscal "
    _columns = {
        'name': fields.char('Group name', size=64, required=True, select=1),
        'code': fields.char('Group code', size=64),
        'group_id': fields.many2one('account.asset.italian.group', 'Parent Asset group', 
                readonly=True),
    }
    _order = "code"
account_asset_italian_species()

class account_asset_italian_type(osv.osv):
    _name = "account.asset.italian.type"
    _description = "Asset type italian Fiscal "
    _columns = {
        'name': fields.char('Type name', size=64, required=True, select=1),
        'species_id': fields.many2one('account.asset.italian.species', 'Parent Asset species', 
                readonly=True),
    }
    _order = "name"
account_asset_italian_type()
