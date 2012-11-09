package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.List;

import org.rpi.rpinfo.api.PersonModel;
import org.rpi.rpinfo.api.RpinfoApi;
import org.rpi.rpinfo.util.StringManip;

import android.content.Context;
import android.graphics.drawable.Drawable;
import android.os.AsyncTask;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

public class SearchResultListAdapter extends ArrayAdapter<PersonModel> {
    private static final String TAG = "QueryResultArrayAdapter";
    private int page = RpinfoApi.FIRST_PAGE;
    private List<PersonModel> representation;
    private String searchTerm;

    public SearchResultListAdapter(Context context, int textViewResourceId,
            List<PersonModel> objects, String searchTerm) {
        super(context, textViewResourceId, objects);
        this.representation = objects;
        this.searchTerm = searchTerm;
    }

    public String getSearchTerm() {
        return searchTerm;
    }

    /**
     * Increment the page and return the new page
     * 
     * @return The next page
     */
    public int nextPage() {
        page += 1;
        return page;
    }

    /**
     * Add some more results to the list
     * 
     * @param newResults
     *            An ArrayList of QueryResultModels
     */
    public void addData(ArrayList<PersonModel> newResults) {
        /*
         * This is hacky and terrible, and it should work the proper way but it doesn't! The proper
         * way would be to use the add function that is inherited from the parent class, rather than
         * change the underlying data structure.
         */
        this.representation.addAll(newResults);
        this.notifyDataSetChanged();
        this.notifyDataSetInvalidated();
    }

    public View getView(int position, View oldView, ViewGroup parent) {
        View newView = oldView;

        /*
         * OldView is the previously displayed view - if possible, re-use it for efficiency. If it
         * doesn't exist, make a new one.
         */
        if (newView == null) {
            LayoutInflater inflater = (LayoutInflater) getContext().getSystemService(
                    Context.LAYOUT_INFLATER_SERVICE);
            newView = inflater.inflate(R.layout.view_search_list_item, null);
        }

        // Get the current from the array
        // QueryResultModel model = this.models.get(position);
        PersonModel model = this.getItem(position);

        // Fill the view with all of the data
        if (model != null) {
            TextView name = (TextView) newView.findViewById(R.id.query_result_name);
            // TextView email = (TextView) newView.findViewById(R.id.query_result_email);
            TextView year = (TextView) newView.findViewById(R.id.query_result_year);
            TextView major = (TextView) newView.findViewById(R.id.query_result_department);
            LinearLayout photoContainer = (LinearLayout) newView
                    .findViewById(R.id.query_person_photo_container);

            if (name != null) {
                String nameData = (String) model.getElement("name", "N/A");
                name.setText(nameData);
            }
            /*
             * if (email != null) { String emailData = (String) model.getElement("email", "N/A");
             * email.setText(emailData); }
             */
            if (year != null) {
                String yearData = (String) model.getElement("year", null);
                // If the person doesn't have a year, is probably faculty or staff and therefore has
                // a title
                if (yearData == null) {
                    yearData = (String) model.getElement("title", "N/A");
                }
                year.setText(StringManip.toTitleCase(yearData));
            }
            if (major != null) {
                String majorData = (String) model.getElement("major", null);
                // If the person doesn't have a major, is probably faculty or staff and therefore
                // has a department
                if (majorData == null) {
                    majorData = (String) model.getElement("department", "N/A");
                }
                major.setText(StringManip.toTitleCase(majorData));
            }
            if (photoContainer != null) {
                loadImage(model, photoContainer);
            }
        }

        return newView;
    }

    /**
     * Load an image associated with a RCSID into an asynctask. Do it in the background.
     * 
     * @param rcsId
     *            The RCSID to load the image from.
     * @param imageView
     *            The view in which to load the image.
     */
    private void loadImage(final PersonModel personModel, final LinearLayout photoContainer) {
        final ImageView imageView = (ImageView) photoContainer
                .findViewById(R.id.query_person_photo);
        final ProgressBar imageProgress = (ProgressBar) photoContainer
                .findViewById(R.id.query_person_photo_progress);

        new AsyncTask<Void, Void, Drawable>() {

            protected void onPreExecute() {
                imageView.setVisibility(View.GONE);
                imageProgress.setVisibility(View.VISIBLE);
            };

            @Override
            protected Drawable doInBackground(Void... params) {
                return personModel.getImage();
            }

            protected void onPostExecute(Drawable result) {
                if (result == null) {
                    imageView.setImageResource(R.drawable.unknown_person);
                } else {
                    imageView.setImageDrawable(result);
                }
                imageView.setVisibility(View.VISIBLE);
                imageProgress.setVisibility(View.GONE);
            };
        }.execute();
    }
}
