package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.Map;
import java.util.Map.Entry;

import android.app.Activity;
import android.os.Bundle;
import android.text.Html;
import android.text.Spanned;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;

public class DetailedDataDisplayerActivity extends Activity {
	/*
	 * Format the field name to display correctly
	 */
	private String formatField( String field ){
		String rv = "";
		
		//If empty string, can't do much
		if( field.length() == 0 ){
			return field;
		}
		
		//The return value should contain everything after the first character
		if( field.length() > 1 ){
			rv = field.substring(1);
		}
				
		rv = Character.toUpperCase(field.charAt(0)) + rv;
		
		return rv;
	}
	
	/*
	 * Format the value to display correctly
	 */
	private String formatValue( String field, String value ){
		return value;
	}
	
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
		//Spanned is like a string but it can contain formatting data and such
		ArrayList<Spanned> parsed_data = new ArrayList<Spanned>();
		for( Entry<String, String> entry : raw_data.entrySet() ){
			if( !entry.getKey().equals("name") ){
				//Make the name of the field bold
				parsed_data.add( Html.fromHtml("<b>" + formatField( entry.getKey() ) + "</b>: " + formatValue( entry.getKey(), entry.getValue() ) ) );
			}
		}
		
		//Put the person's name in
		TextView name = (TextView)this.findViewById(R.id.person_name);
		name.setText(selectedPerson.getElement("name", "N/A"));
		
		//Set up the list view
		ListView lv = (ListView)this.findViewById(R.id.data_list);
		lv.setAdapter(new ArrayAdapter<Spanned>(this, R.layout.detailed_view_list_item, parsed_data));
	}

}
