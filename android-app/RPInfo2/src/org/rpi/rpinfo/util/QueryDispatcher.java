package org.rpi.rpinfo.util;

import org.rpi.rpinfo.SearchBarFragment;

import android.os.AsyncTask;

/**
 * Handle when queries will be sent out.
 */
public class QueryDispatcher implements Runnable {
    private SearchBarFragment searchBarFragment;
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

    public QueryDispatcher(SearchBarFragment searchBarFragment) {
        this.searchBarFragment = searchBarFragment;
    }

    @Override
    public void run() {
        String current = searchBarFragment.getText();

        // If the string is the same twice in a row, assume the user has stopped typing.
        if (prev.equals(current) && !current.equals("")) {
            if (!isUiUpdated) {
                new UiUpdater(searchBarFragment, currentId).execute();
                currentId += 1;
            }
            isUiUpdated = true;
        } else {
            isUiUpdated = false;
        }
        prev = current;
    }

    private class UiUpdater extends AsyncTask<Void, Void, Void> {
        private SearchBarFragment searchBarFragment;
        private int id;

        UiUpdater(SearchBarFragment searchBarFragment, int id) {
            this.searchBarFragment = searchBarFragment;
            this.id = id;
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            synchronized (QueryDispatcher.this.minId) {
                if (id >= QueryDispatcher.this.minId) {
                    searchBarFragment.doSearchCallback();
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