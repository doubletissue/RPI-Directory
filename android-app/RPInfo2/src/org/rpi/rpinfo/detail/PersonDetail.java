package org.rpi.rpinfo.detail;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import org.rpi.rpinfo.util.StringManip;

import android.text.Html;
import android.text.Spanned;

public class PersonDetail {
    private static Set<String> printableKeys = new HashSet<String>() {
        {
            this.add("phone");
            this.add("campus_mailstop");
            this.add("office_location");
            this.add("department");
            // this.add("mailing_address");
            this.add("type");
            this.add("homepage");
            this.add("title");
            this.add("rcsid");
            this.add("email");
        }
    };

    private String key;
    private String value;

    /**
     * Format the field to display correctly
     * 
     * @param field
     *            The field key
     * @return The formatted field name
     */
    private static String formatField(String field) {
        String rv = "";

        // If empty string, can't do much
        if (field.length() == 0) {
            return field;
        }

        rv = field.replaceAll("_", " ");
        rv = rv.toUpperCase();

        return rv;
    }

    /**
     * Format the value to display correctly
     * 
     * @param field
     *            The field (so we know how to format the value)
     * @param value
     *            The value to format
     * @return The formatted value
     */
    private static String formatValue(String field, String value) {
        // Change this in the future to make it fancier
        if (field.equals("campus_mailstop") || field.equals("office_location")
                || field.equals("department") || field.equals("mailing_address")
                || field.equals("type") || field.equals("title")) {
            value = StringManip.toTitleCase(value);
        }
        return value;
    }

    public static ArrayList<PersonDetail> generateModels(Map<String, String> raw_data) {
        ArrayList<PersonDetail> parsed_data = new ArrayList<PersonDetail>();

        for (Entry<String, String> entry : raw_data.entrySet()) {
            // Already output name on the top
            if (printableKeys.contains(entry.getKey())) {
                parsed_data.add(new PersonDetail(entry.getKey(), entry.getValue()));
            }
        }

        return parsed_data;
    }

    PersonDetail(String key, String value) {
        this.key = key;
        this.value = value;
    }

    public String getRawKey() {
        return key;
    }

    public Spanned getKey() {
        Spanned parsed_key = Html.fromHtml("<b>" + formatField(key) + "</b>");
        return parsed_key;
    }

    public String getValue() {
        return formatValue(key, value);
    }

    /*
     * public String toString() { //Spanned is like a string but it can contain formatting data and
     * such Spanned parsed_data = Html.fromHtml("<b>" + formatField( key ) + "</b>: " + formatValue(
     * key, value ) ); return parsed_data.toString(); }
     */
}
