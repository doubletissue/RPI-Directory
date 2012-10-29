package org.rpi.rpinfo.util;

import org.rpi.rpinfo.SearchFragment;

import android.os.AsyncTask;

/**
 * Handle when queries will be sent out.
 */
public class QueryDispatcher implements Runnable {
    private SearchFragment searchFragment;
    /**
     * The next ID to use.
     */
    private int currentId = 0;
    /**
     * The minimum ID to accept of a completed task.
     */
    private Integer minId = 0;
    private String prev = "";
    /**
     * Whether or not the UI has been updated for a given current/prev match.
     */
    private boolean isUiUpdated = false;

    public QueryDispatcher(SearchFragment searchFragment) {
        this.searchFragment = searchFragment;
    }

    @Override
    public void run() {
        String current = searchFragment.getText();

        // If the string is the same twice in a row, assume the user has stopped typing.
        if (prev.equals(current) && !current.equals("")) {
            if (!isUiUpdated) {
                new UiUpdater(searchFragment, currentId).execute();
                currentId += 1;
            }
            isUiUpdated = true;
        } else {
            isUiUpdated = false;
        }
        prev = current;
    }

    private class UiUpdater extends AsyncTask<Void, Void, Void> {
        private SearchFragment searchFragment;
        private int id;

        UiUpdater(SearchFragment searchFragment, int id) {
            this.searchFragment = searchFragment;
            this.id = id;
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            synchronized (QueryDispatcher.this.minId) {
                if (id >= QueryDispatcher.this.minId) {
                    searchFragment.doSearchCallback();
                    QueryDispatcher.this.minId = id;
                }
            }
        }

        @Override
        protected Void doInBackground(Void... params) {
            return null;
        }
    }
}