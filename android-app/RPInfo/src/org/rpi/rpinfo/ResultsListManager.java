package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.Date;

import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListView;

//(data_array.length() < MAX_DISPLAY_ELEMENTS ? data_array.length() : MAX_DISPLAY_ELEMENTS)

public class ResultsListManager {
	private static final int MAX_DISPLAY_ELEMENTS = 25;
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
	
	/**
	 * Extract the first MAX_DISPLAY_ELEMENTS (25) from the result of
	 * the API call. More is unnecessary. 
	 */
	private ArrayList<QueryResultModel> extractDisplayList( ArrayList<QueryResultModel> x ){
		ArrayList<QueryResultModel> rv = new ArrayList<QueryResultModel>(); 
		
		for( int i = 0; i < (x.size() < MAX_DISPLAY_ELEMENTS ? x.size(): MAX_DISPLAY_ELEMENTS ); ++i ){
			rv.add( x.get(i) );
		}
		
		return rv;
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
			ArrayList<QueryResultModel> apiResult = extractDisplayList(RPInfoAPI.getInstance().request(searchTerm));
			
			return apiResult;
 		}
		
		protected void onPostExecute(final ArrayList<QueryResultModel> apiResult) {
			/*
			 * If this was not the most recently started update, there
			 * isn't much to do...
			 */
			if( getCurrentUpdate() != updateStart ){
				return;
			}
						
			//Set up the list view (where the results are displayed)
	        ListView lv = (ListView)context.findViewById(R.id.data_list);
	        lv.setAdapter(new QueryResultArrayAdapter(context, R.layout.query_result_list_item, apiResult));

	        lv.setOnItemClickListener(new OnItemClickListener(){
	        	public void onItemClick(AdapterView<?> parent, View view, int position, long id) {			
					Intent i = new Intent(context, DetailedDataDisplayerActivity.class);
					i.putExtra("selectedPerson", apiResult.get((int) id));
					context.startActivity(i);
				}
	        });
		}
	}
	
	/**
	 * Wrapper for AsyncTask DoUpdate
	 */
	public void update(String searchTerm){
		new DoUpdate().execute(searchTerm);
	}
}
