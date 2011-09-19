package org.rpi.rpinfo;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
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

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.KeyEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnKeyListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;

public class DataDisplayerActivity extends Activity {
	private static final String TAG = "DataDisplayerActivity";

	private ArrayList<QueryResultModel> parseApiResult(JSONObject apiResult) {
		ArrayList<QueryResultModel> list_items = new ArrayList<QueryResultModel>();

		JSONArray data_array;
		try {
			data_array = apiResult.getJSONArray("data");

			// Extract the first 25 items from the list - more won't be helpful to display
			for (int i = 0;
					i < (data_array.length() < 25 ? data_array.length() : 25);
					++i) {
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
	
	private void updateList(String searchTerm){
		//No spaces in a proper URL
		searchTerm = searchTerm.replace(" ", "+");
		
		//Get the JSON output from the api
  		JSONObject apiResult = null;
		try {
			HttpClient httpClient = new DefaultHttpClient();
			HttpContext localContext = new BasicHttpContext();
			HttpGet httpGet = new HttpGet("http://www.rpidirectory.appspot.com/api?name=" + searchTerm);
			HttpResponse response = httpClient.execute( httpGet, localContext );
			BufferedReader in = new BufferedReader( new InputStreamReader(response.getEntity().getContent()));
			apiResult = new JSONObject(in.readLine());
		} catch (ClientProtocolException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (JSONException e) {
			e.printStackTrace();
		}
		
		// This is the array of objects to be displayed
		final ArrayList<QueryResultModel> list_items = parseApiResult(apiResult);
              
		//Set up the list view (where the results are displayed)
        ListView lv = (ListView)findViewById(R.id.data_list);
        lv.setAdapter(new QueryResultArrayAdapter(this, R.layout.query_result_list_item, list_items));

        lv.setOnItemClickListener(new OnItemClickListener(){
        	public void onItemClick(AdapterView<?> parent, View view, int position, long id) {			
				Intent i = new Intent(DataDisplayerActivity.this, DetailedDataDisplayerActivity.class);
				i.putExtra("selectedPerson", list_items.get((int) id));
				startActivity(i);
			}
        });
	}

	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        setContentView(R.layout.data_view);
                
        final Button submitButton = (Button)findViewById(R.id.submit);
        final EditText searchBox = (EditText)findViewById(R.id.searchBox);
        
        /* 
         * Automatically populate the results while the user types
         * (but only if the user has typed 3 or more characters)
         */
        searchBox.addTextChangedListener(new TextWatcher() {
			
			public void onTextChanged(CharSequence s, int start, int before, int count) {
				if( searchBox.getText().length() >= 3 ){
					updateList( searchBox.getText().toString() );
				}
			}
			
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				//Nothing
			}
			
			public void afterTextChanged(Editable s) {
				//Nothing
			}
		});
        
        /*
         * Manually populate the results when the user requests it
         */
        submitButton.setOnClickListener(new OnClickListener() {
			public void onClick(View v){
				updateList( searchBox.getText().toString() );
			}
		});
	}
}