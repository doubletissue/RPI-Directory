// Christian Johnson
// RCOS RPI Directory JavaScript

var delay = 60;
var keybind_delay = Math.floor(100 + Math.random() * 100);
var padding = '15%';
var last_token = 1;
var cached_results = {};
var local_storage_supported;
var query = '';

//Chart data and charts
var class_chart_data, department_chart_data;
var major_chart, department_chart;

function resetCharts(){
  //Reset chart
  class_chart_data.removeRows(0, class_chart_data.getNumberOfRows());
  department_chart_data.removeRows(0, department_chart_data.getNumberOfRows());
}

function redrawCharts(class_chart_data, department_chart_data){
  // Set class chart options
  var class_chart_options = {
    'title':'Class/Positions in Results',
    'height': 300,
    'animation':{
      duration: 250,
      easing: 'out',
    }
  };
  
  var department_chart_options = {
    'title':'Departments in Results',
    'height': 300,
    'animation':{
      duration: 250,
      easing: 'out',
    }
  };
  
  //Update graphs
  major_chart.draw(class_chart_data, class_chart_options);
  department_chart.draw(department_chart_data, department_chart_options);
  
}

function parseServerData(data){
  // Check if quota exceeded
  if (data.data !== [] && data.data == "Quota Exceeded"){
    jError(
    		'You have exceeded our rate limit!  Please wait 5 minutes and try again.  In the meantime, I will send you to a fun place.  Enjoy!',
    		{
    		  clickOverlay : false, // added in v2.0
    		  MinWidth : 250,
    		  TimeShown : 5000,
    		  LongTrip :20,
    		  HorizontalPosition : 'center',
    		  onClosed : function(){ // added in v2.0
            window.location = "http://goo.gl/QMET";
    		  }
    		});
    return;
  }
  
  // Check if database errored out
  if (data.data !== [] && data.data == "Error with request, please try again"){
    jError(
    		'Our database seems to be having some issues, we apologize.  Lets try refreshing the page to see if that helps.',
    		{
    		  clickOverlay : false, // added in v2.0
    		  MinWidth : 250,
    		  TimeShown : 5000,
    		  LongTrip :20,
    		  HorizontalPosition : 'center',
    		  onClosed : function(){ // added in v2.0
            location.reload(true);
    		  }
    		});
    return;
  }
  
  //Empty list
  if (data.data.length == 0){
    $("#results").css("opacity", "1");
  }
  
	if (data.data.length > 0 && Math.abs(last_token - data.token) < 2){
	  AddResultsToTable(data);
  }
  
  // Cache the results
  var keyword_cache = data.q + ":v2"
  cached_results[keyword_cache] = data;
  if (local_storage_supported){
    try {
      localStorage.setItem(keyword_cache, JSON.stringify(data));
    }catch (e){
      if (e == QUOTA_EXCEEDED_ERR) {
        // oh noes, out of 5 MB of localstorage...clear it out!
        localStorage.clear();
      }
    }
  }
}

function parseCachedData(keyword){
  var data = null;
  if (cached_results[keyword]){
    data = cached_results[keyword];
  }else if (local_storage_supported && localStorage.getItem(keyword)){
    data = JSON.parse(localStorage.getItem(keyword));
  }
  
	if (data !== null && data.data !== []){
	  AddResultsToTable(data);
	}else{
	  callServer(keyword);
	}
}

function AddResultsToTable(data){
  // Get rid of current results		
  $("#results").find("tbody").empty();
  
  resetCharts();
  
  //Track data
  var classes = {};
  var departments = {};
  
  // Loop through JSON
  $.each(data.data, function(i, person){
    var table_row = "<tr>";
    
    //Professor Check
    if (person.major == undefined && person.department == undefined){
      person.major = "N/A";
    }else if (person.department != undefined){
      person.major = person.department;
    }

    //Faculty Check
    if (person.year == undefined && person.title != undefined){
      person.year = person.title;
    }else if (person.year == undefined && person.department != undefined){
      person.year = "Faculty";
    }
    
    var email = "";
    
    //EMail check
    if (person.email != undefined){
      email = person.email.replace("@", " [at] ");
      while (email.indexOf(".") > -1){
        email = email.replace(".", " [dot] ");
      }
    }else{
      email = "N/A";
    }
    
    table_row += ("<td>" + person.name + "</td><td>" + person.major + "</td><td>" + (person.year == undefined ? 'N/A' : person.year) + "</td><td>" +  email + "</td>");
    table_row += "</tr>";
    $("#results").find("tbody").append(table_row);
    
    if (person.year == undefined){
      person.year = "N/A";
    }
    
    //Add to classes chart
    if (classes[person.year] == undefined){
      classes[person.year] = 1;
    }else{
      classes[person.year] += 1;
    }
    
    //Add to departments chart
    if (departments[person.major] == undefined){
      departments[person.major] = 1;
    }else{
      departments[person.major] += 1;
    }
    
  });
  
  $("#results").trigger("update");
  $("#results").css("opacity", "1");
  
  for (key in classes){
    class_chart_data.addRow([key, classes[key]]);
  }
  
  for (key in departments){
    department_chart_data.addRow([key, departments[key]]);
  }
  
  redrawCharts(class_chart_data, department_chart_data);
}

//Function to animate text box:
// Send true to animate it up, false to animate it down
function animate(flag){
  if (flag){    
    $("#qr").hide();
    $("#sidebar").show();
    $("#container").animate({
      marginTop: '0%'
    }, delay, function(){ $("#container").css("margin-top","0%"); });
  }else{
    $("#container").animate({
      marginTop: padding,
    }, delay * 1.3);
    $("#sidebar").hide();
    $("#qr").show();
  }
}

//Detect HTML5 Local Storage
function DetectLocalStorage(){
  try{
    if (window['localStorage'] !== null){
      return true;
    }
  }catch(e){
    return false;
  }
}

function callServer(keyword){
  $.ajax({
    type: "GET",
    url: "/api?q=" + encodeURI(keyword) + "&token=" + last_token + "&delay=" + keybind_delay,
    async: true,
    dataType: "json",
    success: parseServerData
  });
}

$(document).ready(function() {
	$("#keyword").bindWithDelay("keyup", function(event) {
	  var keyword = $("#keyword").val().toLowerCase();
	  var margin = $("#container").css("margin-top");
    
    // If a non-blank entry
	  if (keyword != ''){ 	   
 	    last_token += 1;
 	    
 	    //Animate text box up
   	  if ( margin != "0%" || margin != "0px" ){
   	    animate(true);
   	  }
 	    
 	    $("#results").show();
 	    
 	    //Omnibox Search
 	    var keyword_cache = keyword + ":v2"
 	    
 	    // Check cache
 	    if (cached_results[keyword_cache] || (local_storage_supported && localStorage.getItem(keyword_cache))){
 	      parseCachedData(keyword_cache);
 	    }else{  // Dim results and call the API
 	      $("#results").css("opacity", ".25");
 	      callServer(keyword);
 	    }
	  }else if (keyword == ''){ // Entry is blank
	    $("#results").hide();
	    // Animate box back down
	    if ( margin == "0%" || margin == "0px"){
  		  animate(false);
	    }
    }
  }, keybind_delay);
  
  //Make table sortable
  $("#results").tablesorter();
  
	//Focus on textbox
	$("#keyword").focus();
	
	//Detect LocalStorage (HTML5 Cache)
	local_storage_supported = DetectLocalStorage();
	
	//Class Chart
	class_chart_data = new google.visualization.DataTable();
  class_chart_data.addColumn('string', 'Major');
  class_chart_data.addColumn('number', 'Amount');
  
  //Department Chart
  department_chart_data = new google.visualization.DataTable();
  department_chart_data.addColumn('string', 'Department');
  department_chart_data.addColumn('number', 'Amount');
  
  // Instantiate and draw our chart, passing in some options.
  major_chart = new google.visualization.PieChart(document.getElementById('major_stats'));
  
  department_chart = new google.visualization.PieChart(document.getElementById('department_stats'));
  
});