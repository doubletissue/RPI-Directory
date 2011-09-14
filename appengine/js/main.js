// Christian Johnson
// RCOS RPI Directory JavaScript

var last_known_query = "";
var keyword = "";


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
	$("#results").tablesorter({
		//Force sort on name
		sortForce: [[0,0]] 
	}); 
	$("#keyword").keyup(function(event) {
	  keyword = $("#keyword").val();
	
	  // Check for enter keypress
	  if ( event.which == 13 ) {
	     event.preventDefault();
	  }
	  
	  if (keyword != ''){
		  $.ajax({
		     type: "GET",
		     url: "/api?name=" + encodeURI(keyword),
		     async: true,
		 	 dataType: "json",
			 success: parseData,
		   });
	  }else{
		$("#output").text("Type something above!");
	  }
  });				
});