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
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Library General Public License for more details.
 You should have received a copy of the GNU Library General Public
 License along with this library; if not, write to the
 Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
 Boston, MA  02110-1301, USA.
 */
import org.alicebot.ab.utils.CalendarUtils;
import org.alicebot.ab.utils.NetworkUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedWriter;
import java.io.*;
import java.util.HashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.HttpMessage;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.commons.httpclient.util.URIUtil;
import org.apache.commons.io.IOUtils;
// import org.apache.http.conn.BasicManagedEntity;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.client.methods.RequestBuilder;

public class Sraix {

  public static HashMap<String, String> custIdMap = new HashMap<String, String>();

  public static String custid = "1"; // customer ID number for Pandorabots

  public static String sraix(Chat chatSession, String input, String defaultResponse, String hint, String host, String botid, String apiKey, String limit) {
  String response;
  if (!MagicBooleans.enable_network_connection) response = MagicStrings.sraix_failed; else if (host != null && botid != null) {
    response = sraixPandorabots(input, chatSession, host, botid);
  } else response = sraixPannous(input, hint, chatSession);
  System.out.println("Sraix: response = " + response + " defaultResponse = " + defaultResponse);
  if (response == null || (response.trim().isEmpty() || response.equals(MagicStrings.sraix_failed))) {
    if (defaultResponse != null && !defaultResponse.toLowerCase().equals("unknown") && !defaultResponse.toLowerCase().equals("nothing") && !defaultResponse.toLowerCase().equals("null") && !defaultResponse.toLowerCase().trim().equals("")) {
    response = defaultResponse;
    } else {
    response = AIMLProcessor.respond(input, "", "", chatSession);
    }
  }
  return response;
  }

  public static String sraixPandorabots(String input, Chat chatSession, String host, String botid) {
    //System.out.println("Entering SRAIX with input="+input+" host ="+host+" botid="+botid);
  String responseContent = pandorabotsRequest(input, host, botid);
  if (responseContent == null) return MagicStrings.sraix_failed; else return pandorabotsResponse(responseContent, chatSession, host, botid);
  }

  public static String pandorabotsRequest(String input, String host, String botid) {
  try {
    custid = "0";
    String key = host + ":" + botid;
    if (custIdMap.containsKey(key)) custid = custIdMap.get(key);
      //System.out.println("--> custid = "+custid);
      //System.out.println("Pandorabots Request "+input);
    String spec = NetworkUtils.spec(host, botid, custid, input);
      //String fragment = "?botid="+botid+"&custid="+custid+"input="+input;
      //URI uri = new URI("http", host, "/pandora/talk-xml", fragment);
      /*   String scheme = "http";
       String authority = host;
       String path = "/pandora/talk-xml";
       String query = "botid="+botid+"&custid="+custid+"&input="+input;
       String fragment = null;
       URI uri=null;  String out;
       try {
       uri = new URI(scheme, authority, path, query, fragment);
       out = "\n";
       out += "URI example:\n";
       out += "    URI string: "+uri.toString()+"\n";
       System.out.print(out);
       } catch (Exception e) {
       e.printStackTrace();
       }*/
      //uri = new URI(spec);
      //String subInput = input;
      //while (subInput.contains(" ")) subInput = subInput.replace(" ", "+");
      //spec = "http://"+host+"/pandora/talk-xml?botid="+botid+"&custid="+custid+"input="+subInput;
    if (MagicBooleans.trace_mode) System.out.println("Spec = " + spec);
      // System.out.println("URI="+uri);
      // http://isengard.pandorabots.com:8008/pandora/talk-xml?botid=835f69388e345ab2&custid=dd3155d18e344a7c&input=%E3%81%93%E3%82%93%E3%81%AB%E3%81%A1%E3%81%AF
    String responseContent = NetworkUtils.responseContent(spec);
      //System.out.println("Sraix: Response="+responseContent);
    return responseContent;
  } catch (Exception ex) {
    ex.printStackTrace();
    return null;
  }
  }

  public static String pandorabotsResponse(String sraixResponse, Chat chatSession, String host, String botid) {
  String botResponse = MagicStrings.sraix_failed;
  try {
    int n1 = sraixResponse.indexOf("<that>");
    int n2 = sraixResponse.indexOf("</that>");
    if (n2 > n1) botResponse = sraixResponse.substring(n1 + "<that>".length(), n2);
    n1 = sraixResponse.indexOf("custid=");
    if (n1 > 0) {
    custid = sraixResponse.substring(n1 + "custid=\"".length(), sraixResponse.length());
    n2 = custid.indexOf("\"");
    if (n2 > 0) custid = custid.substring(0, n2); else custid = "0";
    String key = host + ":" + botid;
        //System.out.println("--> Map "+key+" --> "+custid);
    custIdMap.put(key, custid);
    }
    if (botResponse.endsWith(".")) botResponse = botResponse.substring(0, botResponse.length() - 1); // snnoying Pandorabots extra "."
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  return botResponse;
  }

  public static String sraixPannous(String input, String hint, Chat chatSession) {
  String rawInput = input;
  if (hint == null) hint = MagicStrings.sraix_no_hint;
  input = " " + input + " ";
  input = input.replace(" point ", ".");
  input = input.replace(" rparen ", ")");
  input = input.replace(" lparen ", "(");
  input = input.replace(" slash ", "/");
  input = input.replace(" star ", "*");
  input = input.replace(" dash ", "-");
    // input = chatSession.bot.preProcessor.denormalize(input);
  input = input.trim();
  input = input.replace(" ", "+");
  int offset = CalendarUtils.timeZoneOffset();
    //System.out.println("OFFSET = "+offset);
  String locationString = "";
  if (chatSession.locationKnown) {
    locationString = "&location=" + chatSession.latitude + "," + chatSession.longitude;
  }
  Matcher mchr = Pattern.compile("^([A-Z][A-Z]+) ").matcher(input);
  if (mchr.find()) {
    String newInput = mchr.replaceAll("");
    System.err.printf("Removed \"%s\" prefix from input: \"%s\" -> \"%s\"\n", mchr.group(1), input, newInput);
    input = newInput;
  }
  Matcher w_mchr = Pattern.compile("^(who|what|where|why|how)( (?:have|has|had|be|am|is|are|was|were|been|being))* ", Pattern.CASE_INSENSITIVE | Pattern.DOTALL).matcher(input);
  if (w_mchr.find()) {
    String questionWord = w_mchr.group(1);
    String helpingVerbs = w_mchr.group(2).trim();
    System.err.printf("Found questionWord=%s, helpingVerbs=%s\n", questionWord, helpingVerbs);
    String newInput = mchr.replaceAll("");
    System.err.printf("Removed questionWord=%s and helpingVerbs=%s from input: \"%s\" -> \"%s\"\n", questionWord, helpingVerbs, input, newInput);
    input = newInput;
  }
  try {
    final DefaultHttpClient client = new DefaultHttpClient();
    final HttpUriRequest req = RequestBuilder.get(String.format("https://www.google.com" + "/search" + "?client=safari&rls=en&gbv=1" + "&q=%1$s" + "&hl=en&num=10", URIUtil.encodeWithinQuery(input))).addHeader("Accept-Language", "en-us").addHeader("Host", "www.google.com").addHeader("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8").addHeader("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15").build();
    MagicBooleans.trace(String.format("in Sraix.sraixPannous, req.getURI(): '%s'", req.getURI()));
    final HttpResponse resp = client.execute(req);
    final HttpMessage respAsMessage = (HttpMessage) resp;
    MagicBooleans.trace(String.format("in Sraix.sraixPannous, resp: %s", resp));
    final String page;
    final HttpEntity entity = resp.getEntity();
    final String encoding = entity.getContentType().getElements()[0].getParameters()[0].getValue();
    try (final InputStream is = entity.getContent()){
    page = IOUtils.toString(is, encoding);
    }
    ;
    final Document doc = Jsoup.parse(page);
    final Elements elems = doc.select("div");
    final Elements h3s = doc.select("h3");
    int bestLev = 999999999;
    String bestTopic = "", bestDesc = "";
    for (final Element h3 : h3s) {
    final Element itemdiv = (Element) h3.parent().parent().parent();
    final Elements descdivs = itemdiv.select("div:first-child:last-child " + "> div:first-child:last-child " + "> div:first-child:last-child " + "> div:first-child " + "> div:first-child:last-child");
    if (descdivs.isEmpty()) continue;
    final Element descdiv = descdivs.get(0);
    String desc = descdiv.text();
    String topic = h3.text().split(" - ")[0].split("\\|")[0];
    String topicMatch = String.format("what is %s?", input), descMatch = String.format("%s is ", input);
    int levTopic = StringUtils.getLevenshteinDistance(topic.toLowerCase(), topicMatch.toLowerCase());
    int levDesc = StringUtils.getLevenshteinDistance(desc.toLowerCase().subSequence(0, descMatch.length()), descMatch.toLowerCase());
    System.err.printf("levTopic=%d, levDesc=%d, topic=\"%s\", desc=\"%s\"\n", levTopic, levDesc, topic, desc);
    if (levTopic + levDesc < bestLev) {
      bestLev = levTopic + levDesc;
      bestTopic = topic;
      bestDesc = desc;
      System.err.printf("Best is now %d + %d: %d\n", levTopic, levDesc, levTopic + levDesc);
    }
    }
    System.err.printf("bestDesc: \"%s\" (topic: \"%s\")", bestDesc, bestTopic);
    String retDesc = bestDesc;
    Matcher m = Pattern.compile("^(.{30,}[a-z])\\. +(.*)$").matcher(bestDesc);
    if (m.find()) retDesc = m.replaceAll("$1");
    System.err.printf("Returning first sentence: \"%s\"\n", retDesc);
    return retDesc;
  } catch (Throwable e) {
    e.printStackTrace();
  }
  return MagicStrings.sraix_failed;
  } // sraixPannous

  public static void log(String pattern, String template) {
  System.out.println("Logging " + pattern);
  template = template.trim();
  if (MagicBooleans.cache_sraix) try {
    if (!template.contains("<year>") && !template.contains("No facilities")) {
    template = template.replace("\n", "\\#Newline");
    template = template.replace(",", MagicStrings.aimlif_split_char_name);
    template = template.replaceAll("<a(.*)</a>", "");
    template = template.trim();
    if (template.length() > 0) {
      FileWriter fstream = new FileWriter("c:/ab/bots/sraixcache/aimlif/sraixcache.aiml.csv", true);
      BufferedWriter fbw = new BufferedWriter(fstream);
      fbw.write("0," + pattern + ",*,*," + template + ",sraixcache.aiml");
      fbw.newLine();
      fbw.close();
    }
    }
  } catch (Exception e) {
    System.out.println("Error: " + e.getMessage());
  }
  }
}
