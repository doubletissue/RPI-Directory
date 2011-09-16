package org.rpi.rpinfo;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
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
		
		/* Dummy functionality until something nice can be put here */
		
		TextView name = (TextView)this.findViewById(R.id.detailed_name);
		name.setText((String)selectedPerson.getElement("name","N/A"));
	}

}
