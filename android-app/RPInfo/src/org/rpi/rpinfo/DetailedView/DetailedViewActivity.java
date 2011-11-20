package org.rpi.rpinfo.DetailedView;

import java.util.ArrayList;
import java.util.Map;
import java.util.Map.Entry;

import org.rpi.rpinfo.R;
import org.rpi.rpinfo.QueryView.PersonModel;
import org.rpi.rpinfo.R.id;
import org.rpi.rpinfo.R.layout;

import android.app.Activity;
import android.content.ContentProviderOperation;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.text.Html;
import android.text.Spanned;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.AdapterView.OnItemClickListener;

public class DetailedViewActivity extends Activity {
	private static final String TAG = "DetailedDataDisplayerActivity"; 
	private PersonModel selectedPerson;
	
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		setContentView(R.layout.detailed_data_view);
		
		Bundle b = getIntent().getExtras();
		if( b == null ){
			finish();
		}
		
		//Extract the selected person from the intent
		selectedPerson = (PersonModel)b.getSerializable("selectedPerson");
		if( selectedPerson == null ){
			finish();
		}
						
		ArrayList<DetailedResultModel> models = DetailedResultModel.generateModels(selectedPerson.getAllElements());
		
		//Put the person's name in
		TextView name = (TextView)this.findViewById(R.id.person_name);
		name.setText(selectedPerson.getElement("name", "N/A"));
		
		//Set up the list view
		ListView lv = (ListView)this.findViewById(R.id.data_list);
		lv.setAdapter(new DetailedListArrayAdapter(this, R.layout.detailed_view_list_item, models));
		
        //If a list element is pressed
        lv.setOnItemClickListener(new OnItemClickListener(){
        	public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
        		DetailedResultModel model = (DetailedResultModel)parent.getAdapter().getItem(position);
        		String key = model.getRawKey();
        		if( key.equals("phone") ){
    				Log.i(TAG, "Calling" + model.getValue());
    				Intent intent = new Intent(android.content.Intent.ACTION_VIEW, Uri.parse("tel:" + model.getValue()));
    				startActivity(intent);
        		} else if( key.equals("email") ) {
    				Log.i(TAG, "Sending email to " + model.getValue());
        			Intent intent = new Intent(android.content.Intent.ACTION_SEND);
        			intent.setType("message/rfc822");
        			intent.putExtra(android.content.Intent.EXTRA_EMAIL, new String[]{model.getValue()});
        			startActivity(Intent.createChooser(intent, "Send email..."));
        		}
			}
        });
	}
	
	public boolean onCreateOptionsMenu(Menu menu){
		MenuInflater infalter = getMenuInflater();
		infalter.inflate(R.layout.detailed_view_menu, menu);
		return true;
	}
	
	public boolean onOptionsItemSelected(MenuItem item){
		switch( item.getItemId() ){
			case R.id.add_contacts_button: 
		}
		return true;
	}
	
	/**
	 * Add the selected person to ones contacts
	 */
	private void addToContacts(){
		ArrayList<ContentProviderOperation> operations = new ArrayList<ContentProviderOperation>();
	}

}
