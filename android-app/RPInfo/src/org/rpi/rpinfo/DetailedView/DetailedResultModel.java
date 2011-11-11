package org.rpi.rpinfo.DetailedView;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;

import android.text.Html;
import android.text.Spanned;

public class DetailedResultModel {
	private String key;
	private String value;
	
	/**
	 * Format the field to display correctly
	 * 
	 * @param field The field key
	 * @return The formatted field name
	 */
	private static String formatField( String field ){
		String rv = "";
		
		//If empty string, can't do much
		if( field.length() == 0 ){
			return field;
		}
		
		rv = field.replaceAll("_", " ");		
		rv = rv.toUpperCase();
		
		return rv;
	}

	/**
	 * Format the value to display correctly
	 * 
	 * @param field The field (so we know how to format the value)
	 * @param value The value to format
	 * @return The formatted value
	 */
	private static String formatValue( String field, String value ){
		return value;
	}
	
	DetailedResultModel(String key, String value){
		this.key = key;
		this.value = value;
	}
	
	public static ArrayList<DetailedResultModel> generateModels( Map<String, String>  raw_data ){		
		ArrayList<DetailedResultModel> parsed_data = new ArrayList<DetailedResultModel>();

		for( Entry<String, String> entry : raw_data.entrySet() ){
			//Already output name on the top
			if( !entry.getKey().equals("name") ){
				parsed_data.add(new DetailedResultModel(entry.getKey(), entry.getValue()));
			}
		}
		
		return parsed_data;
	}
	
	public String getRawKey() {
		return key;
	}
	
	public Spanned getKey() {
		Spanned parsed_key = Html.fromHtml("<b>" + formatField( key ) + "</b>:");
		return parsed_key;
	}
	
	public String getValue() {
		return value;
	}
	
	/*
	public String toString() {
		//Spanned is like a string but it can contain formatting data and such
		Spanned parsed_data = Html.fromHtml("<b>" + formatField( key ) + "</b>: " + formatValue( key, value ) );
		return parsed_data.toString();
	}
	*/
}
