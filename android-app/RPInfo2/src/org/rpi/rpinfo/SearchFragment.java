package org.rpi.rpinfo;

import java.util.ArrayList;

import org.rpi.rpinfo.api.PersonModel;
import org.rpi.rpinfo.api.RpinfoApi;
import org.rpi.rpinfo.util.QueryDispatcher;

import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Handler;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;

public class SearchFragment extends Fragment {
    /**
     * Number of milliseconds between subsequent checks of searchBar
     */
    private static final long INPUT_POLLING_DELAY = 300;
    private static final String TAG = "SearchFragment";

    private long queryCounter = 0;
    private EditText searchBar;
    private SearchResultsListManager<PersonModel> searchResultsListManager;
    private QueryDispatcher queryDispatcher;
    private Handler queryDispatcherHandler;
    private Runnable queryDispatcherRunnableWrapper;
    private RpinfoApi rpinfoApi;

    public SearchFragment() {
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        rpinfoApi = RpinfoApi.getInstance(getActivity());
        View rootView = inflater.inflate(R.layout.fragment_search_bar, container, false);
        searchBar = (EditText) rootView.findViewById(R.id.search_bar);
        searchResultsListManager = new SearchResultsListManager(getActivity(), rootView);
        return rootView;
    }

    @Override
    public void onResume() {
        super.onResume();
        queryDispatcher = new QueryDispatcher(this);
        queryDispatcherHandler = new Handler();
        queryDispatcherRunnableWrapper = new Runnable() {

            @Override
            public void run() {
                // Potentially exeucte a query
                queryDispatcher.run();
                // Queue up another polling of the EditText
                queryDispatcherHandler.postDelayed(queryDispatcherRunnableWrapper,
                        INPUT_POLLING_DELAY);
            };
        };
        // Queue up the first polling of the EditText
        queryDispatcherHandler.postDelayed(queryDispatcherRunnableWrapper, INPUT_POLLING_DELAY);
    }

    @Override
    public void onPause() {
        super.onPause();
        if (queryDispatcherHandler != null) {
            // Stop polling the EditText when the fragment is paused.
            queryDispatcherHandler.removeCallbacks(queryDispatcherRunnableWrapper);
        }
    }

    public String getText() {
        return searchBar.getText().toString();
    }

    public void doSearchCallback() {
        new AsyncTask<Void, Void, ArrayList<PersonModel>>() {

            private String queryString;

            @Override
            protected void onPreExecute() {
                queryString = getText();
                getActivity().setProgressBarIndeterminateVisibility(true);
            }

            @Override
            protected ArrayList<PersonModel> doInBackground(Void... params) {
                return rpinfoApi.request(queryString, RpinfoApi.FIRST_PAGE,
                        RpinfoApi.DEFAULT_NUM_RESULTS);
            };

            protected void onPostExecute(java.util.ArrayList<PersonModel> people) {
                searchResultsListManager.setItems(people, queryString, ++queryCounter);
                getActivity().setProgressBarIndeterminateVisibility(false);
            }

        }.execute();
    }
}
