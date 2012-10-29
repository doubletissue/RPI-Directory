package org.rpi.rpinfo.api;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * A frontend for a JSONObject with data on a particular person
 */
public class PersonModel implements Serializable {
    // A unique identifier for this class (for serialization)
    private static final long serialVersionUID = -579697907972516780L;
    private String data = null;

    /**
     * Constructor
     * 
     * @param data
     *            A JSONObject containing the relevant data
     */
    public PersonModel(JSONObject data) {
        // The question remains: why does JSONObject not implement Serializable?
        this.data = data.toString();
    }

    /**
     * Parse a JSONObject into a HashMap<String, String>
     * 
     * @param data
     *            A JSONObject that maps Strings to Strings
     * @return A map that is identical to the JSONObject
     */
    private HashMap<String, String> getMap(JSONObject data) {
        HashMap<String, String> results = new HashMap<String, String>();

        /*
         * For some reason this returns an iterator rather than a string iterator, even though the
         * javadoc says that it is over string. Go figure.
         */
        @SuppressWarnings("unchecked")
        Iterator<String> keys = data.keys();

        while (keys.hasNext()) {
            String currentKey = keys.next();
            try {
                results.put(currentKey, data.getString(currentKey));
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        return results;
    }

    /**
     * Get an element of the JSONObject that the QueryResultModel holds.
     * 
     * @param key
     *            The key to find
     * @param failure
     *            the object to return if the key is not found
     * @return The value that the key maps to or the failure object
     */
    public String getElement(String key, String failure) {
        JSONObject JSONData = null;

        // Convert the string into a JSONObject object.
        try {
            JSONData = new JSONObject(this.data);
        } catch (JSONException e1) {
            e1.printStackTrace();
        }

        /*
         * Get the requested data from the JSONObject. If it does not exist, return the failure
         * value
         */
        try {
            return (String) JSONData.get(key);
        } catch (JSONException e) {
            return failure;
        }
    }

    /**
     * @return A Map<String, String> representing the original JSON object that was passed in.
     */
    public Map<String, String> getAllElements() {
        JSONObject JSONData = null;

        // Convert the string into a JSONObject object.
        try {
            JSONData = new JSONObject(this.data);
        } catch (JSONException e1) {
            e1.printStackTrace();
        }

        HashMap<String, String> results = getMap(JSONData);

        return results;
    }

}
