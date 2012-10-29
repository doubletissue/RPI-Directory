package org.rpi.rpinfo;

import java.util.ArrayList;

import org.rpi.rpinfo.api.PersonModel;
import org.rpi.rpinfo.api.RpinfoApi;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Context;
import android.content.Intent;
import android.os.AsyncTask;
import android.view.LayoutInflater;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;

public class SearchResultsListManager<ResultsListManager> {

    private static final String TAG = "SearchResultListManager";
    private static final int LIST_VIEW_RESOURCE_ID = R.id.search_result_list;
    private static final int LIST_ITEM_VIEW_RESOURCE_ID = R.layout.view_search_list_item;

    private long queryIndex = -1;
    private View moreButton = null;
    private Context context;
    private ListView listView;

    public SearchResultsListManager(Activity activity, View view) {
        this.context = activity;
        listView = (ListView) view.findViewById(LIST_VIEW_RESOURCE_ID);
    }

    public void setItems(ArrayList<PersonModel> items, String searchTerm, long currentQueryIndex) {
        // Only use a query that was made after the current one
        if (currentQueryIndex < queryIndex) {
            return;
        } else {
            queryIndex = currentQueryIndex;
        }

        SearchResultListAdapter adapter = new SearchResultListAdapter(context,
                LIST_ITEM_VIEW_RESOURCE_ID, items, searchTerm);

        // Add the more button to the bottom of the list
        addMoreButton(listView, adapter);

        listView.setAdapter(adapter);
        if (listView.getVisibility() != View.VISIBLE) {
            listView.setVisibility(View.VISIBLE);

            // If a list element is pressed
            listView.setOnItemClickListener(new OnItemClickListener() {

                @Override
                public void onItemClick(AdapterView<?> adapterView, View view, int position, long id) {
                    Intent i = new Intent(context, org.rpi.rpinfo.detail.DetailActivity.class);
                    // i.putExtra("selectedPerson", apiResult.get((int) id));
                    i.putExtra("selectedPerson",
                            (PersonModel) adapterView.getItemAtPosition((int) id));
                    context.startActivity(i);
                }
            });
        }
    }

    protected void addMoreButton(final ListView lv, final SearchResultListAdapter a) {
        // Remove the more button from the footer if it has already been place
        if (moreButton != null) {
            lv.removeFooterView(moreButton);
        }

        // Set up the bottom at the end of the list (must be done before setAdapter)
        LayoutInflater layoutInflater = (LayoutInflater) context
                .getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        LinearLayout ll = (LinearLayout) layoutInflater.inflate(
                R.layout.view_search_list_more_button, null, false);
        Button b = (Button) ll.findViewById(R.id.more_button);
        b.setOnClickListener(new OnClickListener() {
            public void onClick(View v) {
                // Most of what's going on here is to display the progress dialog
                new AsyncTask<Void, Void, ArrayList<PersonModel>>() {
                    private ProgressDialog pd;

                    protected void onPreExecute() {
                        pd = ProgressDialog.show(context, "", "Fetching more results...");
                    };

                    protected ArrayList<PersonModel> doInBackground(Void... arg0) {
                        // Get the new data
                        ArrayList<PersonModel> newResults = RpinfoApi.getInstance(
                                SearchResultsListManager.this.context).request(a.getSearchTerm(),
                                a.nextPage(), RpinfoApi.DEFAULT_NUM_RESULTS);
                        return newResults;
                    }

                    protected void onPostExecute(ArrayList<PersonModel> newResults) {
                        // Store the new data
                        a.addData(newResults);
                        pd.dismiss();
                    }
                }.execute();
            }
        });

        moreButton = ll;
        lv.addFooterView(ll);
    }

}
