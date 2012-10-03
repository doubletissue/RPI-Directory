package org.rpi.rpinfo.util;

import org.rpi.rpinfo.SearchBarFragment;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;

/**
 * Handle when queries will be sent out.
 */
public class QueryDispatcher implements Runnable {
    private Context context;
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

    public QueryDispatcher(Context context, SearchBarFragment searchBarFragment) {
        this.context = context;
        this.searchBarFragment = searchBarFragment;
    }

    @Override
    public void run() {
        String current = searchBarFragment.getText();
        Log.d("RPINFO", "Prev: " + prev + " Current: " + current);

        // If the string is the same twice in a row, assume the user has stopped typing.
        if (prev.equals(current) && !current.equals("")) {
            new UiUpdater(context, currentId).execute();
            currentId += 1;
        }
        prev = current;
    }

    private class UiUpdater extends AsyncTask<Void, Void, Void> {
        private Context context;
        private int id;

        UiUpdater(Context context, int id) {
            this.context = context;
            this.id = id;
            Log.d("RPINFO", "Pre-execute!");
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            synchronized (QueryDispatcher.this.minId) {
                if (id > QueryDispatcher.this.minId) {
                    Toast.makeText(context, "Updating...", Toast.LENGTH_SHORT).show();
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