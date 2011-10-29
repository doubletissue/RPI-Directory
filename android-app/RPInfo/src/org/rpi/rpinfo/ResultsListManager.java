package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.LinkedList;
import java.util.List;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AbsListView;
import android.widget.AbsListView.OnScrollListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.Button;
import android.widget.LinearLayout;
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
		private SearchTermData searchTermData = null;
		
		protected void onPreExecute() {
			return;
		}
		
		protected ArrayList<QueryResultModel> doInBackground(Void... params){
			if( searchTerms.size() == 0 ){
				return null;
			}
			
			ArrayList<QueryResultModel> apiResult = null;			
			synchronized(searchLock){
				searchTermData = getNextSearchTerm();
										
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
			if( getCurrentUpdate() != searchTermData.searchDate || apiResult == null ){
				return;
			}
						
			//Set up the list view (where the results are displayed)
	        final ListView lv = (ListView)context.findViewById(R.id.data_list);
	        final QueryResultArrayAdapter a = new QueryResultArrayAdapter(context, R.layout.query_result_list_item, apiResult, searchTermData.searchTerm);

	        //Set up the bottom at the end of the list (must be done before setAdapter)
	        LayoutInflater layoutInflater = (LayoutInflater)context.getSystemService( Context.LAYOUT_INFLATER_SERVICE );
	        LinearLayout ll = (LinearLayout)layoutInflater.inflate(R.layout.query_result_list_more_button, null, false);
	        Button b = (Button)ll.findViewById(R.id.more_button);
	        b.setOnClickListener(new OnClickListener() {
				public void onClick(View v) {
					new AsyncTask<Void, Void, ArrayList<QueryResultModel>>() {
						protected ArrayList<QueryResultModel> doInBackground(Void... arg0) {
							ArrayList<QueryResultModel> newResults = RPInfoAPI.getInstance().request(a.getSearchTerm(), a.getPage(), RPInfoAPI.DEFAULT_NUM_RESULTS);
							return newResults;
						}
						
						protected void onPostExecute(ArrayList<QueryResultModel> newResults) {
							a.loadNextPage( newResults );
						}
					}.execute();
				}
			});
	      
	        lv.addFooterView(ll);
	        lv.setAdapter(a);
	        
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
