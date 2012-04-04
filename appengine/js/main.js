// Christian Johnson
// RCOS RPI Directory JavaScript

var delay = 60;
var padding = '15%';
var last_token = 1;
var cached_results = {};
var local_storage_supported;
var query = '';

function parseServerData(data){
	if (data.data !== [] && data.data.length > 0 && last_token == data.token){
	  AddResultsToTable(data);
  }
  // Undo the opacity
  $("#results").css("opacity", "1");
  
  // Cache the results
  cached_results[data.name] = data;
  if (local_storage_supported){
    try {
      localStorage.setItem(data.name, JSON.stringify(data));
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
    //$("#output").text("JS Cached Keyword: " + keyword);
  }else if (local_storage_supported && localStorage.getItem(keyword)){
    data = JSON.parse(localStorage.getItem(keyword));
    //$("#output").text("HTML5 Cached Keyword: " + keyword);
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
  
  // Loop through JSON
  $.each(data.data, function(i, person){
    var table_row = "<tr>";
    
    //Professor Check
    if (person.major == "None" && person.department == "None"){
      person.major = "N/A";
    }else if (person.department != "None"){
      person.major = person.department;
    }

    //Faculty Check
    if (person.year == "None" && person.title != "None"){
      person.year = person.title;
    }else if (person.year == "None" && person.department != "None"){
      person.year = "Faculty";
    }
    
    table_row += ("<td>" + person.name + "</td><td>" + person.major + "</td><td>" + (person.year == "None" ? 'N/A' : person.year) + "</td><td>" + (person.email == "None" ? 'N/A' : person.email) + "</td>");
    table_row += "</tr>";
    $("#results").find("tbody").append(table_row);
  });
  $("#results").trigger("update");
}

//Function to animate text box:
// Send true to animate it up, false to animate it down
function animate(flag){
  if (flag){
    $("#container").animate({
      marginTop: '0%'
    }, delay, function(){ $("#container").css("margin-top","0%"); });
  }else{
    $("#container").animate({
      marginTop: padding,
    }, delay * 1.3);
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
    url: "/api?name=" + encodeURI(keyword) + "&token=" + last_token,
    async: true,
    dataType: "json",
    success: parseServerData
  });
}

$(document).ready(function() {
  $("#keyword").keyup(function(event){
    var keyword = $("#keyword").val().toLowerCase();
	  var margin = $("#container").css("margin-top");
	  
    // Check for enter keypress
	  if (event.which == 13) {
	     event.preventDefault();
	     return;
	  }
    
    if (keyword != ''){
	    //Animate text box up
   	  if ( margin != "0%" || margin != "0px" ){
   	    animate(true);
   	  }
 	    $("#results").show();
 	    // Check cache
 	    if (cached_results[keyword] || (local_storage_supported && localStorage.getItem(keyword))){
 	      parseCachedData(keyword);
 	      $("#results").css("opacity", "1");
 	    }
    }
  });
  
	$("#keyword").bindWithDelay("keyup", function(event) {
	  var keyword = $("#keyword").val().toLowerCase();
	  var margin = $("#container").css("margin-top");
    
    // If a non-blank entry
	  if (keyword != ''){ 	   
 	    last_token += 1;
 	    
 	    // Check cache
 	    if (cached_results[keyword] || (local_storage_supported && localStorage.getItem(keyword))){
 	      parseCachedData(keyword);
 	    }else{  // Dim results and call the API
 	      $("#results").css("opacity", ".25");
 	      callServer(keyword);
 	    }
 	    
 	    $("#results").css("opacity", "1");
	  }else if (keyword == ''){ // Entry is blank
	    $("#results").hide();
	    // Animate box back down
	    if ( margin == "0%" || margin == "0px"){
  		  animate(false);
	    }
    }
  }, 500);
  
  //Make table sortable
  $("#results").tablesorter();
  
	//Focus on textbox
	$("#keyword").focus();
	
	//Detect LocalStorage (HTML5 Cache)
	local_storage_supported = DetectLocalStorage();
});