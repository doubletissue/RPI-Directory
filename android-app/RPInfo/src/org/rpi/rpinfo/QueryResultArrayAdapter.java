package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.List;

import android.content.Context;
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
	private Context context;
	private String searchTerm;
	private int page = 1;
	
	public QueryResultArrayAdapter(Context context, int textViewResourceId,
			List<QueryResultModel> objects, String searchTerm ) {
		super(context, textViewResourceId, objects);
				
		//Hold on to these for later
		this.context = context;
		this.searchTerm = searchTerm;
	}
	
	public String getSearchTerm(){
		return searchTerm;
	}
	
	public int getPage(){
		return page;
	}
	
	public void loadNextPage(ArrayList<QueryResultModel> newResults){
		//Load the next page
		page += 1;
		for( QueryResultModel result : newResults ){						
			add(result);
		}
	}
	
	/*
	public int getCount() {
		return super.getCount() + 1;
	}
	*/
	
	public View getView(int position, View oldView, ViewGroup parent) {
		View newView = oldView;
				
		/*
		 * OldView is the previously displayed view - if possible, re-use it for efficiency.
		 * If it doesn't exist, make a new one.
		 */
		if(newView == null){
			LayoutInflater inflater = (LayoutInflater)context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
			newView = inflater.inflate(R.layout.query_result_list_item, null);
		}
		
		/*
		if( position == getCount() - 1 ){

	        return ll;
		}
		*/
			
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
