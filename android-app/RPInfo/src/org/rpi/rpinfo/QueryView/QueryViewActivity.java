package org.rpi.rpinfo.QueryView;

import org.rpi.rpinfo.R;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.TextView;

public class QueryViewActivity extends Activity {
	private static final String TAG = "DataDisplayerActivity";
	private ResultsListManager resultsList = null;
	
	public boolean onCreateOptionsMenu(Menu menu){
		MenuInflater infalter = getMenuInflater();
		infalter.inflate(R.layout.query_view_menu, menu);
		return true;
	}
	
	public boolean onOptionsItemSelected(MenuItem item){
		switch( item.getItemId() ){
			case R.id.about_button: return this.showAbout();
		}
		return true;
	}
	
	private Boolean showAbout(){
		AlertDialog.Builder builder = new AlertDialog.Builder(this);
		builder.setMessage(getResources().getString(R.string.about));
		builder.setNeutralButton("Okay", new DialogInterface.OnClickListener() {
			public void onClick(DialogInterface dialog, int which) {
				dialog.cancel();
			}
		});
		builder.show();
		
		return true;
	}
	
	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        resultsList = new ResultsListManager(this);
        
        setContentView(R.layout.data_view);
         
        //This is where the search term is entered
        final EditText searchBox = (EditText)findViewById(R.id.searchBox);
        /*
        final Button submitSearch = (Button)findViewById(R.id.submit);
        
        submitSearch.setOnClickListener(new OnClickListener() {
			public void onClick(View v) {
				if( searchBox.getText().length() > 0 ){
					resultsList.update( searchBox.getText().toString() );
				}
			}
		});
		*/
        
        final TextView tv = (TextView)findViewById(R.id.instructions_text);

        //Automatically populate the results while the user types 
        searchBox.addTextChangedListener(new TextWatcher() {
			public void onTextChanged(CharSequence s, int start, int before, int count) {
				if( searchBox.getText().length() > 0 ){
					tv.setVisibility(View.GONE);
					resultsList.update( searchBox.getText().toString() );
				}
			}
						
			public void beforeTextChanged(CharSequence s, int start, int count, int after) {
				//Nothing
			}
			
			public void afterTextChanged(Editable s) {
				for( int i = 0; i < s.length(); ++i ){
					//Don't want any newline characters displaying 
					if( s.charAt(i) == '\n' ){
						s.delete(i, i+1);

						//Hide the keyboard, too
						InputMethodManager imm = (InputMethodManager)QueryViewActivity.this.getSystemService(Context.INPUT_METHOD_SERVICE);
						imm.hideSoftInputFromWindow(QueryViewActivity.this.getCurrentFocus().getWindowToken(), InputMethodManager.HIDE_NOT_ALWAYS);
					}
				}
			}
		});
        
	}
}