// Christian Johnson
// RCOS RPI Directory JavaScript

var delay = 60;
var padding = '15%';
var cached_results = {};
var local_storage_supported;
var suffix_cache = ":v2";
var data_table = null;
var type_timeout = null;


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

function getPersonMajor(person, call, dat){
  if (call == 'set'){
    return;
  }
  if (person.major != undefined){
    return person.major;
  }else if (person.department != undefined){
    return person.department;
  }else{
    return 'N/A';
  }
}

function getPersonYear(person, call, dat){
  if (call == 'set'){
    return;
  }
  if (person.year != undefined){
    return person.year;
  }else{
    return 'N/A';
  }
}

function getOrCreateDataTable(){
  if (!data_table){
    try{
  	  data_table = $('#results').dataTable({
  	    "bProcessing": true,
  	    "bAutoWidth": true,
        "sAjaxDataProp": "data",
        "sDom": 'rt',
        "iDisplayLength": 20,
        "sAjaxSource": "/api?q=michael",
        "sDefaultContent": "hello",
        "aoColumns": [
            { "mData": "name" },
            { "mData": getPersonMajor },
            { "mData": getPersonYear },
            { "mData": "email_html" },
            { "mData": "rcsid", 
              "bVisible": false }
        ]
      });
      $('#results').show();
    }catch(err){
      console.log(err);
    } 
  }
  return data_table;
}

function callServer(keyword){
  if(typeof(keyword)==='undefined'){
    keyword = $('#keyword').val(); 
  }
  table = getOrCreateDataTable();
  table.fnReloadAjax('/api?q=' + keyword);
}

function getURLParameter(name) {
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search)||[,""])[1].replace(/\+/g, '%20'))||null;
}

$(document).ready(function() {
  //Focus on textbox
	$("#keyword").focus();
	
	if (getURLParameter('q')){
	  keyword = getURLParameter('q');
    callServer(keyword);
    $("#keyword").val(keyword);
  }
  
  $('#keyword').keyup(function(e){
    keyword = $('#keyword').val();
    window.history.replaceState(keyword, 'Searching ' + keyword, '/?q=' + keyword);
    if (!keyword || keyword.length == 0) { return; }
    if (e.keyCode == 13 || e.keyCode == 32){
      clearTimeout(type_timeout);
      callServer();
    }else{
      clearTimeout(type_timeout);
      type_timeout = setTimeout(callServer, 500);
    }
    
  });
  
  $("#results tbody").click(function(event) {
      var table = getOrCreateDataTable();
      var pos = table.fnGetPosition(event.target);
      var data = table.fnGetData()[pos[0]];
      if (data.rcsid){
        window.location = '/detail/' + data.rcsid; 
      }
  });
});