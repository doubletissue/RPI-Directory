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
import android.content.OperationApplicationException;
import android.net.Uri;
import android.os.Bundle;
import android.os.RemoteException;
import android.provider.ContactsContract;
import android.provider.ContactsContract.CommonDataKinds.StructuredName;
import android.provider.ContactsContract.Data;
import android.provider.ContactsContract.RawContacts;
import android.text.Html;
import android.text.Spanned;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.AdapterView.OnItemClickListener;

public class DetailedViewActivity extends Activity {
	private static final String TAG = "DetailedDataDisplayerActivity"; 
	private PersonModel selectedPerson;
	private static String ACCOUNT_TYPE = "org.rpi.rpinfo";
	
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
			case R.id.add_contacts_button: return addToContacts();
		}
		return true;
	}
	
	/**
	 * Add the selected person to ones contacts
	 */
	private boolean addToContacts(){
		ArrayList<ContentProviderOperation> ops = new ArrayList<ContentProviderOperation>();

		//Backreference value. Don't need to do anything to it.
		int contact_index = 0;
		
		//Use the RCS ID as a unique account identifier
		String accountName = selectedPerson.getElement("rcsid", null);
		if( accountName != null ){
			ops.add(ContentProviderOperation.newInsert(RawContacts.CONTENT_URI)
				.withValue(RawContacts.ACCOUNT_TYPE, null)
				.withValue(RawContacts.ACCOUNT_NAME, null)
				.build());
		} else {
			Log.i(TAG, "Person does not have an RCS id. Cannot add to contacts.");
			return false;
		}
		
		String personName = selectedPerson.getElement("name", null);
		if( personName != null ){
			ops.add(ContentProviderOperation.newInsert(ContactsContract.Data.CONTENT_URI)
					.withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
					.withValue(ContactsContract.Data.MIMETYPE, ContactsContract.CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE)
					.withValue(ContactsContract.CommonDataKinds.StructuredName.DISPLAY_NAME, personName)
					.build());
		} else {
			Log.i(TAG, "Person does not have a name.");
		}
		
		String personEmail = selectedPerson.getElement("email", null);
		if( personEmail != null ){
			ops.add(ContentProviderOperation.newInsert(ContactsContract.Data.CONTENT_URI)
					.withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
					.withValue(ContactsContract.Data.MIMETYPE, ContactsContract.CommonDataKinds.Email.CONTENT_ITEM_TYPE)
					.withValue(ContactsContract.CommonDataKinds.Email.TYPE, ContactsContract.CommonDataKinds.Email.TYPE_WORK)
					.withValue(ContactsContract.CommonDataKinds.Email.DATA1, personEmail)
					.build());
		} else {
			Log.i(TAG, "Person does not have a e-mail address.");
		}
		
		String personPhoneNumber = selectedPerson.getElement("email", null);
		if( personEmail != null ){
			ops.add(ContentProviderOperation.newInsert(ContactsContract.Data.CONTENT_URI)
					.withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
					.withValue(ContactsContract.Data.MIMETYPE, ContactsContract.CommonDataKinds.Phone.CONTENT_ITEM_TYPE)
					.withValue(ContactsContract.CommonDataKinds.Phone.TYPE, ContactsContract.CommonDataKinds.Phone.TYPE_WORK)
					.withValue(ContactsContract.CommonDataKinds.Phone.NUMBER, personPhoneNumber)
					.build());
		} else {
			Log.i(TAG, "Person does not have a phone number.");
		}
		
		String personWebsite = selectedPerson.getElement("homepage", null);
		if( personWebsite != null ){
			ops.add(ContentProviderOperation.newInsert(ContactsContract.Data.CONTENT_URI)
					.withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
					.withValue(ContactsContract.Data.MIMETYPE, ContactsContract.CommonDataKinds.Website.CONTENT_ITEM_TYPE)
					.withValue(ContactsContract.CommonDataKinds.Website.TYPE, ContactsContract.CommonDataKinds.Website.TYPE_HOMEPAGE)
					.withValue(ContactsContract.CommonDataKinds.Website.URL, personWebsite)
					.build());
		} else {
			Log.i(TAG, "Person does not have a website.");
		}
		
		try {
			getContentResolver().applyBatch(ContactsContract.AUTHORITY, ops);
		} catch (RemoteException e) {
			e.printStackTrace();
		} catch (OperationApplicationException e) {
			e.printStackTrace();
		}
		
		Toast.makeText(this, "Added to contacts.", Toast.LENGTH_SHORT).show();
		
		return true;
	}	

}
