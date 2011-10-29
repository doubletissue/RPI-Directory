package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.List;

import org.json.JSONObject;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.View.OnClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class QueryResultArrayAdapter extends ArrayAdapter<QueryResultModel> {
	private static final String TAG = "QueryResultArrayAdapter";
	//private List<QueryResultModel> models; 
	private String searchTerm;
	private List<QueryResultModel> representation;
	private int page = RPInfoAPI.FIRST_PAGE;
	private View moreButton = null;
	
	public QueryResultArrayAdapter(Context context, int textViewResourceId,
			List<QueryResultModel> objects, String searchTerm ) {
		super(context, textViewResourceId, objects);
				
		//Hold on to this for later
		this.searchTerm = searchTerm;
		this.representation = objects;	
		
        //Set up the bottom at the end of the list (must be done before setAdapter)
        LayoutInflater layoutInflater = (LayoutInflater)context.getSystemService( Context.LAYOUT_INFLATER_SERVICE );
        moreButton = (LinearLayout)layoutInflater.inflate(R.layout.query_result_list_more_button, null, false);
        Button b = (Button)moreButton.findViewById(R.id.more_button);
        b.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				new AsyncTask<Void, Void, ArrayList<QueryResultModel>>() {
					private ProgressDialog pd;

					protected void onPreExecute() {
						pd = ProgressDialog.show(getContext(), "", "Fetching more results...");
					};
					
					protected ArrayList<QueryResultModel> doInBackground(Void... arg0) {
						ArrayList<QueryResultModel> newResults = RPInfoAPI.getInstance().request(getSearchTerm(), nextPage(), RPInfoAPI.DEFAULT_NUM_RESULTS);
						return newResults;
					}
					
					protected void onPostExecute(ArrayList<QueryResultModel> newResults) {
						addData( newResults );
						pd.dismiss();
					}
				}.execute();
			}
		});
	}
	
	public String getSearchTerm(){
		return searchTerm;
	}
	
	public int nextPage(){
		page += 1;
		return page;
	}

	public void addData(ArrayList<QueryResultModel> newResults){
		//for( int i = 0; i < newResults.size(); ++i ){
		/*
		for( QueryResultModel result : newResults ){
			Log.i(TAG, "Adding");
			this.add(result);
			Log.i(TAG, "Added");
		}
		*/
		//This is hacky and terrible, and it should work the proper way but it doesn't!
		this.representation.addAll(newResults);
		this.notifyDataSetChanged();
		this.notifyDataSetInvalidated();
	}
	
	public int getCount() {
		return super.getCount() + 1;
	}
	
	public View getView(int position, View oldView, ViewGroup parent) {
		View newView = oldView;
		
		if( position == getCount() - 1){
			Log.i(TAG, "Position: " + position);
			return moreButton;
		}
				
		/*
		 * OldView is the previously displayed view - if possible, re-use it for efficiency.
		 * If it doesn't exist, make a new one.
		 */
		if(newView == null){
			LayoutInflater inflater = (LayoutInflater)getContext().getSystemService(Context.LAYOUT_INFLATER_SERVICE);
			newView = inflater.inflate(R.layout.query_result_list_item, null);
		}
			
		//Get the current from the array
		//QueryResultModel model = this.models.get(position);
		QueryResultModel model = this.getItem(position);
		
		//Fill the view with all of the data
		if(model != null){
			TextView name = (TextView)newView.findViewById(R.id.query_result_name);
			TextView email = (TextView)newView.findViewById(R.id.query_result_email);
			TextView year = (TextView)newView.findViewById(R.id.query_result_year);
			TextView department = (TextView)newView.findViewById(R.id.query_result_department);

			if( name != null ){
				name.setText((String)model.getElement("name","N/A"));
			}
			if( email != null ){
				email.setText((String)model.getElement("email","N/A"));
			}
			if( year != null ){
				year.setText((String)model.getElement("year","N/A"));
			}
			if( department != null ){
				department.setText((String)model.getElement("major","N/A"));
			}
		}
		
		return newView;
	}

}
