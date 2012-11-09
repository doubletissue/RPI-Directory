package org.rpi.rpinfo.detail;

import java.util.ArrayList;

import org.rpi.rpinfo.R;
import org.rpi.rpinfo.api.PersonModel;

import android.content.Context;
import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;

public class DetailFragment extends Fragment {

    private static final String TAG = "DetailFragment";
    private TextView nameTextView;
    private ListView detailListView;
    private PersonModel selectedPerson;

    public DetailFragment() {
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_detail, container, false);
        nameTextView = (TextView) rootView.findViewById(R.id.person_name);
        detailListView = (ListView) rootView.findViewById(R.id.detail_list);

        Bundle b = getActivity().getIntent().getExtras();
        if (b == null) {
            getActivity().finish();
        }

        // Extract the selected person from the intent
        selectedPerson = (PersonModel) b.getSerializable("selectedPerson");
        if (selectedPerson == null) {
            getActivity().finish();
        }

        ArrayList<PersonDetail> models = PersonDetail.generateModels(selectedPerson
                .getAllElements());

        // Put the person's name in
        nameTextView.setText(selectedPerson.getElement("name", "N/A"));

        addPersonImage(detailListView, selectedPerson);

        // Set up the list view
        detailListView.setAdapter(new DetailListAdapter(getActivity(),
                R.layout.view_detail_list_item, models));

        // If a list element is pressed
        detailListView.setOnItemClickListener(new OnItemClickListener() {
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                PersonDetail model = (PersonDetail) parent.getAdapter().getItem(position);
                String key = model.getRawKey();
                if (key.equals("phone")) {
                    // Log.i(TAG, "Calling" + model.getValue());
                    Intent intent = new Intent(android.content.Intent.ACTION_VIEW, Uri.parse("tel:"
                            + model.getValue()));
                    startActivity(intent);
                } else if (key.equals("email")) {
                    // Log.i(TAG, "Sending email to " + model.getValue());
                    Intent intent = new Intent(android.content.Intent.ACTION_SEND);
                    intent.setType("message/rfc822");
                    intent.putExtra(android.content.Intent.EXTRA_EMAIL,
                            new String[] { model.getValue() });
                    startActivity(Intent.createChooser(intent, "Send email..."));
                }
            }
        });

        return rootView;
    }

    private void addPersonImage(final ListView listView, final PersonModel personModel) {
        // Set up the bottom at the end of the list (must be done before setAdapter)
        LayoutInflater layoutInflater = (LayoutInflater) getActivity().getSystemService(
                Context.LAYOUT_INFLATER_SERVICE);
        LinearLayout linearLayout = (LinearLayout) layoutInflater.inflate(
                R.layout.view_detail_list_image, null, false);
        final ImageView imageView = (ImageView) linearLayout.findViewById(R.id.detail_person_photo);
        final ProgressBar imageProgress = (ProgressBar) linearLayout
                .findViewById(R.id.detail_person_photo_progress);

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

        listView.addHeaderView(linearLayout, null, false);
    }
}
