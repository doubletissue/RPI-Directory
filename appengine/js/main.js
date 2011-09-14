// Christian Johnson
// RCOS RPI Directory JavaScript

var last_known_query = "";
var keyword = "";
var delay = 60;
var padding = '15%';


function parseData(data){  
	if (data !== [] && data.length > 0){		
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
	 $("#output").empty();
	 last_known_query = keyword;
	$("#results").trigger("update");
	}else{
		if (last_known_query != '')
		$("#output").text("Nothing found for " + keyword + ", showing results for " + last_known_query);
		else $("#output").text("Nothing found for " + keyword);
	}	
}

$(document).ready(function() {
	$("#keyword").keyup(function(event) {
	  var keyword = $("#keyword").val();
	  var margin = $("#container").css("margin-top");
	
	  // Check for enter keypress
	  if (event.which == 13) {
	     event.preventDefault();
	     return;
	  }
	  
	  if (keyword != ''){
	    //Animate text box up
   	  if ( margin != "0%" || margin != "0px" ){
   	    $("#container").animate({
   	      marginTop: '0%',
   	    }, delay, function(){ $("#container").css("margin-top","0%"); });
   	  }
   	  
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
	    if ( margin == "0%" || margin == "0px"){
	      $("#output").text("Type something above!");
  		  $("#container").animate({
		      marginTop: padding,
		    }, delay*2);
	    }
	  }
  });
  
  //Make table sortable
  $("#results").tablesorter();
  
	//Focus on textbox
	$("#keyword").focus();
});