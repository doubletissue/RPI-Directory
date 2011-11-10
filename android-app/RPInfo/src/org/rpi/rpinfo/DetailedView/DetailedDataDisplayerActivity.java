package org.rpi.rpinfo.DetailedView;

import java.util.ArrayList;
import java.util.Map;
import java.util.Map.Entry;

import org.rpi.rpinfo.R;
import org.rpi.rpinfo.QueryView.QueryResultModel;
import org.rpi.rpinfo.R.id;
import org.rpi.rpinfo.R.layout;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.text.Html;
import android.text.Spanned;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.AdapterView.OnItemClickListener;

public class DetailedDataDisplayerActivity extends Activity {
	private static final String TAG = "DetailedDataDisplayerActivity"; 
		
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
		
		ArrayList<DetailedResultModel> models = DetailedResultModel.generateModels(selectedPerson.getAllElements());
				
		/*
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
		*/
		
		//Put the person's name in
		TextView name = (TextView)this.findViewById(R.id.person_name);
		name.setText(selectedPerson.getElement("name", "N/A"));
		
		//Set up the list view
		ListView lv = (ListView)this.findViewById(R.id.data_list);
		lv.setAdapter(new ArrayAdapter<DetailedResultModel>(this, R.layout.detailed_view_list_item, models));
		
        //If a list element is pressed
        lv.setOnItemClickListener(new OnItemClickListener(){
        	public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        		//String key = parent.getAdapter().getItem(position)
				/*
				Intent i = new Intent(DetailedDataDisplayerActivity.this, DetailedDataDisplayerActivity.class);
				i.putExtra("selectedPerson", apiResult.get((int) id));
				this.startActivity(i);
				*/
			}
        });
	}

}
