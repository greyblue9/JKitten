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
import java.util.*;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.Jsoup;
import org.jsoup.parser.Parser;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.StringEscapeUtils;
import static java.nio.charset.StandardCharsets.UTF_8;
import java.util.regex.*;
/**
structure representing an AIML category and operations on Category
*/
public class Category 
  implements Comparable<Category> {
  
  public static Map<String, Category> byPattern = new TreeMap<>();

  public String pattern;
  public Element patternEl;
  public String that;
  public Element thatEl;
  public String topic;
  public Element topicEl;
  public String template;
  public String templateRaw;
  public Element templateEl;
  public String filename;

  public int activationCnt;

  public int categoryNumber; // for loading order

  public static int categoryCnt = 0;

  public AIMLSet matches;
  
  @Override
  public int compareTo(final Category o) {
    if (o == null) {
      return 0;
    }
    int cmp = this.getPattern().compareTo(
      o.getPattern()
    );
    if (cmp != 0) return cmp;
    cmp = this.getFilename().compareTo(
      o.getFilename()
    );
    if (cmp != 0) return cmp;
    return 0;
  }
  /**
  Return a set of inputs matching the category
   *
  @return nd AIML Set of elements matching this category
  */
  public AIMLSet getMatches(Bot bot) {
  if (matches != null) return matches; else return new AIMLSet("No Matches", bot);
  }

  /**
  number of times a category was activated by inputs
   *
  @return nteger number of activations
  */
  public int getActivationCnt() {
  return activationCnt;
  }

  /**
  get the index number of this category
   *
  @return nique integer identifying this category
  */
  public int getCategoryNumber() {
  return categoryNumber;
  }

  /**
  get category pattern
   *
  @return attern
  */
  public String getPattern() {
  if (pattern == null) return "*"; else return pattern;
  }

  /**
  get category that pattern
   *
  @return hat pattern
  */
  public String getThat() {
  if (that == null) return "*"; else return that;
  }

  /**
  get category topic pattern
   *
  @return opic pattern
  */
  public String getTopic() {
  if (topic == null) return "*"; else return topic;
  }

  /**
  get category template
   *
  @return emplate
  */
  public String getTemplate() {
  if (template == null) return ""; else return template;
  }

  /**
  get name of AIML file for this category
   *
  @return ile name
  */
  public String getFilename() {
  if (filename == null) return MagicStrings.unknown_aiml_file; else return filename;
  }

  /**
  increment the category activation count
  */
  public void incrementActivationCnt() {
  activationCnt++;
  }

  /** set category activation count
   *
  @param cnt activation count
  */
  public void setActivationCnt(int cnt) {
  activationCnt = cnt;
  }

  /**
  set category filename
  @param filename ame of AIML file
  */
  public void setFilename(String filename) {
  this.filename = filename;
  }

  /**
  set category template
  @param template IML template
  */
  public void setTemplate(String template) {
  this.template = template;
  }

  /**
  set category pattern
   *
  @param pattern IML pattern
  */
  public void setPattern(String pattern) {
  this.pattern = pattern;
  }

  /**
  set category that pattern
   *
  @param that IML that pattern
  */
  public void setThat(String that) {
  this.that = that;
  }

  /**
  set category topic
   *
  @param topic AIML topic pattern
  */
  public void setTopic(String topic) {
  this.topic = topic;
  }

  /**
  return a string represeting the full pattern path as "`input pattern <THAT> that pattern <TOPIC> topic pattern'"
  @return
  */
  public String inputThatTopic() {
  return Graphmaster.inputThatTopic(pattern, that, topic);
  }

  /**
  add a matching input to the matching input set
   *
  @param input atching input
  */
  public void addMatch(String input, Bot bot) {
  if (matches == null) {
    String setName = this.inputThatTopic().replace("*", "STAR").replace("_", "UNDERSCORE").replace(" ", "-").replace("<THAT>", "THAT").replace("<TOPIC>", "TOPIC");
      // System.out.println("Created match set "+setName);
    matches = new AIMLSet(setName, bot);
  }
  matches.add(input);
  }
  
  static final Matcher NL_MATCHER
    = Pattern.compile("\r?\n", Pattern.DOTALL).matcher("");

  /**
  convert a template to a single-line representation by replacing "," with #Comma and newline with #Newline
  @param template riginal template
  @return emplate on a single line of text
  */
  public static String templateToLine(String template) {
    return NL_MATCHER.reset(template)
      .replaceAll("\\#Newline")
      .replace(
        MagicStrings.aimlif_split_char,
        MagicStrings.aimlif_split_char_name
      );
  }

  /**
  restore a template to its original form by replacing #Comma with "," and #Newline with newline.
  @param line emplate on a single line of text
  @return riginal multi-line template
  */
  public static String lineToTemplate(String line) {
  String result = line.replaceAll("\\#Newline", "\n");
  result = result.replaceAll(MagicStrings.aimlif_split_char_name, MagicStrings.aimlif_split_char);
  return result;
  }

  /**
  convert a category from AIMLIF format to a Category object
   *
  @param IF ategory in AIMLIF format
  @return ategory object
  */
  public static Category IFToCategory(String IF) {
  String[] split = IF.split(MagicStrings.aimlif_split_char);
    //System.out.println("Read: "+split);
  return new Category(Integer.parseInt(split[0]), split[1], split[2], split[3], lineToTemplate(split[4]), split[5]);
  }

  /**
  convert a Category object to AIMLIF format
  @param category ategory object
  @return ategory in AIML format
  */
  public static String categoryToIF(Category category) {
    //System.out.println("categoryToIF: template="+templateToLine(category.getTemplate()));
  String c = MagicStrings.aimlif_split_char;
  return category.getActivationCnt() + c + category.getPattern() + c + category.getThat() + c + category.getTopic() + c + templateToLine(category.getTemplate()) + c + category.getFilename();
  }

  /**
  convert a Category object to AIML syntax
   *
  @param category ategory object
  @return IML Category
  */
  public static String categoryToAIML(Category category) {
    String pattern = category.getPattern();
  
    if (pattern.contains("<SET>") || pattern.contains("<BOT")) {
      String[] splitPattern = pattern.split(" ");
      String rpattern = "";
      for (String w : splitPattern) {
      if (w.startsWith("<SET>") || w.startsWith("<BOT") || w.startsWith("NAME=")) {
        w = w.toLowerCase();
      }
      rpattern = rpattern + " " + w;
      }
      pattern = rpattern.trim();
    }
    
    if (pattern.contains("set")) {
      System.err.printf(
        "Rebuilt pattern: %s\n", 
        StringEscapeUtils.escapeJava(pattern)
      );
    }
    
    String NL = "\n";
    String result = "<category>\n  ";
    try {
      if (!category.getTopic().equals("*")) {
      result += "<topic>" 
        + category.getTopic()
        + "</topic>\n  ";
      }
      if (!category.getThat().equals("*")) {
        result += "<that>" 
          + category.getThat()
          + "</that>\n  ";
      }
      result += "<pattern>"
        + pattern
        + "</pattern>\n  ";
     
      result += "<template>"
        + category.getTemplate()
        + "</template>\n  "
       + "</category>";
    } catch (Exception ex) {
      ex.printStackTrace();
      return "";
    }
    return result;
  }
  
  /**
  check to see if a pattern expression is valid in AIML 2.0
   *
  @param pattern attern expression
  @return rue or false
  */
  public boolean validPatternForm(String pattern) {
    if (pattern.length() < 1) {
      validationMessage += "Zero length. ";
      return false;
    }
    return true;
  }

  public String validationMessage = "";

  /**
  check for valid Category format
   *
  @return rue or false
  */
  public boolean validate() {
    validationMessage = "";
    if (!validPatternForm(pattern)) {
      validationMessage += String.format(
        "Badly formatted pattern: %s\n", pattern
      );
    }
    else if (!validPatternForm(that)) {
      validationMessage += String.format(
        "Badly formatted that: %s\n", that
      );
    }
    else if (!validPatternForm(topic)) {
      validationMessage += String.format(
        "Badly formatted topic: %s\n", topic
      );
    }
    else if (!AIMLProcessor.validTemplate(template)) {
      validationMessage += String.format(
        "Badly formatted template: %s\n", template
      );
    }
    
    if (!filename.endsWith(".aiml")) {
      validationMessage += "Filename suffix should be .aiml\n";
    }
    if (validationMessage.isEmpty()) return true;
    System.err.printf(
      "Category(%s) failing validation: [%s]\n",
      this, validationMessage
    );
    return false;
  }
  
  static final Parser parser = Parser.xmlParser();
  
  public static Element toElement(final String input) {
    return parser.parseInput(input, "");
  }
  
  public static String normSpace(String input) {
    return 
        StringUtils.join(
          StringUtils.split(
            input
          ), " "
        ).trim();
  }

  /**
  Constructor
   *
  @param activationCnt ategory activation count
  @param pattern nput pattern
  @param that hat pattern
  @param topic opic pattern
  @param template IML template
  @param filename IML file name
  */
  public Category(int activationCnt, String pattern, String that, String topic, String template, String filename) {
    if (MagicBooleans.fix_excel_csv) {
      pattern = Utilities.fixCSV(pattern);
      that = Utilities.fixCSV(that);
      topic = Utilities.fixCSV(topic);
      template = Utilities.fixCSV(template);
      filename = Utilities.fixCSV(filename);
    }
    this.pattern = pattern.trim().toUpperCase();
    this.that = that.trim().toUpperCase();
    this.topic = topic.trim().toUpperCase();
    this.templateRaw = template;
    this.templateEl = toElement(template.replace("& ", " and "));
    this.template = templateEl.outerHtml().replaceAll("'\n *", "'"); // XML parser treats & badly
    this.filename = filename;
    this.activationCnt = activationCnt;
    matches = null;
    this.categoryNumber = categoryCnt++;
    byPattern.put(this.pattern, this);
  }

  /**
  Constructor
   *
  @param activationCnt ategory activation count
  @param patternThatTopic tring representing Pattern Path
  @param template IML template
  @param filename IML category
  */
  public Category(int activationCnt, String patternThatTopic, String template, String filename) {
  this(activationCnt, patternThatTopic.substring(0, patternThatTopic.indexOf("<THAT>")), patternThatTopic.substring(patternThatTopic.indexOf("<THAT>") + "<THAT>".length(), patternThatTopic.indexOf("<TOPIC>")), patternThatTopic.substring(patternThatTopic.indexOf("<TOPIC>") + "<TOPIC>".length(), patternThatTopic.length()), template, filename);
  }

  /**
  compare two categories for sorting purposes based on activation count
  */
  public static Comparator<Category> ACTIVATION_COMPARATOR = new Comparator<Category>() {

  public int compare(Category c1, Category c2) {
    return c2.getActivationCnt() - c1.getActivationCnt();
  }
  };

  /**
  compare two categories for sorting purposes based on alphabetical order of patterns
  */
  public static Comparator<Category> PATTERN_COMPARATOR = new Comparator<Category>() {

  public int compare(Category c1, Category c2) {
    return String.CASE_INSENSITIVE_ORDER.compare(c1.inputThatTopic(), c2.inputThatTopic());
  }
  };

  /**
  compare two categories for sorting purposes based on category index number
  */
  public static Comparator<Category> CATEGORY_NUMBER_COMPARATOR = new Comparator<Category>() {

  public int compare(Category c1, Category c2) {
    return c1.getCategoryNumber() - c2.getCategoryNumber();
  }
  };
  
  
  @Override
  public int hashCode() {
  int hash = 0x4839;
  hash = (hash << 3) ^ ((pattern != null) ? pattern.hashCode(): 0);
  hash = (hash << 3) ^ ((template != null) ? template.hashCode(): 0);
  hash = (hash << 3) ^ ((that != null) ? that.hashCode(): 0);
  return hash;
  }
  
  @Override
  public boolean equals(Object other) {
  if (!(other instanceof Category)) return false;
  Category o = (Category) other;
  return (
     (pattern != null && pattern.equals(o.pattern))
    || (pattern == null && o.pattern == null)
  ) && (
     (template != null && template.equals(o.template))
    || (template == null && o.template == null)
  ) && (
     (that != null && that.equals(o.that))
    || (that == null && o.that == null)
  );
  }
  
  @Override
  public String toString() {
    return String.format(
      "Category(pattern=%s, topic=%s, template=%s)",
      this.pattern != null
        ? StringEscapeUtils.escapeJava(this.pattern)
        : "null",
      this.that != null
        ? StringEscapeUtils.escapeJava(this.that)
        : "null",
      this.topic != null
        ? StringEscapeUtils.escapeJava(this.topic)
        : "null",
      this.template != null
        ? StringEscapeUtils.escapeJava(this.template)
        : "null"
    );
  }
}