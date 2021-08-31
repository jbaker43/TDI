//function to load second ddlist (drop down list)
function stateSelected()
{
  //wipe current list elements
  while(newDropDown.options.length > 0)
  {
    newDropDown.options.remove(0);
  }

    //gets selected element in first ddlist and sets text to access file
    let el = document.getElementById("state");
    let elText = el.options[el.selectedIndex].text;
    let text = elText.toLowerCase() + ".json";
    //alert(text);

  loadJson(text);
}

//populates lists from JSON files
function loadJson(path)
{
  $.getJSON(path, function(data)
  {
    //debugging
    // console.log(data);
    $.each(data, function(i)
    {
      //debugging
      //console.log(data[i]["id"]);
      //console.log(data[i]["name"]);

      //creates selection options in dropdown lists
      let a = document.createElement("option");
      a.value = data[i]["id"];
      a.text = data[i]["name"];

      //quick fix to only load states (counter = how many states want to load in first ddlist)
      counter += 1;
      if(counter <= 3)
      {
        //first ddlist
        document.getElementById("state").appendChild(a);
      }
      else
      {
        //second ddlist
        document.getElementById("county").appendChild(a);
      }
    })
  })
}




//creates second ddlist
var newDropDown = document.createElement("select");
document.body.appendChild(newDropDown);
newDropDown.id = "county";
newDropDown.name = "county";

//initiates counter variable
var counter = 0;
//file name for first ddlist options
var filePath = "states.json";
loadJson(filePath);

//creates listeners to run functions when selections are made
document.getElementById("state").addEventListener("change", stateSelected);
document.getElementById("county").addEventListener("change", function() {
  runButton.disabled = false;
}, {once : true});

//creates button to submit to php file
var runButton = document.createElement("button");
runButton.innerHTML = "SUBMIT";
document.body.appendChild(runButton);
runButton.disabled = true;

//button to run POST method
runButton.addEventListener("click", function() {
  var stateID = document.getElementById("state");
  stateID = stateID.options[stateID.selectedIndex].value;
  var countyID = document.getElementById("county");
  countyID = countyID.options[countyID.selectedIndex].value;
  var apiCall_2016 = "";

  //var api2016 = fetch('https://api.census.gov/data/2017/acs/acs5?get=NAME,B23006_002E,B23006_003E,B23006_009E,B23006_010E,B23006_016E,B23006_017E,B23006_023E,B23006_024E&for=county:' + countyID + '&in=state:' + stateID);

  //console.log(data2016);

  //Attempt to get data from php file
$.post('site.php', {
  stateID: stateID,
  countyID: countyID,
    }, function(data){

    //needs to save new variables from php file here
    console.log(JSON.stringify(data));

    //print table values to html page
    let table = document.querySelector('table');

    let temp = "<table border = '2'><tr><th>Year</th><th>No School</th><th>No School [In Labor Force]</th><th>High School [or equivalent]</th><th>High School [In Labor Force]</th><th>SC/AA</th><th>SC/AA [In Labor Force</th><th>Bachelor's [or higher]</th><th>Bachelor's [In Labor Force]</th><th>EDU Total</th><th>EDU Total [In Labor Force]</th>";
    let row1 = "</tr><tr><td>103229</td></tr>";

    //adds rows to tables
    table.innerHTML += temp;
    table.innerHTML += row1;
  });

  //Alternate attempt to get data from php file

  // $.ajax({
  //   type: 'POST',
  //   url: 'test.php',
  //   success:
  //   function(result){
  //     var jsonResult = JSON.parse(result);
  //
  //     let table = document.querySelector('table');
  //     let temp = "<table border = '2'><tr><th>Year</th><th>No School</th><th>No School [In Labor Force]</th><th>High School [or equivalent]</th><th>High School [In Labor Force]</th><th>SC/AA</th><th>SC/AA [In Labor Force</th><th>Bachelor's [or higher]</th><th>Bachelor's [In Labor Force]</th><th>EDU Total</th><th>EDU Total [In Labor Force]</th>";
  //     table.innerHTML += temp;
  //
  //     jsonResult.forEach(function(data) {
  //       let row1 = "<tr>" + data.stateID + "</tr>"
  //     })
  //   }
  // });
});
