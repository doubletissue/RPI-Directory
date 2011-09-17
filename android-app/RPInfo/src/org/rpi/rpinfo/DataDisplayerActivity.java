package org.rpi.rpinfo;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListView;

public class DataDisplayerActivity extends Activity {
	private static final String TAG = "DataDisplayerActivity";
	
	/** 
	 * @param in An input stream.
	 * @return String containing everything that was in the input stream.
	 */
	private String readInputStream(InputStream in){
		try {
			String result = "";
			byte[] buffer = new byte[1024];
			
			//Loop until there is nothing left in the stream
			while( in.available() > 0 ){
				//Only write to the string the number of bytes read
				int num_read = in.read(buffer, 0, buffer.length);
				result = result + new String(buffer, 0, num_read);
			}
			
			return result;
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return null;
	}

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

	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        setContentView(R.layout.data_view);
                
        //Extract the search term
  		Bundle b = getIntent().getExtras();
  		if( b == null ){
  			finish();
  		}
  		String searchTerm = (String)b.get("searchTerm");

  		//Get the JSON output from the api
  		JSONObject apiResult = null;
  		try {
  			URL apiURL = new URL("http://rpidirectory.appspot.com/api?name=" + searchTerm);
  			URLConnection connection = apiURL.openConnection();
  			InputStream in = new BufferedInputStream(connection.getInputStream());
  			apiResult = new JSONObject(readInputStream(in));
  			Log.i(TAG, apiResult.toString());
  		} catch (MalformedURLException e) {
  			e.printStackTrace();
  		} catch (IOException e) {
  			e.printStackTrace();
		} catch (JSONException e) {
			e.printStackTrace();
		}

		// This is the array of objects to be displayed
		final ArrayList<QueryResultModel> list_items = parseApiResult(apiResult);
              
        ListView lv = (ListView)findViewById(R.id.data_list);
        lv.setAdapter(new QueryResultArrayAdapter(this, R.layout.query_result_list_item, list_items));

        
        lv.setOnItemClickListener(new OnItemClickListener(){
        	public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
				//TextView name = (TextView) view.findViewById(R.id.query_result_name);
				
				Intent i = new Intent(DataDisplayerActivity.this, DetailedDataDisplayerActivity.class);
				i.putExtra("selectedPerson", list_items.get((int) id));
				startActivity(i);
				
				//Toast.makeText(getApplicationContext(), name.getText(), Toast.LENGTH_SHORT).show();
			}
        });
	}
}