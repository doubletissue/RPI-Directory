package org.rpi.rpinfo;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HttpContext;
import org.json.JSONException;
import org.json.JSONObject;

public class RPInfoAPI {
	private static RPInfoAPI singleton = null;
	private static final String URLBASE = "http://www.rpidirectory.appspot.com/api?name=";
	
	private RPInfoAPI(){
	}
	
	public static RPInfoAPI getInstance(){
		if( singleton == null ){
			singleton = new RPInfoAPI();
		}
		
		return singleton;
	}
	
	public JSONObject request( String searchTerm ){
		//No spaces in a proper URL
		searchTerm = searchTerm.replace(" ", "+");
		
		try {
			HttpClient httpClient = new DefaultHttpClient();
			HttpContext localContext = new BasicHttpContext();
			HttpGet httpGet = new HttpGet(URLBASE + searchTerm);
			HttpResponse response = httpClient.execute( httpGet, localContext );
			BufferedReader in = new BufferedReader( new InputStreamReader(response.getEntity().getContent()));
			return new JSONObject(in.readLine());
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (JSONException e) {
			e.printStackTrace();
		}
		
		return null;
	}
	
	
}