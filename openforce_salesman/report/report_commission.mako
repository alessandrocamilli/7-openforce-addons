<html>
<head>
    <style type="text/css">
    body, table, td, span, div {
    	font-family: Helvetica, Arial;
    	font-size:8px;
		}
    	.left_with_line {
            text-align:left; vertical-align:text-top; border-top:1px solid #000; padding:3px
        }
        .right_with_line {
            text-align:right; vertical-align:text-top; border-top:1px solid #000; padding:3px
        }
        .left_without_line {
            text-align:left; vertical-align:text-top; padding:2px
        }
        .right_without_line {
            text-align:right; vertical-align:text-top; padding:2px
        }
        .text_right{
        	text-align:right;
        }
        .text_left{
        	text-align:left;
        }
        
        .col_central {
            width:20px;
        }
        
        .page-break {
    		page-break-after: always;
		}
		.account {
			height: 10px;
		}
		.account_type_view {
            font-weight:bold;
        }
        
        th.line {
        	 border-bottom:1px solid #000;
        	 padding: 3px;
        }
        .line {
        	 border-bottom:1px solid #E6E6E6;
        	 padding: 3px;
        }
		
		.box_titolo{
			width:100%; 
			height:25px; 
			text-align:center;
		}
		
    </style>
</head>
<body>


<%
date_from = data["form"]["date_from"]
date_to = data["form"]["date_to"]
%>
	
    
    <%
    ##
    ## STATO PATRIMONIALE
    ##
    attivita_rows = attivita(object)
    passivita_rows = passivita(object)
    
    numero_passivita = len(passivita_rows)
    numero_attivita = len(attivita_rows)
    numero_stato_patrimoniale = 0
    
    if numero_attivita > numero_passivita :
    	numero_stato_patrimoniale = numero_attivita
    else :
    	numero_stato_patrimoniale = numero_passivita
    endif
    
    totale_attivo = 0
    totale_passivo = 0
    %>
    
    <div class="box_titolo"><h1>STATO PATRIMONIALE</h1></div>
    
    <table style="width:100%;" cellspacing="0">
        <thead>
        <tr>
            <th class="text_left line">Codice</th>
            <th class="text_left line">Conto</th>
            <th class="text_right line">Saldo</th>
            <th class="col_central"></th>
            <th class="text_left line">Codice</th>
            <th class="text_left line">Conto</th>
            <th class="text_right line">Saldo</th>
        </tr>
        </thead>
        <tbody>
        <% riga = 1 %>
        <% ind = 0 %>
         
        %for riga in range(1, numero_stato_patrimoniale +1) :
        	<% ind = riga - 1 %>
        	<tr>
        	%if riga <= numero_attivita:
        		<%
        		# totali solo su conti ( no view)
           		if attivita_rows[ind]['type'] <> "view":
        			totale_attivo += attivita_rows[ind]['balance']
        		
        		class_account=""
        		if attivita_rows[ind]['type'] == "view":
        			class_account = "account_type_view"
        		else:
        			class_account = "account"
        		%>
	        	<td class="text_left line ${class_account}">${ attivita_rows[ind]['code'] | entity} </td>
	        	<td class="text_left line ${class_account}">${ attivita_rows[ind]['name'] | entity}</td>
	        	<td class="text_right line ${class_account}">${ formatLang(attivita_rows[ind]['balance'], digits=get_digits(dp='Account')) |entity }</td>
	        	<td class="col_central"></td>
            %else:
            	<td class="text_left line"></td>
	        	<td class="text_left line"></td>
	        	<td class="text_right line"></td>
	        	<td class="col_central"></td>
            %endif
            
           	%if riga <= numero_passivita:
           		<%
           		if passivita_rows[ind]['balance'] <> 0:
           			passivita_rows[ind]['balance'] = passivita_rows[ind]['balance'] * -1
           		# totali solo su conti ( no view)
           		if passivita_rows[ind]['type'] <> "view":
           			totale_passivo += passivita_rows[ind]['balance']
           		
        		class_account=""
        		if passivita_rows[ind]['type'] == "view":
        			class_account = "account_type_view"
        		else:
        			class_account = "account"
        		%>
	        	<td class="text_left line ${class_account}">${ passivita_rows[ind]['code'] | entity} </td>
	        	<td class="text_left line ${class_account}">${ passivita_rows[ind]['name'] | entity}</td>
	        	<td class="text_right line ${class_account}">${ formatLang(passivita_rows[ind]['balance'], digits=get_digits(dp='Account')) |entity }</td>
            %else:
            	<td class="text_left line"></td>
	        	<td class="text_left line"></td>
	        	<td class="text_right line"></td>
	            <td></td>
            %endif
            
            </tr>
        %endfor
     		<tr>
        		<td class="text_left line "></td>
	        	<td class="text_right line account_type_view"></td>
	        	<td class="text_right line account_type_view"></td>
	        	<td class="col_central"></td>
	        	<td class="text_left line "></td>
	        	<td class="text_right line account_type_view"></td>
	        	<td class="text_right line account_type_view"></td>
        	</tr>
        
        	<tr>
        		<td class="text_left line "></td>
	        	<td class="text_right line account_type_view">${ 'Totale '}</td>
	        	<td class="text_right line account_type_view">${ formatLang(totale_attivo, digits=get_digits(dp='Account')) |entity }</td>
	        	<td class="col_central"></td>
	        	
	        	<td class="text_left line "></td>
	        	<td class="text_right line account_type_view">${ 'Totale '}</td>
	        	<td class="text_right line account_type_view">${ formatLang(totale_passivo, digits=get_digits(dp='Account')) |entity }</td>
        	</tr>
   
        
        %if totale_attivo < totale_passivo:
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view">${ 'Differenza '}</td>
        	<td class="text_right line account_type_view">${ formatLang(totale_passivo - totale_attivo, digits=get_digits(dp='Account')) |entity }</td>
        	<td class="col_central"></td>
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view"></td>
        	<td class="text_right line account_type_view"></td>
        %else:
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view"></td>
        	<td class="text_right line account_type_view"></td>
        	<td class="col_central"></td>
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view">${ 'Differenza '}</td>
        	<td class="text_right line account_type_view">${ formatLang(totale_attivo - totale_passivo, digits=get_digits(dp='Account')) |entity }</td>
        %endif
        	
        </tbody>
    </table>
    
    
    
        
    <%
    ##
    ## PROFITTI E PERDITE
    ##
    tipo_report = "PROF"
    
    
    ricavi_rows = ricavi(object)
    costi_rows = costi(object)
    
    numero_costi = len(costi_rows)
    numero_ricavi = len(ricavi_rows)
    numero_profitti_perdite = 0
    
    if numero_costi > numero_ricavi :
    	numero_profitti_perdite = numero_costi
    else :
    	numero_profitti_perdite = numero_ricavi
    endif
    
    totale_costi = 0
    totale_ricavi = 0
    
    %>
    <div class="page-break">&nbsp;</div>
    <div class="box_titolo"><h1>PROFITTI E PERDITE</h1></div>
    
    <table style="width:100%;" cellspacing="0">
        <thead>
        <tr>
            <th class="text_left line">Codice</th>
            <th class="text_left line">Conto</th>
            <th class="text_right line">Saldo</th>
            <th class="col_central"></th>
            <th class="text_left line">Codice</th>
            <th class="text_left line">Conto</th>
            <th class="text_right line">Saldo</th>
        </tr>
        </thead>
        <tbody>
        <% riga = 1 %>
        <% ind = 0 %>
         
        %for riga in range(1, numero_profitti_perdite +1) :
        	<% ind = riga - 1 %>
        	<tr>
        	%if riga <= numero_costi:
        		<%
        		# totali solo su conti ( no view)
           		if costi_rows[ind]['type'] <> "view":
        			totale_costi += costi_rows[ind]['balance']
        		
        		class_account=""
        		if costi_rows[ind]['type'] == "view":
        			class_account = "account_type_view"
        		else:
        			class_account = "account"
        		%>
	        	<td class="text_left line ${class_account}">${ costi_rows[ind]['code'] | entity} </td>
	        	<td class="text_left line ${class_account}">${ costi_rows[ind]['name'] | entity}</td>
	        	<td class="text_right line ${class_account}">${ formatLang(costi_rows[ind]['balance'], digits=get_digits(dp='Account')) |entity }</td>
	        	<td class="col_central"></td>
            %else:
            	<td class="text_left line"></td>
	        	<td class="text_left line"></td>
	        	<td class="text_right line"></td>
	        	<td class="col_central"></td>
            %endif
            
           	%if riga <= numero_ricavi:
           		<%
           		if ricavi_rows[ind]['balance'] <> 0:
           			ricavi_rows[ind]['balance'] = ricavi_rows[ind]['balance'] * -1
           		
           		# totali solo su conti ( no view)
           		if ricavi_rows[ind]['type'] <> "view":
           			totale_ricavi += ricavi_rows[ind]['balance']
           		
        		class_account=""
        		if ricavi_rows[ind]['type'] == "view":
        			class_account = "account_type_view"
        		else:
        			class_account = "account"
        		%>
	        	<td class="text_left line ${class_account}">${ ricavi_rows[ind]['code'] | entity} </td>
	        	<td class="text_left line ${class_account}">${ ricavi_rows[ind]['name'] | entity}</td>
	        	<td class="text_right line ${class_account}">${ formatLang(ricavi_rows[ind]['balance'], digits=get_digits(dp='Account')) |entity }</td>
            %else:
            	<td class="text_left line"></td>
	        	<td class="text_left line"></td>
	        	<td class="text_right line"></td>
	            <td></td>
            %endif
            
            </tr>
        %endfor

        	<tr>
        		<td class="text_left line "></td>
	        	<td class="text_right line account_type_view"></td>
	        	<td class="text_right line account_type_view"></td>
	        	<td class="col_central"></td>
	        	<td class="text_left line "></td>
	        	<td class="text_right line account_type_view"></td>
	        	<td class="text_right line account_type_view"></td>
        	</tr>
        	
        	<tr>
        		<td class="text_left line "></td>
	        	<td class="text_right line account_type_view">${ 'Totale '}</td>
	        	<td class="text_right line account_type_view">${ formatLang(totale_costi, digits=get_digits(dp='Account')) |entity }</td>
	        	<td class="col_central"></td>
	        	
	        	<td class="text_left line "></td>
	        	<td class="text_right line account_type_view">${ 'Totale '}</td>
	        	<td class="text_right line account_type_view">${ formatLang(totale_ricavi, digits=get_digits(dp='Account')) |entity }</td>
        	</tr>
        	
        
        %if totale_costi < totale_ricavi:
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view">${ 'Differenza '}</td>
        	<td class="text_right line account_type_view">${ formatLang(totale_ricavi - totale_costi, digits=get_digits(dp='Account')) |entity }</td>
        	<td class="col_central"></td>
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view"></td>
        	<td class="text_right line account_type_view"></td>
        %else:
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view"></td>
        	<td class="text_right line account_type_view"></td>
        	<td class="col_central"></td>
        	<td class="text_left line "></td>
        	<td class="text_right line account_type_view">${ 'Differenza '}</td>
        	<td class="text_right line account_type_view">${ formatLang(totale_costi - totale_ricavi, digits=get_digits(dp='Account')) |entity }</td>
        %endif
        
        </tbody>
    </table>
    
</body>
</html>