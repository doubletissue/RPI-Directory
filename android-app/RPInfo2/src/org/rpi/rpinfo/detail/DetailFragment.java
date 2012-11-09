package org.rpi.rpinfo.detail;

import java.util.ArrayList;

import org.rpi.rpinfo.R;
import org.rpi.rpinfo.api.PersonModel;

import android.content.ContentProviderOperation;
import android.content.Context;
import android.content.Intent;
import android.content.OperationApplicationException;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.RemoteException;
import android.provider.ContactsContract;
import android.provider.ContactsContract.RawContacts;
import android.support.v4.app.Fragment;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.MenuItem.OnMenuItemClickListener;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

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

        setHasOptionsMenu(true);

        return rootView;
    }

    @Override
    public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
        inflater.inflate(R.menu.activity_detail, menu);

        final String email = selectedPerson.getElement("email", null);
        final String phone = selectedPerson.getElement("phone", null);

        MenuItem sendEmail = menu.findItem(R.id.menu_send_email);
        MenuItem dialPhone = menu.findItem(R.id.menu_dial_phone);
        MenuItem addContact = menu.findItem(R.id.menu_add_contact);

        if (email == null) {
            sendEmail.setVisible(false);
        } else {
            sendEmail.setOnMenuItemClickListener(new OnMenuItemClickListener() {

                @Override
                public boolean onMenuItemClick(MenuItem item) {
                    Intent intent = new Intent(android.content.Intent.ACTION_SEND);
                    intent.setType("message/rfc822");
                    intent.putExtra(android.content.Intent.EXTRA_EMAIL, new String[] { email });
                    startActivity(Intent.createChooser(intent, "Send email..."));
                    return false;
                }
            });
        }

        if (phone == null) {
            dialPhone.setVisible(false);
        } else {
            dialPhone.setOnMenuItemClickListener(new OnMenuItemClickListener() {

                @Override
                public boolean onMenuItemClick(MenuItem item) {
                    Intent intent = new Intent(android.content.Intent.ACTION_VIEW, Uri.parse("tel:"
                            + phone));
                    startActivity(intent);
                    return false;
                }
            });
        }

        addContact.setOnMenuItemClickListener(new OnMenuItemClickListener() {

            @Override
            public boolean onMenuItemClick(MenuItem item) {
                addToContacts();
                return false;
            }
        });
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {

        return true;
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

    /**
     * Add the selected person to ones contacts
     */
    private boolean addToContacts() {
        ArrayList<ContentProviderOperation> ops = new ArrayList<ContentProviderOperation>();

        // Backreference value. Don't need to do anything to it.
        int contact_index = 0;

        // Use the RCS ID as a unique account identifier
        String accountName = selectedPerson.getElement("rcsid", null);
        if (accountName != null) {
            ops.add(ContentProviderOperation.newInsert(RawContacts.CONTENT_URI)
                    .withValue(RawContacts.ACCOUNT_TYPE, null)
                    .withValue(RawContacts.ACCOUNT_NAME, null).build());
        } else {
            // Log.i(TAG, "Person does not have an RCS id. Cannot add to contacts.");
            return false;
        }

        String personName = selectedPerson.getElement("name", null);
        if (personName != null) {
            ops.add(ContentProviderOperation
                    .newInsert(ContactsContract.Data.CONTENT_URI)
                    .withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
                    .withValue(ContactsContract.Data.MIMETYPE,
                            ContactsContract.CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE)
                    .withValue(ContactsContract.CommonDataKinds.StructuredName.DISPLAY_NAME,
                            personName).build());
        } else {
            // Log.i(TAG, "Person does not have a name.");
        }

        String personEmail = selectedPerson.getElement("email", null);
        if (personEmail != null) {
            ops.add(ContentProviderOperation
                    .newInsert(ContactsContract.Data.CONTENT_URI)
                    .withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
                    .withValue(ContactsContract.Data.MIMETYPE,
                            ContactsContract.CommonDataKinds.Email.CONTENT_ITEM_TYPE)
                    .withValue(ContactsContract.CommonDataKinds.Email.TYPE,
                            ContactsContract.CommonDataKinds.Email.TYPE_WORK)
                    .withValue(ContactsContract.CommonDataKinds.Email.DATA1, personEmail).build());
        } else {
            // Log.i(TAG, "Person does not have a e-mail address.");
        }

        String personPhoneNumber = selectedPerson.getElement("phone", null);
        if (personEmail != null) {
            ops.add(ContentProviderOperation
                    .newInsert(ContactsContract.Data.CONTENT_URI)
                    .withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
                    .withValue(ContactsContract.Data.MIMETYPE,
                            ContactsContract.CommonDataKinds.Phone.CONTENT_ITEM_TYPE)
                    .withValue(ContactsContract.CommonDataKinds.Phone.TYPE,
                            ContactsContract.CommonDataKinds.Phone.TYPE_WORK)
                    .withValue(ContactsContract.CommonDataKinds.Phone.NUMBER, personPhoneNumber)
                    .build());
        } else {
            // Log.i(TAG, "Person does not have a phone number.");
        }

        String personWebsite = selectedPerson.getElement("homepage", null);
        if (personWebsite != null) {
            ops.add(ContentProviderOperation
                    .newInsert(ContactsContract.Data.CONTENT_URI)
                    .withValueBackReference(ContactsContract.Data.RAW_CONTACT_ID, contact_index)
                    .withValue(ContactsContract.Data.MIMETYPE,
                            ContactsContract.CommonDataKinds.Website.CONTENT_ITEM_TYPE)
                    .withValue(ContactsContract.CommonDataKinds.Website.TYPE,
                            ContactsContract.CommonDataKinds.Website.TYPE_HOMEPAGE)
                    .withValue(ContactsContract.CommonDataKinds.Website.URL, personWebsite).build());
        } else {
            // Log.i(TAG, "Person does not have a website.");
        }

        try {
            getActivity().getContentResolver().applyBatch(ContactsContract.AUTHORITY, ops);
        } catch (RemoteException e) {
            e.printStackTrace();
        } catch (OperationApplicationException e) {
            e.printStackTrace();
        }

        Toast.makeText(getActivity(), "Added to contacts.", Toast.LENGTH_SHORT).show();

        return true;
    }

}
