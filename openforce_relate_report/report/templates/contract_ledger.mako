## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .overflow_ellipsis {
                text-overflow: ellipsis;
                overflow: hidden;
                white-space: nowrap;
            }

            ${css}
        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)
        %>

        <%setLang(user.lang)%>

        <%
        initial_balance_text = {'initial_balance': _('Computed'), 'opening_balance': _('Opening Entries'), False: _('No')}
        %>

        ##<div class="act_as_table data_table">
        ##    <div class="act_as_row labels">
                ##<div class="act_as_cell">${_('Chart of Account')}</div>
                ##<div class="act_as_cell">${_('Fiscal Year')}</div>
        ##        <div class="act_as_cell">
                    ##%if filter_form(data) == 'filter_date':
        ##                ${_('Dates Filter')}
                    ##%else:
                    ##    ${_('Periods Filter')}
                    ##%endif
                    
        ##        </div>
        ##        <div class="act_as_cell">${_('Accounts Filter')}</div>
        ##        <div class="act_as_cell">${_('Initial Balance')}</div>
        ##        <div class="act_as_cell">${_('Target Moves')}</div>
        ##    </div>
        ##    <div class="act_as_row">
                ##<div class="act_as_cell">${ chart_account.name }</div>
                ##<div class="act_as_cell">${ fiscalyear.name if fiscalyear else '-' }</div>
        ##        <div class="act_as_cell">
        ##            ${_('From:')}
                    ##%if filter_form(data) == 'filter_date' :
        ##                ${formatLang(start_date, date=True) if start_date else u'' }
                    ##%else:
                    ##    ${start_period.name if start_period else u'' }
                    ##%endif
        ##            ${_('To:')}
                    ##%if filter_form(data) == 'filter_date':
        ##                ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    ##%else:
                    ##    ${stop_period.name if stop_period else u'' }
                    ##%endif
        ##        </div>
        ##        <div class="act_as_cell">
        ##            %if partner_ids:
        ##                ${_('Custom Filter')}
        ##            %else:
        ##                ${ display_partner_account(data) }
        ##            %endif
        ##        </div>
        ##        <div class="act_as_cell">${ display_target_move(data) }</div>
                ##<div class="act_as_cell">${ initial_balance_text[initial_balance_mode] }</div>
        ##        <div class="act_as_cell">${ _(' DA VEDERE initial_balance_text') }</div>
        ##    </div>
        ##</div>
    
        %for contract in objects:
            ##%if account.ledger_lines or account.init_balance:
            %if contract.ledger_lines:
                <%
                if not contract.elements_order:
                    continue
                account_total_invoiced = 0.0
                account_total_value = 0.0
                account_total_cost = 0.0
                account_balance_cumul = 0.0
                account_balance_cumul_curr = 0.0
                %>

                ##<div class="account_title bg" style="width: 1080px; margin-top: 20px; font-size: 12px;">${account.code} - ${account.name}</div>
                <div class="account_title bg" style="width: 1080px; margin-top: 24px; font-size: 16px;">${contract.name or ''} </div>
                <div class="account_title bg" style="width: 1080px; font-size: 12px;">${ _('Partner ')} ${contract.partner_id.name or ''} </div>

                ##%for partner_name, p_id, p_ref, p_name in account.elements_order:
                %for line_id, line_name in contract.elements_order:
                <%
                  total_invoiced = 0.0
                  total_value = 0.0
                  total_cost = 0.0
                  cumul_balance = 0.0
                  cumul_balance_curr = 0.0

                  part_cumul_balance = 0.0
                  part_cumul_balance_curr = 0.0
                %>
                <div class="act_as_table list_table" style="margin-top: 5px;">
                    <div class="act_as_caption account_title">
                        ##${partner_name or _('No Partner')}
                        ${line_name or _('No Journal')}
                    </div>
                    <div class="act_as_thead">
                        <div class="act_as_row labels">
                            ## journal
                            <div class="act_as_cell" style="width: 50px;">${_('Journal')}</div>
                            ## date
                            <div class="act_as_cell first_column" style="width: 50px;">${_('Date')}</div>
                            ## user
                            <div class="act_as_cell" style="width: 50px;">${_('User')}</div>
                            ## number
                            <div class="act_as_cell" style="width: 60px;">${_('Number')}</div>
                            ## Qty
                            <div class="act_as_cell amount" style="width: 60px;">${_('Quantity')}</div>
                            ## Um
                            <div class="act_as_cell" style="width: 30px;">${_('Uom')}</div>
                            ## label
                            <div class="act_as_cell" style="width: 180px;">${_('Label')}</div>
                            ## Partner
                            %if display_partner(data):
                                <div class="act_as_cell" style="width: 80px;">${_('Partner')}</div>
                            %endif
                            ## label 2 
                            <div class="act_as_cell" style="width: 100px;">${_('')}</div>
                            ## Invoiced
                            %if display_invoiced(data):
                                <div class="act_as_cell amount" style="width: 60px;">${_('Invoiced')}</div>
                            %endif
                            ## Value (to invoice)
                            %if display_price(data):
                                <div class="act_as_cell amount" style="width: 60px;">${_('Value')}</div>
                            %endif
                            ## cost
                            %if display_cost(data):
                                <div class="act_as_cell amount" style="width: 60px;">${_('Cost')}</div>
                            %endif
                            ## balance
                            %if display_cost(data):
                                <div class="act_as_cell amount" style="width: 60px;">${_('Cumul. Bal.')}</div>
                            %endif
                            
                        </div>
                    </div>
                    <div class="act_as_tbody">

                        %for line in contract.ledger_lines.get(line_id, []):
                          <%
                          ## da vedere per ora sia credito che debito metto amount
                          ##total_credit += line.get('credit') or 0.0
                          ##total_debit += line.get('debit') or 0.0
                          total_invoiced += line.get('line_amount_invoiced') or 0.0
                          total_value += line.get('line_amount_to_invoice') or 0.0
                          total_cost += line.get('line_amount') or 0.0

                          label_elements = [line.get('line_name') or '']
                          if line.get('invoice_number'):
                            label_elements.append("(%s)" % (line['invoice_number'],))
                          label = ' '.join(label_elements)
                          %>
                            <div class="act_as_row lines">
                              ## journal
                              <div class="act_as_cell">${line.get('j_name') or ''}</div>
                              ## date
                              <div class="act_as_cell first_column">${formatLang(line.get('line_date') or '', date=True)}</div>
                              ## User
                              <div class="act_as_cell overflow_ellipsis">${line.get('user_name') or ''}</div>
                              ## Number
                              <div class="act_as_cell overflow_ellipsis">${line.get('number') or ''}</div>
                              ## Qty
                              <div class="act_as_cell amount">${formatLang(line.get('line_qty') or 0.0) | amount }</div>
                              ## Uom
                              <div class="act_as_cell">${line.get('line_uom_name') or ''}</div>
                              ## label
                              <div class="act_as_cell">${line.get('line_name') or ''}</div>
                              ## Partner
                              %if display_partner(data):
                                <div class="act_as_cell">${line.get('move_partner_name') or''}</div>
                              %endif
                              ## label 2 
                              <div class="act_as_cell">${line.get('product_to_invoice_name') or ''} ${line.get('account_move_desc') or ''}</div>
                              ## Invoiced
                              %if display_invoiced(data):
                                <div class="act_as_cell amount">${formatLang(line.get('line_amount_invoiced') or 0.0) | amount }</div>
                              %endif
                              ## value
                              %if display_price(data):
                                <div class="act_as_cell amount">${formatLang(line.get('line_amount_to_invoice') or 0.0) | amount }</div>
                              %endif
                              ## cost
                              %if display_cost(data):
                                <div class="act_as_cell amount">${formatLang(line.get('line_amount') or 0.0) | amount }</div>
                              %endif
                              ## balance
                              %if display_cost(data):
                                <div class="act_as_cell amount">${formatLang(line.get('line_balance') or 0.0) | amount }</div>
                              %endif
                              ## balance cumulated
                              <% cumul_balance += line.get('line_balance') or 0.0 %>
                              
                          </div>
                        %endfor
                        <div class="act_as_row lines labels">
                          ## journal
                          <div class="act_as_cell"></div>
                          ## date
                          <div class="act_as_cell first_column"></div>
                          ## user
                          <div class="act_as_cell"></div>
                          ## Number
                          <div class="act_as_cell"></div>
                          ## qty
                          <div class="act_as_cell"></div>
                          ## uom
                          <div class="act_as_cell"></div>
                          ## label
                          <div class="act_as_cell">${_('Cumulated Balance on Journal')}</div>
                          ## Partner
                          %if display_partner(data):
                            <div class="act_as_cell"></div>
                          %endif 
                          ## label 2 (vehicle)
                          <div class="act_as_cell"></div>
                          ## Invoiced
                          %if display_invoiced(data):
                            <div class="act_as_cell amount">${formatLang(total_invoiced) | amount }</div>
                          %endif
                          ## Value
                          %if display_price(data):
                            <div class="act_as_cell amount">${formatLang(total_value) | amount }</div>
                          %endif  
                          ## cost
                          %if display_cost(data):
                            <div class="act_as_cell amount">${formatLang(total_cost) | amount }</div>
                          %endif
                          ## balance cumulated
                          %if display_cost(data):
                            <div class="act_as_cell amount" style="padding-right: 1px;">${formatLang(cumul_balance) | amount }</div>
                          %endif
                      </div>
                    </div>
                </div>
                <%
                    account_total_invoiced += total_invoiced
                    account_total_value += total_value
                    account_total_cost += total_cost
                    account_balance_cumul += cumul_balance
                    account_balance_cumul_curr += cumul_balance_curr
                %>
                %endfor

                <div class="act_as_table list_table" style="margin-top:5px;">
                    <div class="act_as_row labels" style="font-weight: bold; font-size: 10px;">
                            <div class="act_as_cell first_column" style="width: 320px;">${contract.name or ''}</div>
                            ## label
                            <div class="act_as_cell" style="width: 350px;">${_("Cumulated Balance on Contract")}</div>
                            ## invoiced
                            %if display_invoiced(data):
                                <div class="act_as_cell amount" style="width: 60px;">${ formatLang(account_total_invoiced) | amount }</div>
                            %endif
                            ## value
                            %if display_price(data):
                                <div class="act_as_cell amount" style="width: 60px;">${ formatLang(account_total_value) | amount }</div>
                            %endif
                            ## cost
                            %if display_cost(data):
                                <div class="act_as_cell amount" style="width: 60px;">${ formatLang(account_total_cost) | amount }</div>
                            %endif
                            ## balance cumulated
                            %if display_cost(data):
                                <div class="act_as_cell amount" style="width: 60px; padding-right: 1px;">${ formatLang(account_balance_cumul) | amount }</div>
                            %endif
                        </div>
                    </div>
                </div>
            %endif
        %endfor
    </body>
</html>
