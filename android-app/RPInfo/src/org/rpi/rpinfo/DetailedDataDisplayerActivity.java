package org.rpi.rpinfo;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
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
		
		JSONObject data = selectedPerson.getAllElements();
		
		//Put the person's name in
		TextView name = (TextView)this.findViewById(R.id.person_name);
		name.setText(selectedPerson.getElement("name", "N/A"));
		
		ListView lv = (ListView)this.findViewById(R.id.data_list);
	}

}
