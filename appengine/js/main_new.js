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
 * Title Caps
 * 
 * Ported to JavaScript By John Resig - http://ejohn.org/ - 21 May 2008
 * Original by John Gruber - http://daringfireball.net/ - 10 May 2008
 * License: http://www.opensource.org/licenses/mit-license.php
 */

(function(){
	var small = "(a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|v[.]?|via|vs[.]?)";
	var punct = "([!\"#$%&'()*+,./:;<=>?@[\\\\\\]^_`{|}~-]*)";
  
	this.titleCaps = function(title){
		var parts = [], split = /[:.;?!] |(?: |^)["Ò]/g, index = 0;
		
		while (true) {
			var m = split.exec(title);

			parts.push( title.substring(index, m ? m.index : title.length)
				.replace(/\b([A-Za-z][a-z.'Õ]*)\b/g, function(all){
					return /[A-Za-z]\.[A-Za-z]/.test(all) ? all : upper(all);
				})
				.replace(RegExp("\\b" + small + "\\b", "ig"), lower)
				.replace(RegExp("^" + punct + small + "\\b", "ig"), function(all, punct, word){
					return punct + upper(word);
				})
				.replace(RegExp("\\b" + small + punct + "$", "ig"), upper));
			
			index = split.lastIndex;
			
			if ( m ) parts.push( m[0] );
			else break;
		}
		
		return parts.join("").replace(/ V(s?)\. /ig, " v$1. ")
			.replace(/(['Õ])S\b/ig, "$1s")
			.replace(/\b(AT&T|Q&A)\b/ig, function(all){
				return all.toUpperCase();
			});
	};
    
	function lower(word){
		return word.toLowerCase();
	}
    
	function upper(word){
	  return word.substr(0,1).toUpperCase() + word.substr(1);
	}
})();

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
    return titleCaps(person.major);
  }else if (person.department != undefined){
    return titleCaps(person.department);
  }else{
    return 'N/A';
  }
}

function getPersonYear(person, call, dat){
  if (call == 'set'){
    return;
  }

  if (person.year != undefined){
    return titleCaps(person.year);
  }else if (person.title != undefined){
		return titleCaps(person.title);
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
        "sAjaxSource": "/api?q=",
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
		if (!$.browser.msie) {
		  window.history.replaceState(keyword, 'Searching ' + keyword, '/?q=' + keyword);
		}
    
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

  if (document.getElementById('profile-link') != null){
    $('#profile-link').popover({
      placement: 'bottom',
      trigger: 'hover',
      title: 'Have you claimed your profile yet?',
      content: 'Make sure to <a href="/dashboard">claim</a> your profile!'
    });
    setTimeout(function(){$('#profile-link').popover('show');}, 250);
  }    
});