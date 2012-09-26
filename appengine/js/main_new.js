// Christian Johnson
// RCOS RPI Directory JavaScript

var delay = 60;
var padding = '15%';
var cached_results = {};
var local_storage_supported;
var suffix_cache = ":v2";
var data_table = 0;


/*
Function to animate text box.
send true to animate it up, false to animate it down
*/
function animate(flag){
  if (flag){    
    $("#qr").hide();
    $("#sidebar").show();
    $("#container").animate({
      marginTop: '0%'
    }, delay, function(){ $("#container").css("margin-top","0%"); });
  }else{
    $("#container").animate({
      marginTop: padding
    }, delay * 1.3);
    $("#sidebar").hide();
    $("#qr").show();
  }
}

//Detect HTML5 Local Storage
function DetectLocalStorage(){
  try{
    if (window['localStorage'] !== null){
      _gaq.push(['_trackEvent', 'Local Storage', 'True']);
      return true;
    }
  }catch(e){
    _gaq.push(['_trackEvent', 'Local Storage', 'False']);
    return false;
  }
}

function callServer(keyword){
  if(request_in_progress){
    request.abort();
  }
  request_in_progress = true;
  url = "/api?q=" + keyword + "&token=" + last_token + "&source=website";
  request = $.getJSON(url, parseServerData);
}
	
$(document).ajaxError(function(event, request, settings, exception){
  console.log("Error: "  + exception);
  _gaq.push(['_trackEvent', 'Error', 'Parsing Error: ' + exception]);
});

// divert alerts to console.log if available
if (typeof(console) !== "undefined") {
  window.alert = function(content) {
    try {
      window.console.log(content);
    } catch(e) {}
  }
}

$(document).ready(function() {
  //Focus on textbox
	$("#keyword").focus();
	
	try{
	  data_table = $('#results').dataTable({
      "bProcessing": true,
      "bServerSide": true,
      "sAjaxDataProp": "data",
      "sDom": 'rt<p>',
      "sAjaxSource": "/api?q=michael",
      "aoColumns": [
          { "mData": "name" },
          { "mData": "department" },
          { "mData": "year" },
          { "mData": "email" }
      ]
    });
  }catch(err){
    console.log(err);
  }
  
  $('#keyword').keydown(function(e){
    if (e.keyCode == 13){
      alert('Enter');
      $('#results').dataTable().fnReloadAjax('/api?q=' + $(this).val());
    }
  });
  
});