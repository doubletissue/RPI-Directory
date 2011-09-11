package org.rpi.rpinfo;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

import android.app.ListActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class DataDisplayerActivity extends ListActivity {
	
	/** 
	 * @param in An input stream.
	 * @return String containing everything that was in the input stream.
	 */
	private String readInputStream(InputStream in){
		try {
			String result = "";
			byte[] buffer = new byte[1024];
			
			//Loop until there is nothing left in the stream
			while( in.available() > 0 ){
				//Only write to the string the number of bytes read
				int num_read = in.read(buffer, 0, buffer.length);
				result = result + new String(buffer, 0, num_read);
			}
			
			return result;
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return null;
	}

	public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        ArrayList<QueryResultModel> list_items = new ArrayList<QueryResultModel>();
        list_items.add(new QueryResultModel("1","Benoid Mandelbrot","mandeb@rpi.edu","Senior","MATH/CSCI"));
        list_items.add(new QueryResultModel("2","Andre Weil","weila3@rpi.edu","Sophomore", "MATH"));
        list_items.add(new QueryResultModel("3","Thomas Bayes","bayest4@rpi.edu","Junior", "MATH"));
        list_items.add(new QueryResultModel("4","Edsger Dijkstra","dijkse2@rpi.edu","Senior", "CSCI"));
        list_items.add(new QueryResultModel("5","Blaise Pascal","pascab@rpi.edu","Freshman", "MATH"));
        list_items.add(new QueryResultModel("6","Rene Descartes","descar14@rpi.edu","Junior", "PHIL/MATH"));
        list_items.add(new QueryResultModel("7","Edward Teller","tellee@rpi.edu","Freshman", "PHYS"));
        list_items.add(new QueryResultModel("8","Raymond Smullyan","smullr@rpi.edu","Junior", "PHIL"));
        setListAdapter(new QueryResultArrayAdapter(this, R.layout.query_result_list_item, list_items));
              
        ListView lv = getListView();
        lv.setOnItemClickListener(new OnItemClickListener(){
			public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
				TextView name = (TextView) view.findViewById(R.id.query_result_name);
				Toast.makeText(getApplicationContext(), name.getText(), Toast.LENGTH_SHORT).show();
			}
        });
                
        /*
		Bundle b = getIntent().getExtras();
		if( b == null ){
			finish();
		}
		
		String searchTerm = (String)b.get("searchTerm");
		
		try {
			URL apiURL = new URL("rpidirectory.appspot.com/api?name=" + searchTerm);
			URLConnection connection = apiURL.openConnection();
			InputStream in = new BufferedInputStream(connection.getInputStream());
		} catch (MalformedURLException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		*/
		
	}
}