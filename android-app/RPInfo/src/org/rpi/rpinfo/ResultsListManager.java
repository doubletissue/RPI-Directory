package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;

import android.app.Activity;
import android.content.Intent;
import android.os.AsyncTask;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListView;

public class ResultsListManager {
	private class SearchTermData {
		public SearchTermData(String searchTerm, Date searchDate){
			this.searchTerm = searchTerm;
			this.searchDate = searchDate;
		}
		
		public String searchTerm;
		public Date searchDate;
	}
	
	private static final String TAG = "ResultsListManager";
	private Date currentUpdate = new Date();
	private static final Object currentUpdateLock = new Object();
	private Activity context = null;
	//Keep track of search terms so that they can be buffered
	private LinkedList<SearchTermData> searchTerms = new LinkedList<SearchTermData>();
	//Lock for the searchTerms list
	private Object searchTermsLock = new Object();
	//Lock for searching
	private Object searchLock = new Object();

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
	
	private SearchTermData getNextSearchTerm(){
		synchronized(searchTermsLock){
			return searchTerms.removeFirst();
		}
	}
	
	//Perform the actual update asynchronously
	private class DoUpdate extends AsyncTask<Void, Void, ArrayList<QueryResultModel> > {
		private Date updateStart = null;
		
		protected void onPreExecute() {
			return;
		}
		
		protected ArrayList<QueryResultModel> doInBackground(Void... params){
			if( searchTerms.size() == 0 ){
				return null;
			}
			
			ArrayList<QueryResultModel> apiResult = null;			
			synchronized(searchLock){
				SearchTermData searchTermData = getNextSearchTerm();
				
				updateStart = searchTermData.searchDate;
						
				//Get the JSON output from the api
				apiResult = RPInfoAPI.getInstance().request(searchTermData.searchTerm, RPInfoAPI.FIRST_PAGE, RPInfoAPI.DEFAULT_NUM_RESULTS);
			}
			
			return apiResult;
 		}
		
		protected void onPostExecute(final ArrayList<QueryResultModel> apiResult) {
			/*
			 * If this was not the most recently started update or there is no api result,
			 * there isn't much that we can do.
			 */
			//Log.i(TAG, "" + getCurrentUpdate().getTime() + " " + updateStart.getTime() );
			if( getCurrentUpdate() != updateStart || apiResult == null ){
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
		synchronized(searchTermsLock){
			Date thisUpdate = new Date();
			searchTerms.addFirst( new SearchTermData( searchTerm, thisUpdate ) );
			setCurrentUpdate(thisUpdate);
		}
		new DoUpdate().execute();
	}
}
