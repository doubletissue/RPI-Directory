package org.rpi.rpinfo.util;

public class StringManip {

    /**
     * Convert a string to Title Case
     * 
     * @param s
     *            String to convert to Title Case
     * @return The string in Title Case
     */
    public static String toTitleCase(String s) {
        StringBuilder stringBuilder = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); ++i) {
            if (i == 0 || s.charAt(i - 1) == ' ' || s.charAt(i - 1) == '-') {
                stringBuilder.append(Character.toTitleCase(s.charAt(i)));
            } else {
                stringBuilder.append(s.charAt(i));
            }
        }
        return stringBuilder.toString();
    }
}
