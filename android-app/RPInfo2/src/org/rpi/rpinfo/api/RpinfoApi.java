package org.rpi.rpinfo.api;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map.Entry;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HttpContext;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.content.Context;
import android.os.AsyncTask;
import android.widget.Toast;

//import android.util.Log;

public class RpinfoApi {
    private static RpinfoApi singleton = null;
    public static final int FIRST_PAGE = 1;
    public static final int DEFAULT_NUM_RESULTS = 20;
    private static final String TAG = "RpinfoApi";
    private static final String URLBASE = "http://www.rpidirectory.appspot.com/api";
    // private static final String URLBASE = "http://homepages.rpi.edu/~horowm/api";
    private static final String PARAM_SEARCH_TEXT = "q";
    private static final String PARAM_PAGE = "page_num";
    private static final String PARAM_NUM_RESULTS = "page_size";
    private static final String PARAM_SOURCE = "source";
    private static final String PARAM_SOURCE_THIS = "androidApp";
    private static final ResultsCache cache = new ResultsCache();
    private Object requestLock = new Object();
    private Context context;

    private RpinfoApi(Context context) {
        this.context = context;
    }

    /**
     * Add the GET parameters to the URL, also perform any sanitization
     * 
     * @param params
     *            The GET parameters
     * @return The encoded URL
     */
    private String decorateUrl(HashMap<String, String> params) {
        String url = URLBASE;

        boolean first = true;
        for (Entry<String, String> entry : params.entrySet()) {
            // URLEncoder sanitize the input
            url += (first ? "?" : "&") + URLEncoder.encode(entry.getKey()) + "="
                    + URLEncoder.encode(entry.getValue());
            first = false;
        }

        return url;
    }

    public static RpinfoApi getInstance(Context c) {
        if (singleton == null) {
            singleton = new RpinfoApi(c);
        }

        return singleton;
    }

    /**
     * Parse the result of an API transaction to a list of QueryResultModel
     * 
     * @param apiResult
     *            The result of the API transaction
     * @return The ArrayList<QueryResultModel> that corresponds to the data
     */
    private ArrayList<PersonModel> parseApiResult(JSONObject apiResult) throws JSONException {
        ArrayList<PersonModel> list_items = new ArrayList<PersonModel>();

        JSONArray data_array = apiResult.getJSONArray("data");

        // No need to display more than MAX_DISPLAY_ELEMENTS (25) elements
        for (int i = 0; i < data_array.length(); ++i) {
            JSONObject current;

            // Get the current object in the array and add it to the list
            current = data_array.getJSONObject(i);
            list_items.add(new PersonModel(current));
        }

        return list_items;
    }

    /**
     * @param searchTerm
     *            The term to search for
     * @param page
     *            The page to return
     * @param numResults
     *            The number of results per page
     * @return The results of the query
     */
    private ArrayList<PersonModel> doRequest(String searchTerm, int page, int numResults) {
        /**
         * Do only one request at a time - reduce server load, but also allow requests to take
         * advantage of cached results by previous requests.
         */
        // Log.i( TAG, "Search: " + searchTerm );

        synchronized (requestLock) {
            try {
                ArrayList<PersonModel> rv = null;
                if (page == FIRST_PAGE) {
                    rv = cache.extract(searchTerm);
                }

                if (rv == null) {
                    HttpClient httpClient = new DefaultHttpClient();
                    HttpContext localContext = new BasicHttpContext();

                    // Prepare the URL parameters
                    HashMap<String, String> params = new HashMap<String, String>();
                    params.put(PARAM_SEARCH_TEXT, searchTerm);
                    params.put(PARAM_PAGE, Integer.toString(page));
                    params.put(PARAM_NUM_RESULTS, Integer.toString(numResults));
                    params.put(PARAM_SOURCE, PARAM_SOURCE_THIS);

                    String url = decorateUrl(params);
                    HttpGet httpGet = new HttpGet(url);

                    HttpResponse response = httpClient.execute(httpGet, localContext);
                    BufferedReader in = new BufferedReader(new InputStreamReader(response
                            .getEntity().getContent()));

                    try {
                        String json = in.readLine();
                        rv = parseApiResult(new JSONObject(json));
                    } catch (Exception e) {
                        new AsyncTask<Void, Void, Void>() {
                            @Override
                            protected void onPreExecute() {
                                Toast.makeText(
                                        RpinfoApi.this.context,
                                        "Error: Something bad happened!\nThe search service may be down :(",
                                        Toast.LENGTH_LONG).show();
                            }

                            @Override
                            protected Void doInBackground(Void... params) {
                                return null;
                            }
                        }.execute();
                        rv = new ArrayList<PersonModel>();
                    }

                    // Don't cache results for other pages... yet
                    if (page == FIRST_PAGE) {
                        cache.insert(searchTerm, rv);
                    }
                }

                return rv;
            } catch (ClientProtocolException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        return null;
    }

    /**
     * Wrapper for doRequest
     * 
     * @param searchTerm
     *            The term to search for
     * @param page
     *            The page to return
     * @param numResults
     *            The number of results per page
     * @return The results of the query
     */
    public ArrayList<PersonModel> request(String searchTerm, int page, int numResults) {
        return doRequest(searchTerm, page, numResults);
    }
}