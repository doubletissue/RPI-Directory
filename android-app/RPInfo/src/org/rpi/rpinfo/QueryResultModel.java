package org.rpi.rpinfo;

import java.io.Serializable;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * A frontend for a JSONObject with data on a particular person
 */
public class QueryResultModel implements Serializable {
	//A unique identifier for this class (for serialization)
	private static final long serialVersionUID = -579697907972516780L;
	private JSONObject data = null;
	
	public QueryResultModel( JSONObject data ){
		this.data = data;
	}
	
	/**
	 * Get an element of the JSONObject that the QueryResultModel holds.
	 * 
	 * @param key The key to find
	 * @param failure the object to return if the key is not found
	 * @return The value that the key maps to or the failure object
	 */
	public Object getElement(String key, Object failure){
		try {
			return this.data.get(key);
		} catch (JSONException e) {
			return failure;
		}
	}
	
}
