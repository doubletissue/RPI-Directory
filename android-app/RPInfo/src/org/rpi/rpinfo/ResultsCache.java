package org.rpi.rpinfo;

import java.util.ArrayList;
import java.util.LinkedList;

import android.util.Log;

public class ResultsCache {	
	private static final String TAG = "ResultsCache";
	
	private class CacheEntry {
		public String key;
		public ArrayList<QueryResultModel> value;
		
		CacheEntry( String key, ArrayList<QueryResultModel> value ){
			this.key = key;
			this.value = value;
		}
	}
	
	// Represents the cache - the linked list is being used as a queue
	private LinkedList< CacheEntry > representation = new LinkedList< CacheEntry >();
	private static final int MAX_CACHE_SIZE = 5;
	
	public ResultsCache(){
	}
	
	/**
	 * Check if a search term matches an element of the cache
	 * 
	 * @param key The key in the cache.
	 * @param searchTerm The search term to match.
	 */
	public boolean matchSearchTerm(String key, String searchTerm ){
		try {
			String compareTerm = searchTerm.substring(0, key.length());
			if( key.equalsIgnoreCase(compareTerm) ){
				return true;
			}
		} catch(IndexOutOfBoundsException e) {
			return false;
		}
		
		return false;
	}

	private int fillSearchSpace( int top, int left, int topLeft, Character c1, Character c2 ){
		int topOrLeft = Math.min( top, left );
		int result = Math.min( topOrLeft, topLeft + (Character.toUpperCase(c1) == Character.toUpperCase(c2) ? 0 : 1) );
		return result;
	}
	
	/**
	 * Check if s contains the subsequence matching using dynamic programming.
	 * Do this by computing the distance, then seeing if it is equal to the
	 * difference in lengths.
	 * 
	 * @param s The first string
	 * @param matching The second string
	 * @return Whether or not the second string is a subsequence of the first string
	 */
	private boolean matchSubsequence( String s, String matching ){
		int[][] searchSpace = new int[s.length() + 1][matching.length() + 1];
		
		//Prepare the base cases
		for( int i = 0; i <= s.length(); ++i ){
			searchSpace[i][0] = i;
		}
		for( int i = 0; i <= matching.length(); ++i ){
			searchSpace[0][i] = i;
		}
		
		//String debugString = "";
		
		//Fill in the rest of the matrix
		for( int i = 1; i <= s.length(); ++i ){
			for( int j = 1; j <= matching.length(); ++j ){
				searchSpace[i][j] = fillSearchSpace( 
						1+searchSpace[i-1][j], 
						1+searchSpace[i][j-1], 
						searchSpace[i-1][j-1],
						s.charAt(i-1), 
						matching.charAt(j-1) );
				//debugString += searchSpace[i][j];
			}
			//debugString += "\n";
		}

		//Log.i(TAG, debugString);
		
		int distance = searchSpace[s.length()][matching.length()];
		
		//Log.i(TAG, "Distance: " + distance + " ML: " + matching.length() + " NL: " + s.length() );
		
		if( distance == Math.abs( matching.length() - s.length() ) ){
			return true;
		} else {
			return false;
		}
	}

	private ArrayList<QueryResultModel> pruneResults(String searchTerm,
			ArrayList<QueryResultModel> models){
		ArrayList<QueryResultModel> rv = new ArrayList<QueryResultModel>();
		
		for( QueryResultModel element : models ){
			if( matchSubsequence( element.getElement("name", null), searchTerm ) ){
				rv.add(element);
			}
		}
		
		return rv;
	}

	public ArrayList<QueryResultModel> extract(String searchTerm){
		/*
		Log.i( TAG, "Input: " + searchTerm );
		
		for( CacheEntry element : representation ){
			Log.i( TAG, "Key: " + element.key );
		}
		*/
		
		ArrayList<QueryResultModel> rv;
		for( CacheEntry entry : representation ){
			if( matchSearchTerm(entry.key, searchTerm) ){
				//Log.i( TAG, "Matched: " + searchTerm );
				rv = pruneResults( searchTerm, entry.value );
				//Log.i( TAG, "Insert: " + searchTerm );
				insert( searchTerm, rv );
				return rv;
			}
		}
		
		return null;
	}
	
	public void insert(String searchTerm, ArrayList<QueryResultModel> searchResults ) {
		//Log.i( TAG, "Insert Happening: " + searchTerm );
		
		CacheEntry entry = new CacheEntry( searchTerm, searchResults );
		representation.addFirst( entry );
		if( representation.size() > MAX_CACHE_SIZE ){
			representation.removeLast();
		}
	}
}
