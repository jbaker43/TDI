<html>
<head>
	<title>Census Bureau API</title>
</head>
<body>

	<?php
		$stateID = $_POST['stateID'];
		$countyID = $_POST['countyID'];
		#$apiCall_2016 = $_POST['apiCall_2016'];

		#$stateID += " 55";
		#$apiCall_2016 = "https://api.census.gov/data/2016/acs/acs5?get=NAME,B23006_002E,B23006_003E,B23006_009E,B23006_010E,B23006_016E,B23006_017E,B23006_023E,B23006_024E&for=county:".$countyID."&in=state:".$stateID;

		#echo $stateID;
		#echo $countyID;
		#echo $apiCall_2016;

		$input = array('a' => $stateID);

		echo $stateID;
		echo json_encode($stateID);
		echo json_encode($countyID);
		echo json_encode($input);
		echo json_encode($input['a']);

		echo "<tr><th>Year</th><th>No School</th><th>No School [In Labor Force]</th><th>High School [or equivalent]</th><th>High School [In Labor Force]</th><th>SC/AA</th><th>SC/AA [In Labor Force</th><th>Bachelor's [or higher]</th><th>Bachelor's [In Labor Force]</th><th>EDU Total</th><th>EDU Total [In Labor Force]</th></tr>";
	?>
	<tr><th>Year</th><th>No School</th><th>No School [In Labor Force]</th><th>High School [or equivalent]</th><th>High School [In Labor Force]</th><th>SC/AA</th><th>SC/AA [In Labor Force</th><th>Bachelor's [or higher]</th><th>Bachelor's [In Labor Force]</th><th>EDU Total</th><th>EDU Total [In Labor Force]</th></tr>

</body>
</html>
