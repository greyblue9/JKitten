/* Program AB Reference AIML 2.1 implementation
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

import discord4j.core.DiscordClient;
import discord4j.core.GatewayDiscordClient;
import discord4j.core.event.domain.message.MessageCreateEvent;
import discord4j.core.object.entity.Member;
import discord4j.core.object.entity.Message;
import discord4j.core.object.entity.Role;
import discord4j.core.object.entity.channel.GuildChannel;
import discord4j.core.object.entity.channel.MessageChannel;
import org.alicebot.ab.*;

import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class Main {
  
  public static final Map<CharSequence, Chat> chatSessions = new LinkedHashMap<>();
  
  static {
  MagicStrings.setRootPath("./");
  MagicStrings.default_Customer_id = "856229099952144464";
  AIMLProcessor.extension = new PCAIMLProcessorExtension();
  }
  
  public static void trace(final Object... args) {
  if (!MagicBooleans.trace_mode) return;
  final StringBuilder sb = new StringBuilder(128);
  for (final Object arg: args) {
    if (sb.length() != 0) sb.append(" ");
    sb.append(
    (arg instanceof CharSequence)
      ? (CharSequence) arg
      : (arg == null)
        ? "<null>"
        : arg.toString()
    );
  }
  System.err.print(sb.toString());
  System.err.print((char) 0x0A);
  System.err.flush();
  }
  
  public static Chat getOrCreateChat(
    final Bot bot,
    final boolean doWrites,
    final CharSequence customerId
  )
  {
  if (! chatSessions.containsKey(customerId)) {
    final Chat chat = new Chat(
    bot, doWrites, customerId.toString(
    ));
    trace("created", chat, "for customerId", customerId);
    chatSessions.put(customerId, chat);
    return chat;
  }
  final Chat chat = chatSessions.get(customerId);
  trace("Returning", chat, "for customerId", customerId);
  return chat;
  }
  
  public static class DiscordBot {

  public static DiscordClient start(final Bot bot, final boolean doWrites) 
  {
    final String token = System.getenv("Token");
    if (token == null) return null;
    final DiscordClient cl = DiscordClient.create(token);
    final GatewayDiscordClient gw = cl.login().block();
    gw.on(MessageCreateEvent.class).subscribe(
    (final MessageCreateEvent event) ->
    {
      final Message msg = event.getMessage();
      final MessageChannel channel 
      = msg.getChannel().block();
      if (Objects.requireNonNull(channel).getId().asLong()
      != 944426266256367656L)
      {
      return;
      }
      if (msg.getAuthor().get().isBot()) {
      return;
      }
      final long authorId 
      = msg.getAuthor().get().getId().asLong();
      final String username = msg.getAuthor().get().getUsername();
      final Chat chat = getOrCreateChat(
      bot, doWrites, Long.toString(authorId, 10)
      );
      String currentName = chat.predicates.getOrDefault("name", "unknown");
      if (null == currentName 
        || "".equals(currentName) 
        || "unknown".equals(currentName.toLowerCase()) 
        || "friend".equals(currentName.toLowerCase()) 
        || "seeker".equals(currentName.toLowerCase())) 
      {
      trace("setting name to", username);
      chat.predicates.put("name", username);
      //trace("setting that to", username);
      //chat.predicates.put("that", username);
      }
      trace("msg", msg, "in chat", chat);
      String text = msg.getContent();
      Pattern p = Pattern.compile("<!?@([0-9]+)>", Pattern.DOTALL);
      Matcher mchr = p.matcher(text);
      while (mchr.find()) {
      long num = Long.parseLong(mchr.group(1));
      List<Member> members = gw.getGuildMembers(msg.getGuildId().get()).toStream().filter(mb -> mb.getId().asLong() == num).collect(Collectors.toList());
      if (! members.isEmpty()) {
        Member member = members.get(0);
        String memberName = member.getUsername();
        trace("Replacing member", mchr.group(0), "with", memberName);
        text = mchr.replaceAll(memberName);
        mchr.reset(text);
        continue;
      }
      List<Role> roles = gw.getGuildRoles(msg.getGuildId().get()).toStream().filter(r -> r.getId().asLong() == num).collect(Collectors.toList());
      if (! roles.isEmpty()) {
        Role role = roles.get(0);
        String roleName = role.getName();
        trace("Replacing role", mchr.group(0), "with", roleName);
        text = mchr.replaceAll(roleName);
        mchr.reset(text);
        continue;
      }
      List<GuildChannel> channels = gw.getGuildChannels(msg.getGuildId().get()).toStream().filter(c -> c.getId().asLong() == num).collect(Collectors.toList());
      if (! channels.isEmpty()) {
        GuildChannel ch = channels.get(0);
        String channelName = ch.getName();
        trace("Replacing channel", mchr.group(0), "with", channelName);
        text = mchr.replaceAll(channelName);
        mchr.reset(text);
      }
      }
      final String response = chat.multisentenceRespond(text);
      System.err.printf(
      "\n%s: %s\n", msg.getAuthor().get().getUsername(), text
      );
      System.err.printf(
      "  >> %s\n", response
      );
      if (response != null && !response.isEmpty()) {
      Objects.requireNonNull(msg.getChannel().block()).createMessage(response).block();
      }
    });
    return cl;
  }
  }

  public static void main(final String... args) {
  String botName = MagicStrings.default_bot_name;
  MagicBooleans.jp_tokenize = false;
  MagicBooleans.trace_mode = true;
  String action = "chat";
  for (final String s : args) {
    String[] splitArg = s.split("=");
    if (splitArg.length >= 2) {
    String option = splitArg[0];
    String value = splitArg[1];
    trace("option:", option, "value:", value);
    if (option.equals("bot")) botName = value;
    if (option.equals("action")) action = value;
    if (option.equals("trace")) {
      MagicBooleans.trace_mode = Boolean.parseBoolean(value);
    }
    if (option.equals("morph")) {
      MagicBooleans.jp_tokenize = Boolean.parseBoolean(value);
    }
    }
  }
  trace("Working Directory =", MagicStrings.root_path);
  Graphmaster.enableShortCuts = false;
  
  final Bot bot = new Bot(
    botName, MagicStrings.root_path, action
  );
  boolean doWrites = ! action.equals("chat-app");
  final Chat chat = getOrCreateChat(
    bot, doWrites, MagicStrings.default_Customer_id
  );
  
  EnglishNumberToWords.makeSetMap(bot);
  getGloss(bot, "glossary.xml");
  if (MagicBooleans.make_verbs_sets_maps) {
    Verbs.makeVerbSetsMaps(bot);
  }
  if (bot.brain.getCategories().size() 
   < MagicNumbers.brain_print_size) {
    bot.brain.printgraph();
  }
  trace("Action =", action);
  final DiscordClient cl;
  if (args.length == 0) {
     cl = DiscordBot.start(bot, true);
  }
  
  if (action.equals("chat") || action.equals("chat-app"))
  {
    chat.chat();
  } else if (action.equals("ab")) {
    TestAB.testAB(bot, TestAB.sample_file);
  } else if (action.equals("aiml2csv") 
      || action.equals("csv2aiml"))
  {
    convert(bot, action);
  } else if (action.equals("abwq")) {
    AB ab = new AB(bot, TestAB.sample_file);
    ab.abwq();
  } else if (action.equals("test")) {
    TestAB.runTests(bot, MagicBooleans.trace_mode);
  } else if (action.equals("shadow")) {
    MagicBooleans.trace_mode = false;
    bot.shadowChecker();
  } else if (action.equals("iqtest")) {
    ChatTest ct = new ChatTest(bot);
    try {
    ct.testMultisentenceRespond();
    } catch (Exception ex) {
    ex.printStackTrace();
    }
  } else {
    System.out.println("Unrecognized action " + action);
  }
  }

  public static void convert(Bot bot, String action) {
  if (action.equals("aiml2csv")) {
    bot.writeAIMLIFFiles(); 
  } else if (action.equals("csv2aiml")) {
    bot.writeAIMLFiles();
  }
  }

  public static Object getGloss(Bot bot, String filename) {
  System.out.println("getGloss");
  try {
    // Open the file that is the first
    // command line parameter
    final File file = new File(filename);
    if (file.exists()) {
    try (final FileInputStream fstream = new FileInputStream(file)) {
      // Get the object
      return getGlossFromInputStream(bot, fstream);
    }
    }
  } catch (final IOException e) {
    e.printStackTrace();
  }
  return null;
  }

  public static Map<Category, Nodemapper> getGlossFromInputStream(Bot bot, InputStream in) {
  System.out.println("getGlossFromInputStream");
  BufferedReader br = new BufferedReader(new InputStreamReader(in));
  String strLine;
  int cnt = 0;
  int filecnt = 0;
  HashMap<String, String> def = new HashMap<String, String>();
  final Map<Category, Nodemapper> categories = new HashMap<>();
  try {
      //Read File Line By Line
    String word;
    String gloss;
    word = null;
    gloss = null;
    while ((strLine = br.readLine()) != null) {
    if (strLine.contains("<entry word")) {
      int start = strLine.indexOf("<entry word=\"") + "<entry word=\"".length();
          //int end = strLine.indexOf(" status=");
      int end = strLine.indexOf("#");
      word = strLine.substring(start, end);
      word = word.replaceAll("_", " ");
      System.out.println(word);
    } else {
      gloss = strLine.replaceAll("", "");
      gloss = gloss.replaceAll("", "");
      gloss = gloss.trim();
      System.out.println(gloss);
    }
    if (word != null && gloss != null) {
      word = word.toLowerCase().trim();
      if (gloss.length() > 2) gloss = gloss.substring(0, 1).toUpperCase() + gloss.substring(1, gloss.length());
      String definition;
      if (def.keySet().contains(word)) {
      definition = def.get(word);
      definition = definition + "; " + gloss;
      } else definition = gloss;
      def.put(word, definition);
      word = null;
      gloss = null;
    }
    }
    Category d = new Category(0, "WNDEF *", "*", "*", "unknown", "wndefs" + filecnt + ".aiml");
    bot.brain.addCategory(d);
    for (String x : def.keySet()) {
    word = x;
    gloss = def.get(word) + ".";
    cnt++;
    if (cnt % 5000 == 0) filecnt++;
    Category c = new Category(0, "WNDEF " + word, "*", "*", gloss, "wndefs" + filecnt + ".aiml");
    System.out.println(cnt + " " + filecnt + " " + c.inputThatTopic() + ":" + c.getTemplate() + ":" + c.getFilename());
    final Nodemapper node;
    if ((node = bot.brain.findNode(c)) != null) node.category.setTemplate(node.category.getTemplate() + "," + gloss);
    bot.brain.addCategory(c);
    categories.put(c, node);
    }
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  return categories;
  }

  public static void sraixCache(String filename, Chat chatSession) {
  int limit = 1000;
  try {
    FileInputStream fstream = new FileInputStream(filename);
      // Get the object
    BufferedReader br = new BufferedReader(new InputStreamReader(fstream));
    String strLine;
      //Read File Line By Line
    int count = 0;
    while ((strLine = br.readLine()) != null && count++ < limit) {
    System.out.println("Human: " + strLine);
    String response = chatSession.multisentenceRespond(strLine);
    System.out.println("Robot: " + response);
    }
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  }
}