package org.alicebot.ab;
/* Program AB Reference AIML 2.0 implementation
 Copyright (C) 2013 ALICE A.I. Foundation
 Contact: info@alicebot.org
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
 Boston,MA 02110-1301, USA.
 */

import org.alicebot.ab.utils.IOUtils;
import com.google.common.collect.Ordering;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.SuffixFileFilter;
import org.apache.commons.io.IOCase;
import org.apache.commons.io.filefilter.TrueFileFilter;
import java.io.*;
import java.util.*;

/**
Class representing the AIML bot
*/
public class Bot {
  
  public static String getenv(String key, String defaultV) {
    String val = System.getenv(key);
    if (val == null || val.trim().isEmpty()) {
      return defaultV;
    }
    return val;
  }
  
  public final Properties properties = new Properties();

  public final PreProcessor preProcessor;

  public final Graphmaster brain;
  
  public Graphmaster learnfGraph;

  public Graphmaster learnGraph;
  public Graphmaster deletedGraph;
    
  // public Graphmaster unfinishedGraph;
  // public final ArrayList<Category> categories;
  public String name = "alice";

  public HashMap<String, AIMLSet> setMap = new HashMap<String, AIMLSet>();

  public HashMap<String, AIMLMap> mapMap = new HashMap<String, AIMLMap>();

  public HashSet<String> pronounSet = new HashSet<String>();

  public String root_path = ".";

  public String bot_path = root_path + "/bots";

  public String bot_name_path = bot_path + "/alice";

  public String aimlif_path = bot_name_path + "/aimlif";

  public String aiml_path = bot_name_path + "/aiml";

  public String config_path = bot_name_path + "/config";

  public String log_path = bot_name_path + "/log";

  public String sets_path = bot_name_path + "/sets";

  public String maps_path = bot_name_path + "/maps";

  /**
  Set all directory path variables for this bot
   *
  @param root oot directory of Program AB
  @param name ame of bot
  */
  public void setAllPaths(String root, String name) {
    try {
      File root_dir = new File(
        getenv(
          "ROOT_PATH",
          root
        )
      );
      if (!root_dir.exists()) {
        this.root_path = new File(".").getPath();
      } else {
        this.root_path = root_dir.getPath();
      }
      this.root_path = new File(this.root_path)
        .getAbsoluteFile().getCanonicalFile().getPath();
      
      File bot_dir = new File(
        getenv(
          "BOT_PATH",
          new File(
            new File(this.root_path),
            getenv("BOT_DIRNAME", "bots")
          ).getPath()
        )
      );
      if (! bot_dir.exists()) {
        this.bot_path = this.root_path;
      } else {
        this.bot_path = bot_dir.getPath();
      }
      
      File bot_name_dir = new File(
        getenv(
          "BOT_NAME_PATH",
          new File(
             new File(this.bot_path),
            getenv("BOT_NAME_DIRNAME", name)
          ).getPath()
        )
      );
      if (! bot_name_dir.exists()) {
        this.bot_name_path = this.root_path;
      } else {
        this.bot_name_path = bot_name_dir.getPath();
      }
      
      File rootDir =new File(root)
        .getAbsoluteFile().getCanonicalFile();
      
      File aiml_dir = new File(
        getenv(
          "AIML_PATH",
          new File(
            new File(this.bot_name_path), "aiml"
          ).getPath()
        )
      );
      if (! aiml_dir.exists()) {
        this.aiml_path = this.root_path;
      } else {
        this.aiml_path = aiml_dir.getPath();
      }
      
      
      if (MagicBooleans.trace_mode) {
        System.err.println(
          "Name = " + name + ", Path = " + bot_name_path
        );
      }
      
      File aimlif_dir = new File(
        getenv(
          "AIMLIF_PATH",
          new File(
            new File(this.bot_name_path), "aimlif"
          ).getPath()
        )
      );
      if (! aimlif_dir.exists()) {
        this.aimlif_path = this.root_path;
      } else {
        this.aimlif_path = aimlif_dir.getPath();
      }
      
      File config_dir = new File(
        getenv(
          "CONFIG_PATH",
          new File(
            new File(this.bot_name_path), "config"
          ).getPath()
        )
      );
      if (! config_dir.exists()) {
        this.config_path = this.root_path;
      } else {
        this.config_path = config_dir.getPath();
      }
      
      File log_dir = new File(
        getenv(
          "LOG_PATH",
          new File(
            new File(this.bot_name_path), "logs"
          ).getPath()
        )
      );
      if (! log_dir.exists()) {
        this.log_path = this.root_path;
      } else {
        this.log_path = log_dir.getPath();
      }
      
      File sets_dir = new File(
        getenv(
          "SETS_PATH",
          new File(
            new File(this.bot_name_path), "sets"
          ).getPath()
        )
      );
      if (! sets_dir.exists()) {
        this.sets_path = this.root_path;
      } else {
        this.sets_path = sets_dir.getPath();
      }
      
      File maps_dir = new File(
        getenv(
          "MAPS_PATH",
          new File(
            new File(this.bot_name_path), "maps"
          ).getPath()
        )
      );
      if (! maps_dir.exists()) {
        this.maps_path = this.root_path;
      } else {
        this.maps_path = maps_dir.getPath();
      }
      
      
      if (MagicBooleans.trace_mode) {
        System.out.println(root_path);
        System.out.println(bot_path);
        System.out.println(bot_name_path);
        System.out.println(aiml_path);
        System.out.println(aimlif_path);
        System.out.println(config_path);
        System.out.println(log_path);
        System.out.println(sets_path);
        System.out.println(maps_path);
      }
    } catch (IOException ioe) {
      throw new RuntimeException(ioe);
    }
  }

  /**
  Constructor (default action, default path, default bot name)
  */
  public Bot() {
  this(MagicStrings.default_bot);
  }

  /**
  Constructor (default action, default path)
  */
  public Bot(String name) {
  this(name, MagicStrings.root_path);
  }

  /**
  Constructor (default action)
   *
   */
  public Bot(String name, String path) {
  this(name, path, "auto");
  }

  /**
  Constructor
   *
  @param name ame of bot
  @param path oot path of Program AB
  @param action rogram AB action
  */
  public Bot(String name, String path, String action) {
  int cnt = 0;
  int elementCnt = 0;
  this.name = name;
  setAllPaths(path, name);
  this.brain = new Graphmaster(this);
  this.learnfGraph = new Graphmaster(this, "learnf");
  this.learnGraph = new Graphmaster(this, "learn");
    // this.unfinishedGraph = new Graphmaster(this);
    // this.categories = new ArrayList<Category>();
  preProcessor = new PreProcessor(this);
  addProperties();
  cnt = addAIMLSets();
  if (MagicBooleans.trace_mode) System.out.println("Loaded " + cnt + " set elements.");
  cnt += addAIMLMaps();
  if (MagicBooleans.trace_mode) System.out.println("Loaded " + cnt + " map elements");
  this.pronounSet = getPronouns();
  AIMLSet number = new AIMLSet(MagicStrings.natural_number_set_name, this);
  setMap.put(MagicStrings.natural_number_set_name, number);
  AIMLMap successor = new AIMLMap(MagicStrings.map_successor, this);
  mapMap.put(MagicStrings.map_successor, successor);
  AIMLMap predecessor = new AIMLMap(MagicStrings.map_predecessor, this);
  mapMap.put(MagicStrings.map_predecessor, predecessor);
  AIMLMap singular = new AIMLMap(MagicStrings.map_singular, this);
  mapMap.put(MagicStrings.map_singular, singular);
  AIMLMap plural = new AIMLMap(MagicStrings.map_plural, this);
  mapMap.put(MagicStrings.map_plural, plural);
    //System.out.println("setMap = "+setMap);
  Date aimlDate = new Date(new File(aiml_path).lastModified());
  Date aimlIFDate = new Date(new File(aimlif_path).lastModified());
  if (MagicBooleans.trace_mode) System.out.println("AIML modified " + aimlDate + " AIMLIF modified " + aimlIFDate);
  MagicStrings.pannous_api_key = Utilities.getPannousAPIKey(this);
  MagicStrings.pannous_login = Utilities.getPannousLogin(this);

  
  if (action.equals("aiml2csv")) {
    cnt += addCategoriesFromAIMLIF();
    cnt += addCategoriesFromAIML();
    writeAIMLIFFiles();
  } else if (action.equals("csv2aiml")) {
    cnt += addCategoriesFromAIML();
    cnt += addCategoriesFromAIMLIF();
    writeAIMLFiles();
  } else {
    if (aimlDate.after(aimlIFDate)) {
    cnt += addCategoriesFromAIMLIF();
    cnt += addCategoriesFromAIML();
    //writeAIMLFiles();
    //writeAIMLIFFiles();
    } else {
    cnt += addCategoriesFromAIML();
    cnt += addCategoriesFromAIMLIF();
    //writeAIMLIFFiles();
    //writeAIMLFiles();
    }
  }
  
  Category b = new Category(0, "PROGRAM VERSION", "*", "*", MagicStrings.program_name_version, "update.aiml");
  brain.addCategory(b);
  brain.nodeStats();
  learnfGraph.nodeStats();
  }

  HashSet<String> getPronouns() {
  HashSet<String> pronounSet = new HashSet<String>();
  String pronouns = Utilities.getFile(config_path + "/pronouns.txt");
  String[] splitPronouns = pronouns.split("\n");
  for (int i = 0; i < splitPronouns.length; i++) {
    String p = splitPronouns[i].trim();
    if (p.length() > 0) pronounSet.add(p);
  }
  if (MagicBooleans.trace_mode) System.out.println("Read pronouns: " + pronounSet);
  return pronounSet;
  }

  /**
  add an array list of categories with a specific file name
   *
  @param file ame of AIML file
  @param moreCategories ist of categories
  */
  public List<Category> addMoreCategories(String file, List<Category> moreCategories) {
  if (moreCategories == null) {
    moreCategories = new ArrayList<>();
  }
  if (file.contains(MagicStrings.deleted_aiml_file)) {
    if (this.deletedGraph != null) {
      for (Category c : moreCategories) {
        System.out.println("Delete "+c.getPattern());
        deletedGraph.addCategory(c);
      }
    }
  } else if (file.contains(MagicStrings.learnf_aiml_file)) {
    if (MagicBooleans.trace_mode) System.out.println("Reading Learnf file");
    for (Category c : moreCategories) {
       try {
         brain.addCategory(c);
         learnfGraph.addCategory(c);
      } catch (Throwable e) { e.printStackTrace(); };
    }
  } else {
    for (Category c : moreCategories) {
        //System.out.println("Brain size="+brain.root.size());
        //brain.printgraph();
    try {
    
      brain.addCategory(c);
    } catch (Throwable e) { e.printStackTrace(); };
    }
  }
  return moreCategories;
  }
  
  /**
  Load all brain categories from AIML directory
  */
  int addCategoriesFromAIML() {
  Timer timer = new Timer();
  timer.start();
  int cnt = 0;
  try {
      // Directory path here
    File folder = new File(aiml_path)
      .getAbsoluteFile().getCanonicalFile();
    
    final List<File> files 
      = Ordering.usingToString().sortedCopy(
        FileUtils.listFiles(
          new File(aiml_path),
          new SuffixFileFilter(".aiml", IOCase.INSENSITIVE),
          TrueFileFilter.TRUE
        )
      );
    final File[] listOfFiles = files.toArray(new File[0]);
    
    System.err.printf(
      "\n\n=== Loading %d AIML files from %s ===\n\n",
      files.size(),
      aiml_path
    );
    int i = -1;
    for (final File listOfFile: files) {
      if (! listOfFile.isFile()) continue;
      final String file = listOfFile.getName();
      if (file.endsWith(".aiml") || file.endsWith(".AIML")) {
        ++i;
        System.err.printf(
          "Loading %3d/%-3d: %-30s ... ",
          i+1, files.size(), file
        );
        List<Category> moreCategories = new ArrayList<>();
        int mcSize1 = 0, mcSize2 = 0;
        
        try {
          moreCategories = AIMLProcessor.AIMLToCategories(
            aiml_path, file
          );
          assert moreCategories != null;
          mcSize1 = moreCategories.size();
        } catch (Exception iex) {
          iex.printStackTrace();
        } finally {
          cnt += mcSize1;
        }
        System.err.printf("[OK +%4d -> %6d] ", mcSize1, cnt);
        
        try {
          moreCategories = addMoreCategories(
            file, moreCategories
          );
          assert moreCategories != null;
          mcSize2 = moreCategories.size() - mcSize1;
        } catch (Exception iex) {
          iex.printStackTrace();
        } finally {
          cnt += mcSize2;
        }
        if (mcSize2 > 0) {
          System.err.printf("[+%4d -> %6d]\n", mcSize2, cnt);
        } else {
          System.err.println();
        }
        
        if (false && mcSize1 == 0 && mcSize2 == 0) {
          System.err.printf(
            "Deleting %s ...\n", listOfFile
          );
          listOfFile.delete();
        }
      }
    }
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  if (MagicBooleans.trace_mode) System.out.println("Loaded " + cnt + " categories in " + timer.elapsedTimeSecs() + " sec");
  return cnt;
  }

  /**
  load all brain categories from AIMLIF directory
  */
  public int addCategoriesFromAIMLIF() {
  Timer timer = new Timer();
  timer.start();
  int cnt = 0;
  try {
      // Directory path here
    String file;
    File folder = new File(aimlif_path);
    if (folder.exists()) {
    File[] listOfFiles = IOUtils.listFiles(folder);
    if (MagicBooleans.trace_mode) System.out.println("Loading AIML files from " + aimlif_path);
    for (File listOfFile : listOfFiles) {
      if (listOfFile.isFile()) {
      file = listOfFile.getName();
      if (file.endsWith(MagicStrings.aimlif_file_suffix) || file.endsWith(MagicStrings.aimlif_file_suffix.toUpperCase())) {
        if (MagicBooleans.trace_mode) {
          System.err.printf("Loading %s\n", listOfFile);
        }
        try {
        List<Category> moreCategories = readIFCategories(aimlif_path + "/" + file);
        assert moreCategories != null;
        moreCategories = addMoreCategories(file, moreCategories);
        assert moreCategories != null;
        cnt += moreCategories.size();
        } catch (Exception iex) {
        System.out.println("Problem loading " + file);
        iex.printStackTrace();
        }
      }
      }
    }
    } else System.out.println("addCategoriesFromAIMLIF: " + aimlif_path + " does not exist.");
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  if (MagicBooleans.trace_mode) System.out.println("Loaded " + cnt + " categories in " + timer.elapsedTimeSecs() + " sec");
  return cnt;
  }

  /**
  write all AIML and AIMLIF categories
  */
  public void writeQuit() {
  writeAIMLIFFiles();
    //System.out.println("Wrote AIMLIF Files");
  writeAIMLFiles();
  }

  /**
  read categories from specified AIMLIF file into specified graph
   *
  @param graph raphmaster to store categories
  @param fileName ile name of AIMLIF file
  */
  public int readCertainIFCategories(Graphmaster graph, String fileName) {
  int cnt = 0;
  File file = new File(aimlif_path + "/" + fileName + MagicStrings.aimlif_file_suffix);
  if (file.exists()) {
    try {
    ArrayList<Category> certainCategories = readIFCategories(aimlif_path + "/" + fileName + MagicStrings.aimlif_file_suffix);
    for (Category d : certainCategories) graph.addCategory(d);
    cnt = certainCategories.size();
    System.out.println("readCertainIFCategories " + cnt + " categories from " + fileName + MagicStrings.aimlif_file_suffix);
    } catch (Exception iex) {
    System.out.println("Problem loading " + fileName);
    iex.printStackTrace();
    }
  } else System.out.println("No " + aimlif_path + "/" + fileName + MagicStrings.aimlif_file_suffix + " file found");
  return cnt;
  }

  /**
  write certain specified categories as AIMLIF files
   *
  @param graph he Graphmaster containing the categories to write
  @param file he destination AIMLIF file
  */
  public void writeCertainIFCategories(Graphmaster graph, String file) {
  
if (MagicBooleans.trace_mode) System.out.println("writeCertainIFCaegories " + file + " size= " + graph.getCategories().size());
  writeIFCategories(graph.getCategories(), file + MagicStrings.aimlif_file_suffix);
  File dir = new File(aimlif_path);
  dir.setLastModified(new Date().getTime());
  }

  /**
  write deleted categories to AIMLIF file
  */
  /**
  write learned categories to AIMLIF file
  */
  public void writeLearnfIFCategories() {
  writeCertainIFCategories(learnfGraph, MagicStrings.learnf_aiml_file);
  }

  /**
  write unfinished categories to AIMLIF file
  */
  /* public void writeUnfinishedIFCategories() {
   writeCertainIFCategories(unfinishedGraph, MagicStrings.unfinished_aiml_file);
   }*/
  /**
  write categories to AIMLIF file
   *
  @param cats rray list of categories
  @param filename IMLIF filename
  */
  public void writeIFCategories(ArrayList<Category> cats, String filename) {
  return;
  /*//System.out.println("writeIFCategories "+filename);
  BufferedWriter bw = null;
  File existsPath = new File(aimlif_path);
  if (!existsPath.exists()) existsPath.mkdirs();
  if (existsPath.exists()) try {
      //Construct the bw object
    bw = new BufferedWriter(new FileWriter(aimlif_path + "/" + filename));
    for (Category category : cats) {
    try {
      bw.write(Category.categoryToIF(category));
      bw.newLine();
    } catch (Throwable e) {
      e.printStackTrace() ;
    }
    }  
    } catch (FileNotFoundException ex) {
    ex.printStackTrace();
  } catch (IOException ex) {
    ex.printStackTrace();
  } finally {
      //Close the bw
    try {
    if (bw != null) {
      bw.flush();
      bw.close();
    }
    } catch (IOException ex) {
    ex.printStackTrace();
    }
  }*/
  }

  /**
  Write all AIMLIF files from bot brain
  */
  public void writeAIMLIFFiles() {
  return;
  /**
  if (MagicBooleans.trace_mode) System.out.println("writeAIMLIFFiles");
  HashMap<String, BufferedWriter> fileMap = new HashMap<String, BufferedWriter>();
  Category b = new Category(0, "BRAIN BUILD", "*", "*", new Date().toString(), "update.aiml");
  brain.addCategory(b);
  ArrayList<Category> brainCategories = brain.getCategories();
  Collections.sort(brainCategories, Category.CATEGORY_NUMBER_COMPARATOR);
  for (Category c : brainCategories) {
    try {
    BufferedWriter bw;
    String fileName = c.getFilename();
    if (fileMap.containsKey(fileName)) bw = fileMap.get(fileName); else {
      bw = new BufferedWriter(new FileWriter(aimlif_path + "/" + fileName + MagicStrings.aimlif_file_suffix));
      fileMap.put(fileName, bw);
    }
    bw.write(Category.categoryToIF(c));
    bw.newLine();
    } catch (Exception ex) {
    ex.printStackTrace();
    }
  }
  Set set = fileMap.keySet();
  for (Object aSet : set) {
    BufferedWriter bw = fileMap.get(aSet);
      //Close the bw
    try {
    if (bw != null) {
      bw.flush();
      bw.close();
    }
    } catch (IOException ex) {
    ex.printStackTrace();
    }
  }
  File dir = new File(aimlif_path);
  dir.setLastModified(new Date().getTime());*/
  }

  /**
  Write all AIML files. Adds categories for BUILD and DEVELOPMENT ENVIRONMENT
  */
  public void writeAIMLFiles() {
  return;
  /*if (MagicBooleans.trace_mode) System.out.println("writeAIMLFiles");
  HashMap<String, BufferedWriter> fileMap = new HashMap<String, BufferedWriter>();
  Category b = new Category(0, "BRAIN BUILD", "*", "*", new Date().toString(), "update.aiml");
  brain.addCategory(b);
    //b = new Category(0, "PROGRAM VERSION", "*", "*", MagicStrings.program_name_version, "update.aiml");
    //brain.addCategory(b);
  ArrayList<Category> brainCategories = brain.getCategories();
  Collections.sort(brainCategories, Category.CATEGORY_NUMBER_COMPARATOR);
  for (Category c : brainCategories) {
    try { //!c.getFilename().equals(MagicStrings.null_aiml_file)) try {
        //System.out.println("Writing "+c.getCategoryNumber()+" "+c.inputThatTopic());
    BufferedWriter bw;
    String fileName = c.getFilename();
    if (fileMap.containsKey(fileName)) bw = fileMap.get(fileName); else {
      String copyright = Utilities.getCopyright(this, fileName);
      bw = new BufferedWriter(new FileWriter(aiml_path + "/" + fileName));
      fileMap.put(fileName, bw);
      bw.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + "\n" + "\n");
      //bw.write(copyright);
    }
    bw.write(Category.categoryToAIML(c) + "\n");
    } catch (Exception ex) {
    ex.printStackTrace();
    }
  }
  Set set = fileMap.keySet();
  for (Object aSet : set) {
    BufferedWriter bw = fileMap.get(aSet);
      //Close the bw
    try {
    if (bw != null) {
      bw.write("\n");
      bw.flush();
      bw.close();
    }
    } catch (IOException ex) {
    ex.printStackTrace();
    }
  }
  File dir = new File(aiml_path);
  dir.setLastModified(new Date().getTime());*/
  }

  /**
  load bot properties
  */
  void addProperties() {
  try {
    properties.getProperties(config_path + "/properties.txt");
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  }

  /**
  read AIMLIF categories from a file into bot brain
   *
  @param filename ame of AIMLIF file
  @return rray list of categories read
  */
  public ArrayList<Category> readIFCategories(String filename) {
  ArrayList<Category> categories = new ArrayList<Category>();
  try {
    // Open the file that is the first
    // command line parameter
    FileInputStream fstream = new FileInputStream(filename);
    // Get the object
    BufferedReader br = new BufferedReader(new InputStreamReader(fstream));
    String strLine;
    //Read File Line By Line
    while ((strLine = br.readLine()) != null) {
    try {
      Category c = Category.IFToCategory(strLine);
      categories.add(c);
    } catch (Exception ex) {
      System.out.println("Invalid AIMLIF in " + filename + " line " + strLine);
    }
    }
    //Close the input stream
    br.close();
  } catch (IOException e) {
    //Catch exception if any
    System.err.println("Error: " + e.getMessage());
  }
  return categories;
  }

  /**
  Load all AIML Sets
  */
  int addAIMLSets() {
  int cnt = 0;
  Timer timer = new Timer();
  timer.start();
  try {
      // Directory path here
    String file;
    File folder = new File(sets_path);
    if (folder.exists()) {
    File[] listOfFiles = IOUtils.listFiles(folder);
    if (MagicBooleans.trace_mode) System.out.println("Loading AIML Sets files from " + sets_path);
    for (File listOfFile : listOfFiles) {
      if (listOfFile.isFile()) {
      file = listOfFile.getName();
      if (file.endsWith(".txt") || file.endsWith(".TXT")) {
        if (MagicBooleans.trace_mode) System.out.println(file);
        String setName = file.substring(0, file.length() - ".txt".length());
        if (MagicBooleans.trace_mode) System.out.println("Read AIML Set " + setName);
        AIMLSet aimlSet = new AIMLSet(setName, this);
        cnt += aimlSet.readAIMLSet(this);
        setMap.put(setName, aimlSet);
      }
      }
    }
    } else System.out.println("addAIMLSets: " + sets_path + " does not exist.");
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  return cnt;
  }

  /**
  Load all AIML Maps
  */
  int addAIMLMaps() {
  int cnt = 0;
  Timer timer = new Timer();
  timer.start();
  try {
      // Directory path here
    String file;
    File folder = new File(maps_path);
    if (folder.exists()) {
    File[] listOfFiles = IOUtils.listFiles(folder);
    if (MagicBooleans.trace_mode) System.out.println("Loading AIML Map files from " + maps_path);
    for (File listOfFile : listOfFiles) {
      if (listOfFile.isFile()) {
      file = listOfFile.getName();
      if (file.endsWith(".txt") || file.endsWith(".TXT")) {
        if (MagicBooleans.trace_mode) System.out.println(file);
        String mapName = file.substring(0, file.length() - ".txt".length());
        if (MagicBooleans.trace_mode) System.out.println("Read AIML Map " + mapName);
        AIMLMap aimlMap = new AIMLMap(mapName, this);
        cnt += aimlMap.readAIMLMap(this);
        mapMap.put(mapName, aimlMap);
      }
      }
    }
    } else System.out.println("addAIMLMaps: " + maps_path + " does not exist.");
  } catch (Exception ex) {
    ex.printStackTrace();
  }
  return cnt;
  }

  public void deleteLearnfCategories() {
  ArrayList<Category> learnfCategories = learnfGraph.getCategories();
  for (Category c : learnfCategories) {
    Nodemapper n = brain.findNode(c);
    System.out.println("Found node " + n + " for " + c.inputThatTopic());
    if (n != null) n.category = null;
  }
  learnfGraph = new Graphmaster(this);
  }

  public void deleteLearnCategories() {
  ArrayList<Category> learnCategories = learnGraph.getCategories();
  for (Category c : learnCategories) {
    Nodemapper n = brain.findNode(c);
    System.out.println("Found node " + n + " for " + c.inputThatTopic());
    if (n != null) n.category = null;
  }
  learnGraph = new Graphmaster(this);
  }

  /**
  check Graphmaster for shadowed categories
  */
  public void shadowChecker() {
  shadowChecker(brain.root);
  }

  /** traverse graph and test all categories found in leaf nodes for shadows
   *
   */
  void shadowChecker(Nodemapper node) {
  if (NodemapperOperator.isLeaf(node)) {
    String input = node.category.getPattern();
    input = brain.replaceBotProperties(input);
    input = input.replace("*", "XXX").replace("_", "XXX").replace("^", "").replace("#", "");
    String that = node.category.getThat().replace("*", "XXX").replace("_", "XXX").replace("^", "").replace("#", "");
    String topic = node.category.getTopic().replace("*", "XXX").replace("_", "XXX").replace("^", "").replace("#", "");
    input = instantiateSets(input);
    System.out.println("shadowChecker: input=" + input);
    Nodemapper match = brain.match(input, that, topic);
    if (match != node) {
    System.out.println("" + Graphmaster.inputThatTopic(input, that, topic));
    System.out.println("MATCHED: " + match.category.inputThatTopic());
    System.out.println("SHOULD MATCH:" + node.category.inputThatTopic());
    }
  } else {
    for (String key : NodemapperOperator.keySet(node)) {
    shadowChecker(NodemapperOperator.get(node, key));
    }
  }
  }

  public String instantiateSets(String pattern) {
  String[] splitPattern = pattern.split(" ");
  pattern = "";
  for (String x : splitPattern) {
    if (x.startsWith("<SET>")) {
    String setName = AIMLProcessor.trimTag(x, "SET");
    AIMLSet set = setMap.get(setName);
    if (set != null) x = "FOUNDITEM"; else x = "NOTFOUND";
    }
    pattern = pattern + " " + x;
  }
  return pattern.trim();
  }
}