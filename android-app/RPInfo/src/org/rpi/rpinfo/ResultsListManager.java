package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.Date;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListView;

public class ResultsListManager {
	private Date currentUpdate = new Date();
	private Activity context = null;
	
	public ResultsListManager(Activity context){
		this.context = context;
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
	
	/*
	 * Perform the actual update asynchronously
	 */
	private class DoUpdate extends AsyncTask<String, Void, JSONObject>{
		private Date updateStart = null;
		
		protected void onPreExecute() {
			//Keep track of when the update was started
			updateStart = new Date();
			currentUpdate = updateStart;
		}
		
		protected JSONObject doInBackground(String... params) {
			String searchTerm = params[0];
			
			//Get the JSON output from the api
	  		JSONObject apiResult = RPInfoAPI.getInstance().request(searchTerm);
			
			return apiResult;
 		}
		
		protected void onPostExecute(JSONObject apiResult) {
			/*
			 * f this was not the most recently started update, there
			 * isn't much to do...
			 */
			if( currentUpdate != updateStart ){
				return;
			}
			
			//This is the array of objects to be displayed
			final ArrayList<QueryResultModel> list_items = parseApiResult(apiResult);
			
			//Set up the list view (where the results are displayed)
	        ListView lv = (ListView)context.findViewById(R.id.data_list);
	        lv.setAdapter(new QueryResultArrayAdapter(context, R.layout.query_result_list_item, list_items));

	        lv.setOnItemClickListener(new OnItemClickListener(){
	        	public void onItemClick(AdapterView<?> parent, View view, int position, long id) {			
					Intent i = new Intent(context, DetailedDataDisplayerActivity.class);
					i.putExtra("selectedPerson", list_items.get((int) id));
					context.startActivity(i);
				}
	        });
		}
	}
	
	/*
	 * Wrapper for AsyncTask DoUpdate
	 */
	public void update(String searchTerm){
		new DoUpdate().execute(searchTerm);
	}
}
