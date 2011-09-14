// Christian Johnson
// RCOS RPI Directory JavaScript

var last_known_query = "";

function parseData(data){
	if (data !== [] && data.length > 0){		
	 $("#results").empty();	
	 $.each(data, function(i, person){
       $("#results").append("<li>" + person.name + " - " + person.class + " -  " + person.major +  "</li>");
	 });
	 $("#output").text("Results for: " + keyword);
	 last_known_query = keyword;
	}else{
		if (last_known_query != '')
		$("#output").text("Nothing found for " + keyword + ", showing results for " + last_known_query);
		else $("#output").text("Nothing found for " + keyword);
	}
}

$(document).ready(function() {
	$("#keyword").keyup(function(event) {
	  var keyword = $("#keyword").val();
	
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