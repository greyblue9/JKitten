package org.alicebot.ab;
/* Program AB Reference AIML 2.0 implementation
 Copyright (C) 2013 ALICE A.I. Foundation
 Contact: info@alicebot.org
 This library is free software; you can redistribute it and/or
 modify it under the terms of the GNU Library General Public
 License as published by the Free Software Foundation; either
 version 2 of the License, or (at your option) any later version.
 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 Library General Public License for more details.
 You should have received a copy of the GNU Library General Public
 License along with this library; if not, write to the
 Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
 Boston, MA 02110-1301, USA.
 */
import java.io.*;
import java.util.HashMap;
import org.apache.commons.lang3.StringEscapeUtils;

/**
Manage client predicates
 *
 */
public class Predicates extends HashMap<String, String> {

  /**
  save a predicate value
   *
  @param key redicate name
  @param value redicate value
  @return redicate value
  */
  @Override
  public String put(String key, String value) {
    MagicBooleans.trace(String.format(
      "predicates.put(key: %s, value: %s)",
      StringEscapeUtils.escapeJava(key),
      StringEscapeUtils.escapeJava(value)
    ));
    if (key.equals("topic")
      && (value == null || value.isEmpty()))
    {
      value = this.get(key);
    }
    if (value.equals(MagicStrings.too_much_recursion)) {
      value = MagicStrings.default_list_item;
    }
    // MagicBooleans.trace("Setting predicate key: " + key + " to value: " + value);
    String result = super.put(key, value);
    // MagicBooleans.trace("in predicates.put, returning: " + result);
    return result;
  }

  /**
  get a predicate value
   *
  @param key predicate name
  @return redicate value
  */
  @Override
  public String get(final Object key) {
    MagicBooleans.trace(String.format(
      "predicates.get(key: %s)",
      StringEscapeUtils.escapeJava((String) key)
    ));
    String result = super.get(key);
    if (result == null) result = MagicStrings.default_get;
    MagicBooleans.trace(String.format(
      "predicates.get(key: %s) returning -> %s",
      StringEscapeUtils.escapeJava((String) key),
      StringEscapeUtils.escapeJava(result)
    ));
    return result;
  }

  /**
  Read predicate default values from an input stream
   *
  @param in input stream
  */
  public void getPredicateDefaultsFromInputStream(
    final InputStream in) 
  {
    try (final BufferedReader br = new BufferedReader(
           new InputStreamReader(in))
        )
    {
      // Read File Line By Line
      String strLine;
      while ((strLine = br.readLine()) != null) {
        if (strLine.contains(":")) {
          String property = strLine.substring(0, strLine.indexOf(":"));
          String value = strLine.substring(strLine.indexOf(":") + 1);
          this.put(property, value);
        }
      }
    } catch (Exception ex) {
      ex.printStackTrace();
    }
  }

  /** read predicate defaults from a file
   *
  @param filename ame of file
  */
  public void getPredicateDefaults(String filename) {
    try {
        // Open the file that is the first
        // command line parameter
        final File file = new File(filename);
        if (file.exists()) {
        try (final InputStream fstream
          = new FileInputStream(filename))
        {
          // Get the object
          getPredicateDefaultsFromInputStream(fstream);
        }
      }
    } catch (Exception e) {
      // Catch exception if any
      e.printStackTrace();
    }
  }
}
