package org.rpi.rpinfo.QueryView;

import org.rpi.rpinfo.R;

public class ResultsListManager {
    /**
     * Relate a search term to the time when it was searched
     */
    private class SearchTermData {
        public SearchTermData(String searchTerm, Date searchDate) {
            this.searchTerm = searchTerm;
            this.searchDate = searchDate;
        }

        public String searchTerm;
        public Date searchDate;
    }

    private static final String TAG = "ResultsListManager";
    private static View moreButton = null;
    private Date currentUpdate = new Date();
    private Activity context = null;
    // Keep track of search terms so that they can be buffered
    private LinkedList<SearchTermData> searchTerms = new LinkedList<SearchTermData>();
    // Lock for the searchTerms list
    private Object searchTermsLock = new Object();
    // Lock for searching
    private Object searchLock = new Object();
    // Lock for updating
    private static final Object currentUpdateLock = new Object();

    public ResultsListManager(Activity context) {
        this.context = context;
    }

    private void setCurrentUpdate(Date newCurrentUpdate) {
        synchronized (currentUpdateLock) {
            currentUpdate = newCurrentUpdate;
        }
    }

    private Date getCurrentUpdate() {
        synchronized (currentUpdateLock) {
            return this.currentUpdate;
        }
    }

    private SearchTermData getNextSearchTerm() {
        synchronized (searchTermsLock) {
            return searchTerms.removeFirst();
        }
    }

    // Perform the actual update asynchronously
    private class DoUpdate extends AsyncTask<Void, Void, ArrayList<PersonModel>> {
        private SearchTermData searchTermData = null;

        protected void onPreExecute() {
        }

        protected ArrayList<PersonModel> doInBackground(Void... params) {
            if (searchTerms.size() == 0) {
                return null;
            }

            synchronized (searchLock) {
                searchTermData = getNextSearchTerm();
            }

            if (searchTermData.searchTerm.length() <= 2) {
                try {
                    // Log.i(TAG, "Waiting...");
                    Thread.sleep(500);
                    // Log.i(TAG, "Done!");
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }

            ArrayList<PersonModel> apiResult = null;

            // Log.i(TAG, "Next Term: " + searchTermData.searchTerm);

            // Get the JSON output from the api
            apiResult = RPInfoAPI.getInstance(ResultsListManager.this.context).request(
                    searchTermData.searchTerm, RPInfoAPI.FIRST_PAGE, RPInfoAPI.DEFAULT_NUM_RESULTS);

            return apiResult;
        }

        protected void addMoreButton(final ListView lv, final ResultsListArrayAdapter a) {
            // Remove the more button from the footer if it has already been place
            if (moreButton != null) {
                lv.removeFooterView(moreButton);
            }

            // Set up the bottom at the end of the list (must be done before setAdapter)
            LayoutInflater layoutInflater = (LayoutInflater) context
                    .getSystemService(Context.LAYOUT_INFLATER_SERVICE);
            LinearLayout ll = (LinearLayout) layoutInflater.inflate(
                    R.layout.query_result_list_more_button, null, false);
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
                            ArrayList<PersonModel> newResults = RPInfoAPI.getInstance(
                                    ResultsListManager.this.context).request(a.getSearchTerm(),
                                    a.nextPage(), RPInfoAPI.DEFAULT_NUM_RESULTS);
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

        protected void onPostExecute(final ArrayList<PersonModel> apiResult) {
            /*
             * If this was not the most recently started update or there is no api result, there
             * isn't much that we can do.
             */
            // Log.i(TAG, "" + getCurrentUpdate().getTime() + " " + updateStart.getTime() );
            if (getCurrentUpdate() != searchTermData.searchDate || apiResult == null) {
                return;
            }

            // Set up the list view (where the results are displayed)
            final ListView lv = (ListView) context.findViewById(R.id.data_list);
            final ResultsListArrayAdapter a = new ResultsListArrayAdapter(context,
                    R.layout.query_result_list_item, apiResult, searchTermData.searchTerm);

            // Add the more button to the bottom of the list
            addMoreButton(lv, a);

            lv.setAdapter(a);

            // If a list element is pressed
            lv.setOnItemClickListener(new OnItemClickListener() {
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    Intent i = new Intent(context,
                            org.rpi.rpinfo.DetailedView.DetailedViewActivity.class);
                    i.putExtra("selectedPerson", apiResult.get((int) id));
                    context.startActivity(i);
                }
            });
        }
    }

    /**
     * Wrapper for AsyncTask DoUpdate
     */
    public void update(String searchTerm) {
        /*
         * //If only searching for one character, give the user time to enter more characters if(
         * searchTerm.length() <= 2){ try { Log.i(TAG, "Waiting..."); Thread.sleep(3000); Log.i(TAG,
         * "Done!"); } catch (InterruptedException e) { e.printStackTrace(); } }
         */

        synchronized (searchTermsLock) {
            Date thisUpdate = new Date();
            // Set the current item as the next search (for speed)
            searchTerms.addFirst(new SearchTermData(searchTerm, thisUpdate));
            // Set the current update time to be the one that is actually rendered
            setCurrentUpdate(thisUpdate);
        }

        // Log.i(TAG, searchTerm);

        new DoUpdate().execute();
    }
}
