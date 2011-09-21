package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.Map;
import java.util.Map.Entry;

import org.json.JSONObject;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

public class DetailedDataDisplayerActivity extends Activity {
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		setContentView(R.layout.detailed_data_view);
		
		Bundle b = getIntent().getExtras();
		if( b == null ){
			finish();
		}
		
		//Extract the selected person from the intent
		QueryResultModel selectedPerson = (QueryResultModel)b.getSerializable("selectedPerson");
		if( selectedPerson == null ){
			finish();
		}
				
		//Extract the data from the selected person and prepare to put it into a nice list view
		Map<String, String> raw_data = selectedPerson.getAllElements();
		ArrayList<String> parsed_data = new ArrayList<String>();
		for( Entry<String, String> entry : raw_data.entrySet() ){
			if( !entry.getKey().equals("Name") ){
				parsed_data.add( entry.getKey() + ": " + entry.getValue() );
			}
		}
		
		//Put the person's name in
		TextView name = (TextView)this.findViewById(R.id.person_name);
		name.setText(selectedPerson.getElement("name", "N/A"));
		
		//Set up the list view
		ListView lv = (ListView)this.findViewById(R.id.data_list);
		lv.setAdapter(new ArrayAdapter<String>(this, R.layout.detailed_view_list_item, parsed_data));
	}

}
