package org.rpi.rpinfo.detail;

import java.util.List;

import org.rpi.rpinfo.R;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

public class DetailListAdapter extends ArrayAdapter<PersonDetail> {
    public DetailListAdapter(Context context, int textViewResourceId,
            List<PersonDetail> objects) {
        super(context, textViewResourceId, objects);
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
            newView = inflater.inflate(R.layout.view_detail_list_item, null);
        }

        PersonDetail model = this.getItem(position);

        // Fill the view with all of the data
        if (model != null) {
            TextView key = (TextView) newView.findViewById(R.id.key);
            TextView value = (TextView) newView.findViewById(R.id.value);

            key.setText(model.getKey());
            value.setText(model.getValue());
        }

        return newView;
    }
}
