<html>
<head>
    <style type="text/css">
    </style>
</head>
<body>

<h2>TEST</h2>
<p>
${test}
</p>

	<table style="width:100%;" cellspacing="0">
        <thead>
        <tr>
            <th class="left_without_line">Ragione sociale</th>
            <th class="left_without_line">Localita</th>
            <th class="left_without_line">Provincia</th>
            <th class="left_without_line">Indirizzo</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <% counter = 0 %>
        %for line in partners(object) :
        	<tr>
        	<td class="left_with_line">${ line['name'] | entity}</th>
        	<td class="left_with_line"> </th>
        	<td class="left_with_line"> </th>
        	<td class="left_with_line"> </th>
            <td></td>
            </tr>
        %endfor
        </tbody>
    </table>
    
    <table style="width:100%;" cellspacing="0">
        <thead>
        <tr>
            <th class="left_without_line">Ragione sociale</th>
            <th class="left_without_line">Localita</th>
            <th class="left_without_line">Provincia</th>
            <th class="left_without_line">Indirizzo</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        <% counter = 0 %>
        %for account in accounts(object) :
        	<tr>
        	<td class="left_with_line">${ account['name'] | entity}</th>
        	<td class="left_with_line"> </th>
        	<td class="left_with_line"> </th>
        	<td class="left_with_line"> </th>
            <td></td>
            </tr>
        %endfor
        </tbody>
    </table>
    
</body>
</html>