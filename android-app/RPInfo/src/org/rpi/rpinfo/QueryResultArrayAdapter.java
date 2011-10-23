package org.rpi.rpinfo;

import java.util.List;

import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class QueryResultArrayAdapter extends ArrayAdapter<QueryResultModel> {
	private static final String TAG = "QueryResultArrayAdapter";
	//private List<QueryResultModel> models; 
	private Context context;
	
	public QueryResultArrayAdapter(Context context, int textViewResourceId,
			List<QueryResultModel> objects) {
		super(context, textViewResourceId, objects);
				
		//Hold on to these for later
		//this.models = objects;
		this.context = context;
	}
		
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
				
		//If we're at the end of the list, better start getting more data!
		if( position == this.getCount() - 1 ){
			//Load the next page
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
				year.setText((String)model.getElement("class","N/A"));
			}
			if( department != null ){
				department.setText((String)model.getElement("major","N/A"));
			}
		}
		
		return newView;
	}

}
