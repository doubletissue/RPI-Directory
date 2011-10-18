package org.rpi.rpinfo;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URLEncoder;
import java.util.ArrayList;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HttpContext;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;

public class RPInfoAPI {
	private static final String TAG = "RPInfoAPI";
	private static RPInfoAPI singleton = null;
	private static final String URLBASE = "http://www.rpidirectory.appspot.com/api?name=";
	private static final ResultsCache cache = new ResultsCache();
	private Object requestLock = new Object();
	
	private RPInfoAPI(){
	}
	
	public static RPInfoAPI getInstance(){
		if( singleton == null ){
			singleton = new RPInfoAPI();
		}
		
		return singleton;
	}
	
	private ArrayList<QueryResultModel> parseApiResult(JSONObject apiResult){
		ArrayList<QueryResultModel> list_items = new ArrayList<QueryResultModel>();

		JSONArray data_array;
		try {
			data_array = apiResult.getJSONArray("data");

			// No need to display more than MAX_DISPLAY_ELEMENTS (25) elements
			for( int i = 0; i < data_array.length(); ++i ){
				JSONObject current;

				// Get the current object in the array and add it to the list
				current = data_array.getJSONObject(i);
				list_items.add(new QueryResultModel(current));
			}
		} catch (JSONException e) {
			e.printStackTrace();
		}

		return list_items;
	}
	
	private ArrayList<QueryResultModel> doRequest( String searchTerm ){
		/**
		 * Do only one request at a time - reduce server load, but also
		 * allow requests to take advantage of cached results by previous
		 * requests.
		 */
		Log.i( TAG, "Search: " + searchTerm );
		
		synchronized( requestLock ){
			try {
				ArrayList<QueryResultModel> rv = cache.extract( searchTerm );
				
				if( rv == null ){
					HttpClient httpClient = new DefaultHttpClient();
					HttpContext localContext = new BasicHttpContext();
					
					//URLEncoder sanitize the input
					HttpGet httpGet = new HttpGet( URLBASE + URLEncoder.encode(searchTerm) );
					
					HttpResponse response = httpClient.execute( httpGet, localContext );
					BufferedReader in = new BufferedReader( new InputStreamReader(response.getEntity().getContent()));
					
					rv = parseApiResult( new JSONObject(in.readLine()) );
					//Log.i( TAG, "Insert: " + searchTerm );
					cache.insert( searchTerm, rv );
				}
				
				return rv;
			} catch (ClientProtocolException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			} catch (JSONException e) {
				e.printStackTrace();
			}
		}
		
		return null;
	}
	
	
	public ArrayList<QueryResultModel> request( String searchTerm ){	
		return doRequest( searchTerm );
	}
}