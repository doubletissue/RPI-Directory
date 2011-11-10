package org.rpi.rpinfo.QueryView;

import java.util.ArrayList;
import java.util.List;

import org.json.JSONObject;
import org.rpi.rpinfo.R;
import org.rpi.rpinfo.R.id;
import org.rpi.rpinfo.R.layout;

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
	private String searchTerm;
	private List<QueryResultModel> representation;
	private int page = RPInfoAPI.FIRST_PAGE;
	
	public QueryResultArrayAdapter(Context context, int textViewResourceId,
			List<QueryResultModel> objects, String searchTerm ) {
		super(context, textViewResourceId, objects);
				
		//Hold on to this for later
		this.searchTerm = searchTerm;
		this.representation = objects;	
	}
	
	public String getSearchTerm(){
		return searchTerm;
	}
	
	/**
	 * Increment the page and return the new page 
	 * 
	 * @return The next page
	 */
	public int nextPage(){
		page += 1;
		return page;
	}

	/**
	 * Add some more results to the list
	 * 
	 * @param newResults An ArrayList of QueryResultModels 
	 */
	public void addData(ArrayList<QueryResultModel> newResults){
		/*
		 * This is hacky and terrible, and it should work the proper way but it doesn't!
		 * The proper way would be to use the add function that is inherited from the parent class,
		 * rather than change the underlying data structure.
		 */
		this.representation.addAll(newResults);
		this.notifyDataSetChanged();
		this.notifyDataSetInvalidated();
	}
		
	public View getView(int position, View oldView, ViewGroup parent) {
		View newView = oldView;
						
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
			TextView major = (TextView)newView.findViewById(R.id.query_result_department);

			if( name != null ){
				String nameData = (String)model.getElement("name","N/A");
				name.setText(nameData);
			}
			if( email != null ){
				String emailData = (String)model.getElement("email","N/A");
				email.setText(emailData);
			}
			if( year != null ){
				String yearData = (String)model.getElement("year",null);
				//If the person doesn't have a year, is probably faculty or staff and therefore has a title
				if( yearData == null ){
					yearData = (String)model.getElement("title", "N/A");
				}
				year.setText(yearData);
			}
			if( major != null ){
				String majorData = (String)model.getElement("major",null);
				//If the person doesn't have a major, is probably faculty or staff and therefore has a department
				if( majorData == null ){
					majorData = (String)model.getElement("department","N/A");
				}
				major.setText(majorData);
			}
		}
		
		return newView;
	}

}
