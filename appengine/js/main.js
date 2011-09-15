// Christian Johnson
// RCOS RPI Directory JavaScript

var keyword = "";
var delay = 60;
var padding = '20%';

function parseData(data){  
	if (data !== [] && data.length > 0){
	  // Get rid of current results		
	  $("#results").find("tbody").empty();
	 
	  // Loop through JSON
	  $.each(data, function(i, person){
	    var table_row = "<tr>";
      // Loop through each person and output their attributes
      //$.each(person, function(key, value){
		   //if (key in {'name':'', 'major':'','class':''}/* && value != undefined*/){
		   //  table_row += ("<td>" + value + "</td>");	
		   //}
	    //});
	    table_row += ("<td>"+person.name+"</td><td>"+ (person.major == undefined ? 'N/A' : person.major) +"</td><td>"+ (person.class == undefined ? 'N/A' : person.class) +"</td>");
	    table_row += "</tr>"
      $("#results").find("tbody").append(table_row);
	  });
	  $("#results").trigger("update");
  }
  // Cool idea, flickers though :-\
  //$("#results").css("opacity", "1");
}

//Function to animate text box:
// Send true to animate it up, false to animate it down
function animate(flag){
  if (flag){
    $("#container").animate({
      marginTop: '0%',
    }, delay, function(){ $("#container").css("margin-top","0%"); });
  }else{
    $("#container").animate({
      marginTop: padding,
    }, delay * 2);
  }
}

$(document).ready(function() {
	$("#keyword").bindWithDelay("keyup", function(event) {
	    var keyword = $("#keyword").val();
  	  var margin = $("#container").css("margin-top");
	
  	  // Check for enter keypress
  	  if (event.which == 13) {
  	     event.preventDefault();
  	     return;
  	  }
	    
	    // If a non-blank entry
  	  if (keyword != ''){
  	    //Animate text box up
     	  if ( margin != "0%" || margin != "0px" ){
     	    animate(true);
     	  }
   	   
   	    // Cool idea, flickering for some reason though
   	    //$("#results").css("opacity", ".25");
   	    
  		  $.ajax({
		      type: "GET",
		      url: "/api?name=" + encodeURI(keyword),
		      async: true,
		 	    dataType: "json",
			    success: parseData,
		    });
		   
  		  $("#results").show();
  	  }else if (keyword == ''){ // Entry is blank
  	    $("#results").hide();
  	    // Animate box back down
  	    //if ( margin == "0%" || margin == "0px"){
    		//  animate(false);
  	    //}
	    }
	  }, 175);
  
  //Make table sortable
  $("#results").tablesorter();
  
	//Focus on textbox
	$("#keyword").focus();
});