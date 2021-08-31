<!DOCTYPE html>
<!--
		Author: Ryan Mosley
		Date:	Feburary 23, 2021
		File:	TDI 1_0.php
		Purpose: The core API function and mathematical algorithm of the TDI website.
-->


<html>
<head>
	<title>Census Bureau API</title>
	<link rel = "stylesheet" href = "style.css">
</head>
<body>

	<?php
		#Key for Census Bureau API
		$apiKey = "c549b7bd88219067147888ce2524f3209da2a870";

		#Census Bureau API call for information
		$apiCall_2016 = "https://api.census.gov/data/2016/acs/acs5?get=NAME,B23006_002E,B23006_003E,B23006_009E,B23006_010E,B23006_016E,B23006_017E,B23006_023E,B23006_024E&for=county:065&in=state:47";

		$apiCall_2017 = "https://api.census.gov/data/2017/acs/acs5?get=NAME,B23006_002E,B23006_003E,B23006_009E,B23006_010E,B23006_016E,B23006_017E,B23006_023E,B23006_024E&for=county:065&in=state:47";

		$apiCall_2018 = "https://api.census.gov/data/2018/acs/acs5?get=NAME,B23006_002E,B23006_003E,B23006_009E,B23006_010E,B23006_016E,B23006_017E,B23006_023E,B23006_024E&for=county:065&in=state:47";

		$apiCall_2019 = "https://api.census.gov/data/2019/acs/acs5?get=NAME,B23006_002E,B23006_003E,B23006_009E,B23006_010E,B23006_016E,B23006_017E,B23006_023E,B23006_024E&for=county:065&in=state:47";

		#-----------------------------------------------------------------

		#Opens API 2016 information for reading
		$data2016 = fopen($apiCall_2016, "r");

		#Saves data from 2016 call to json variable
		$data2016Stream = stream_get_contents($data2016);
		fclose($data2016);

		#Decodes 2016 json data into string array
		$data_2016 = json_decode($data2016Stream, true);

		#-----------------------------------------------------------------

		#Opens API 2017 information for reading
		$data2017 = fopen($apiCall_2017, "r");

		#Saves data from 2017 call to json variable
		$data2017Stream = stream_get_contents($data2017);
		fclose($data2017);

		#Decodes 2017 json data into string array
		$data_2017 = json_decode($data2017Stream, true);

		#-----------------------------------------------------------------

		#Opens API 2018 information for reading
		$data2018 = fopen($apiCall_2018, "r");

		#Saves data from 2018 call to json variable
		$data2018Stream = stream_get_contents($data2018);
		fclose($data2018);

		#Decodes 2018 json data into string array
		$data_2018 = json_decode($data2018Stream, true);

		#-----------------------------------------------------------------

		#Opens API 2019 information for reading
		$data2019 = fopen($apiCall_2019, "r");

		#Saves data from 2019 call to json variable
		$data2019Stream = stream_get_contents($data2019);
		fclose($data2019);

		#Decodes 2019 json data into string array
		$data_2019 = json_decode($data2019Stream, true);

		#-----------------------------------------------------------------

		#Saves table name (County, State)
		$name = $data_2016[1][0];

		#Converts 2016 string array variables to int
		$ns_2016 =     intval($data_2016[1][1]);
		$ns_ilf_2016 = intval($data_2016[1][2]);
		$hs_2016 =     intval($data_2016[1][3]);
		$hs_ilf_2016 = intval($data_2016[1][4]);
		$sc_2016 =     intval($data_2016[1][5]);
		$sc_ilf_2016 = intval($data_2016[1][6]);
		$bs_2016 =     intval($data_2016[1][7]);
		$bs_ilf_2016 = intval($data_2016[1][8]);

		$edu_total_2016 = $hs_2016 + $sc_2016 + $bs_2016;
		$edu_total_ilf_2016 = $hs_ilf_2016 + $sc_ilf_2016 + $bs_ilf_2016;

		#-----------------------------------------------------------------

		#Converts 2017 string array variables to int
		$ns_2017 =     intval($data_2017[1][1]);
		$ns_ilf_2017 = intval($data_2017[1][2]);
		$hs_2017 =     intval($data_2017[1][3]);
		$hs_ilf_2017 = intval($data_2017[1][4]);
		$sc_2017 =     intval($data_2017[1][5]);
		$sc_ilf_2017 = intval($data_2017[1][6]);
		$bs_2017 =     intval($data_2017[1][7]);
		$bs_ilf_2017 = intval($data_2017[1][8]);

		$edu_total_2017 = $hs_2017 + $sc_2017 + $bs_2017;
		$edu_total_ilf_2017 = $hs_ilf_2017 + $sc_ilf_2017 + $bs_ilf_2017;

		#-----------------------------------------------------------------

		#Converts 2018 string array variables to int
		$ns_2018 =     intval($data_2018[1][1]);
		$ns_ilf_2018 = intval($data_2018[1][2]);
		$hs_2018 =     intval($data_2018[1][3]);
		$hs_ilf_2018 = intval($data_2018[1][4]);
		$sc_2018 =     intval($data_2018[1][5]);
		$sc_ilf_2018 = intval($data_2018[1][6]);
		$bs_2018 =     intval($data_2018[1][7]);
		$bs_ilf_2018 = intval($data_2018[1][8]);

		$edu_total_2018 = $hs_2018 + $sc_2018 + $bs_2018;
		$edu_total_ilf_2018 = $hs_ilf_2018 + $sc_ilf_2018 + $bs_ilf_2018;

		#-----------------------------------------------------------------

		#Converts 2018 string array variables to int
		$ns_2019 =     intval($data_2019[1][1]);
		$ns_ilf_2019 = intval($data_2019[1][2]);
		$hs_2019 =     intval($data_2019[1][3]);
		$hs_ilf_2019 = intval($data_2019[1][4]);
		$sc_2019 =     intval($data_2019[1][5]);
		$sc_ilf_2019 = intval($data_2019[1][6]);
		$bs_2019 =     intval($data_2019[1][7]);
		$bs_ilf_2019 = intval($data_2019[1][8]);

		$edu_total_2019 = $hs_2019 + $sc_2019 + $bs_2019;
		$edu_total_ilf_2019 = $hs_ilf_2019 + $sc_ilf_2019 + $bs_ilf_2019;

		#-----------------------------------------------------------------

		#Does the calculations needed for the prediction algorithm
		/*
		$ns_pred_2019 =     ($ns_2016 + $ns_2017 + $ns_2018) / 3;
		$ns_pred_2019 =     round($ns_pred_2019, 0);

		$ns_ilf_pred_2019 = ($ns_ilf_2016 + $ns_ilf_2017 + $ns_ilf_2018) /3;
		$ns_ilf_pred_2019 = round($ns_ilf_pred_2019, 0);

		$hs_pred_2019 =     ($hs_2016 + $hs_2017 + $hs_2018) / 3;
		$hs_pred_2019 =     round($hs_pred_2019, 0);

		$hs_ilf_pred_2019 = ($hs_ilf_2016 + $hs_ilf_2017 + $hs_ilf_2018) / 3;
		$hs_ilf_pred_2019 = round($hs_ilf_pred_2019, 0);

		$sc_pred_2019 =     ($sc_2016 + $sc_2017 + $sc_2018) / 3;
		$sc_pred_2019 =     round($sc_pred_2019, 0);

		$sc_ilf_pred_2019 = ($sc_ilf_2016 + $sc_ilf_2017 + $sc_ilf_2018) / 3;
		$sc_ilf_pred_2019 = round($sc_ilf_pred_2019, 0);

		$bs_pred_2019 =     ($bs_2016 + $bs_2017 + $bs_2018) / 3;
		$bs_pred_2019 =     round($bs_pred_2019, 0);

		$bs_ilf_pred_2019 = ($bs_ilf_2016 + $bs_ilf_2017 + $bs_ilf_2018) / 3;
		$bs_ilf_pred_2019 = round($bs_ilf_pred_2019, 0);
		*/
		$edu_total_pred_2019 = ($edu_total_2016 + $edu_total_2017 + $edu_total_2018) / 3;
		$edu_total_pred_2019 = round($edu_total_pred_2019, 0);

		$edu_total_ilf_pred_2019 = ($edu_total_ilf_2016 + $edu_total_ilf_2017 + $edu_total_ilf_2018) / 3;
		$edu_total_ilf_pred_2019 = round($edu_total_ilf_pred_2019, 0);

		#-----------------------------------------------------------------

		$total_predict = array($edu_total_2017, $edu_total_2018, $edu_total_pred_2019);
		$total_predict_ilf = array($edu_total_ilf_2017, $edu_total_ilf_2018, $edu_total_ilf_pred_2019);

		#-----------------------------------------------------------------

		#prints the raw output of the algorithm in a HTML table
		print("<h1>$name</hr>");
		print("<table>");
		print("<tr><th>Year</th><th>No School</th><th>No School<br>[In Labor Force]</th><th>High School<br>[or equivalent]</th><th>High School<br>[In Labor Force]</th><th>SC/AA</th><th>SC/AA<br>[In Labor Force</th><th>Bachelor's<br>[or higher]</th><th>Bachelor's<br>[In Labor Force]</th><th>EDU Total</th><th>EDU Total<br>[In Labor Force]</th></tr>");
		print("<tr><td>2016 Actual</td><td>$ns_2016</td><td>$ns_ilf_2016</td><td>$hs_2016</td><td>$hs_ilf_2016</td><td>$sc_2016</td><td>$sc_ilf_2016</td><td>$bs_2016</td><td>$bs_ilf_2016</td><td>$edu_total_2016</td><td>$edu_total_ilf_2016</td></tr>");
		print("<tr><td>2017 Actual</td><td>$ns_2017</td><td>$ns_ilf_2017</td><td>$hs_2017</td><td>$hs_ilf_2017</td><td>$sc_2017</td><td>$sc_ilf_2017</td><td>$bs_2017</td><td>$bs_ilf_2017</td><td>$edu_total_2017</td><td>$edu_total_ilf_2017</td></tr>");
		print("<tr><td>2018 Actual</td><td>$ns_2018</td><td>$ns_ilf_2018</td><td>$hs_2018</td><td>$hs_ilf_2018</td><td>$sc_2018</td><td>$sc_ilf_2018</td><td>$bs_2018</td><td>$bs_ilf_2018</td><td>$edu_total_2018</td><td>$edu_total_ilf_2018</td></tr>");
		print("<tr><td>2019 Actual</td><td>$ns_2019</td><td>$ns_ilf_2019</td><td>$hs_2019</td><td>$hs_ilf_2019</td><td>$sc_2019</td><td>$sc_ilf_2019</td><td>$bs_2019</td><td>$bs_ilf_2019</td><td>$edu_total_2019</td><td>$edu_total_ilf_2019</td></tr>");
		print("<tr><td>2019 Prediction</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>$edu_total_pred_2019</td><td>$edu_total_ilf_pred_2019</td></tr>");

		for ($x = 0; $x < 7; $x++)
		{
			$total_predict[($x + 3)] = round( ( $total_predict[$x] + $total_predict[$x + 1] + $total_predict[$x + 2] ) / 3 , 0);
			$total_predict_ilf[($x + 3)] = round( ( $total_predict_ilf[$x] + $total_predict_ilf[$x + 1] + $total_predict_ilf[$x + 2] ) / 3, 0);
			$year = $x + 2020;
			print("<tr><td>$year Prediction</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>".$total_predict[$x + 3]."</td><td>".$total_predict_ilf[$x + 3]."</td></tr>");
		}
		print("<tr><td>Percentage of Error</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>");
		print("</table>");
	?>

</body>
</html>
