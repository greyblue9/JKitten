package org.alicebot.ab;
/**
 rogram AB Reference AIML 2.0 implementation
 opyright (C) 2013 ALICE A.I. Foundation
 ontact: info@alicebot.org
 his library is free software; you can redistribute it and/or
 odify it under the terms of the GNU Library General Public
 icense as published by the Free Software Foundation; either
 ersion 2 of the License, or (at your option) any later version.
 his library is distributed in the hope that it will be useful,
 ut WITHOUT ANY WARRANTY; without even the implied warranty of
 ERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 ibrary General Public License for more details.
 ou should have received a copy of the GNU Library General Public
 icense along with this library; if not, write to the
 ree Software Foundation, Inc., 51 Franklin St, Fifth Floor,
 oston, MA 02110-1301, USA.
 */
import java.io.*;
import java.util.HashMap;

/**
 mplements AIML Map
 map is a function from one string set to another.
 lements of the domain are called keys and elements of the range are called values.
 */
public class AIMLMap extends HashMap<String, String> {

  public String mapName;

  String host; // for external maps

  String botid; // for external maps

  boolean isExternal = false;

  Inflector inflector = new Inflector();

  Bot bot;

  /**
   onstructor to create a new AIML Map
   param name he name of the map
   */
  public AIMLMap(String name, Bot bot) {
  super();
  this.bot = bot;
  this.mapName = name;
  }

  /**
   eturn a map value given a key
   param key he domain element
   return he range element or a string indicating the key was not found
   */
  public String get(String key) {
  String value;
  if (mapName.equals(MagicStrings.map_successor)) {
    try {
    int number = Integer.parseInt(key);
    return String.valueOf(number + 1);
    } catch (Exception ex) {
    return MagicStrings.default_map;
    }
  } else if (mapName.equals(MagicStrings.map_predecessor)) {
    try {
    int number = Integer.parseInt(key);
    return String.valueOf(number - 1);
    } catch (Exception ex) {
    return MagicStrings.default_map;
    }
  } else if (mapName.equals("singular")) {
    return inflector.singularize(key).toLowerCase();
  } else if (mapName.equals("plural")) {
    return inflector.pluralize(key).toLowerCase();
  } else if (isExternal && MagicBooleans.enable_external_sets) {
      // String[] split = key.split(" ");
    String query = mapName.toUpperCase() + " " + key;
    String response = Sraix.sraix(null, query, MagicStrings.default_map, null, host, botid, null, "0");
    System.out.println("External " + mapName + "(" + key + ")=" + response);
    value = response;
  } else value = super.get(key);
  if (value == null) value = MagicStrings.default_map;
    // System.out.println("AIMLMap get "+key+"="+value);
  return value;
  }

  /**
   ut a new key, value pair into the map.
   param key he domain element
   param value he range element
   return he value
   */
  public String put(String key, String value) {
    // System.out.println("AIMLMap put "+key+"="+value);
  return super.put(key, value);
  }

  public void writeAIMLMap() {
  System.out.println("Writing AIML Map " + mapName);
  try {
      // Create file
    FileWriter fstream = new FileWriter(bot.maps_path + "/" + mapName + ".txt");
    BufferedWriter out = new BufferedWriter(fstream);
    for (String p : this.keySet()) {
    p = p.trim();
        // System.out.println(p+"-->"+this.get(p));
    out.write(p + ":" + this.get(p).trim());
    out.newLine();
    }
      // Close the output stream
    out.close();
  } catch (Exception e) {
      // Catch exception if any
    System.err.println("Error: " + e.getMessage());
  }
  }

  public int readAIMLMapFromInputStream(InputStream in, Bot bot) {
  int cnt = 0;
  BufferedReader br = new BufferedReader(new InputStreamReader(in));
  String strLine;
    // Read File Line By Line
  try {
    while ((strLine = br.readLine()) != null && strLine.length() > 0) {
    String[] splitLine = strLine.split(":");
        // System.out.println("AIMLMap line="+strLine);
    if (splitLine.length >= 2) {
      cnt++;
      if (strLine.startsWith(MagicStrings.remote_map_key)) {
      if (splitLine.length >= 3) {
        host = splitLine[1];
        botid = splitLine[2];
        isExternal = true;
        System.out.println("Created external map at " + host + " " + botid);
      }
      } else {
      String key = splitLine[0].toUpperCase();
      String value = splitLine[1];
            // assume domain element is already normalized for speedier load
            // key = bot.preProcessor.normalize(key).trim();
      put(key, value);
      }
    }
    }
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  return cnt;
  }

  /**
   ead an AIML map for a bot
   param bot he bot associated with this map.
   */
  public int readAIMLMap(Bot bot) {
  int cnt = 0;
  if (MagicBooleans.trace_mode) System.out.println("Reading AIML Map " + bot.maps_path + "/" + mapName + ".txt");
  try {
      // Open the file that is the first
      // command line parameter
    File file = new File(bot.maps_path + "/" + mapName + ".txt");
    if (file.exists()) {
    FileInputStream fstream = new FileInputStream(bot.maps_path + "/" + mapName + ".txt");
        // Get the object
    cnt = readAIMLMapFromInputStream(fstream, bot);
    fstream.close();
    } else System.out.println(bot.maps_path + "/" + mapName + ".txt not found");
  } catch (Exception e) {
      // Catch exception if any
    System.err.println("Error: " + e.getMessage());
  }
  return cnt;
  }
}
