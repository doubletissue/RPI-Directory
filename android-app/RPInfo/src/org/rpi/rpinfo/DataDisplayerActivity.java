package org.rpi.rpinfo;

import android.app.Activity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;

public class DataDisplayerActivity extends Activity {
	private static final String TAG = "DataDisplayerActivity";
	private ResultsListManager resultsList = null;
	
	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        resultsList = new ResultsListManager(this);
        
        setContentView(R.layout.data_view);
                
        //final Button submitButton = (Button)findViewById(R.id.submit);
        final EditText searchBox = (EditText)findViewById(R.id.searchBox);
        
        //Automatically populate the results while the user types 
        searchBox.addTextChangedListener(new TextWatcher() {
			
			public void onTextChanged(CharSequence s, int start, int before, int count) {
				if( searchBox.getText().length() > 0 ){
					resultsList.update( searchBox.getText().toString() );
				}
			}
						
			public void beforeTextChanged(CharSequence s, int start, int count,
					int after) {
				//Nothing
			}
			
			public void afterTextChanged(Editable s) {
				//Nothing
			}
		});
                
        /*
         * Manually populate the results when the user requests it
         */
        /*
        submitButton.setOnClickListener(new OnClickListener() {
			public void onClick(View v){
				resultsList.update( searchBox.getText().toString() );
			}
		});
		*/
	}
}