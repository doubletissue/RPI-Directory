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
	private static final Object currentUpdateLock = new Object();
	private Activity context = null;
	
	public ResultsListManager(Activity context){
		this.context = context;
	}
	
	private void setCurrentUpdate( Date newCurrentUpdate ){
		synchronized(currentUpdateLock){
			currentUpdate = newCurrentUpdate;
		}
	}
	
	private Date getCurrentUpdate(){
		synchronized(currentUpdateLock){
			return this.currentUpdate;
		}
	}
	
	/*
	 * Perform the actual update asynchronously
	 */
	private class DoUpdate extends AsyncTask<String, Void, ArrayList<QueryResultModel> > {
		private Date updateStart = null;
		
		protected void onPreExecute() {
			//Keep track of when the update was started
			updateStart = new Date();
			setCurrentUpdate( updateStart );
		}
		
		protected ArrayList<QueryResultModel> doInBackground(String... params) {
			String searchTerm = params[0];
			
			//Get the JSON output from the api
			ArrayList<QueryResultModel> apiResult = RPInfoAPI.getInstance().request(searchTerm);
			
			return apiResult;
 		}
		
		protected void onPostExecute(ArrayList<QueryResultModel> apiResult) {
			/*
			 * If this was not the most recently started update, there
			 * isn't much to do...
			 */
			if( getCurrentUpdate() != updateStart ){
				return;
			}
			
			//No need to display more than 25 elements
			final ArrayList<QueryResultModel> list_items = (ArrayList<QueryResultModel>)apiResult.subList(0, 25);
			
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
