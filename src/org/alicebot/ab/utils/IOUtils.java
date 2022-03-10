package org.alicebot.ab.utils;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptContext;
import jdk.nashorn.api.scripting.ScriptObjectMirror;
import com.google.common.collect.Ordering;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.SuffixFileFilter;
import org.apache.commons.io.IOCase;
import org.apache.commons.io.filefilter.TrueFileFilter;
import java.util.*;
import org.apache.commons.lang3.StringEscapeUtils;

public class IOUtils {

  BufferedReader reader;

  BufferedWriter writer;

  public IOUtils(String filePath, String mode) {
  try {
    if (mode.equals("read")) {
    reader = new BufferedReader(new FileReader(filePath));
    } else if (mode.equals("write")) {
    (new File(filePath)).delete();
    writer = new BufferedWriter(new FileWriter(filePath, true));
    }
  } catch (IOException e) {
    System.err.println("error: " + e);
  }
  }

  public String readLine() {
  String result = null;
  try {
    result = reader.readLine();
  } catch (IOException e) {
    System.err.println("error: " + e);
  }
  return result;
  }

  public void writeLine(String line) {
  try {
    writer.write(line);
    writer.newLine();
  } catch (IOException e) {
    System.err.println("error: " + e);
  }
  }

  public void close() {
  try {
    if (reader != null) reader.close();
    if (writer != null) writer.close();
  } catch (IOException e) {
    System.err.println("error: " + e);
  }
  }

  public static void writeOutputTextLine(String prompt, String text) {
  System.out.println(prompt + ": " + text);
  }

  public static String readInputTextLine() {
  return readInputTextLine(null);
  }

  public static String readInputTextLine(String prompt) {
  if (prompt != null) {
    System.out.print(prompt + ": ");
  }
  BufferedReader lineOfText = new BufferedReader(new InputStreamReader(System.in));
  String textLine = null;
  try {
    textLine = lineOfText.readLine();
  } catch (IOException e) {
    e.printStackTrace();
  }
  return textLine;
  }

  public static File[] listFiles(File dir) {
  return dir.listFiles();
  }

  public static String system(String evaluatedContents, String failedString) {
  Runtime rt = Runtime.getRuntime();
    //System.out.println("System "+evaluatedContents);
  try {
    Process p = rt.exec(evaluatedContents);
    InputStream istrm = p.getInputStream();
    InputStreamReader istrmrdr = new InputStreamReader(istrm);
    BufferedReader buffrdr = new BufferedReader(istrmrdr);
    String result = "";
    String data = "";
    while ((data = buffrdr.readLine()) != null) {
    result += data + "\n";
    }
      //System.out.println("Result = "+result);
    return result;
  } catch (Exception ex) {
    ex.printStackTrace();
    return failedString;
  }
  }
  
  static ScriptEngineManager mgr;
  static ScriptEngine engine;
  static ScriptContext ctx;
  static ScriptObjectMirror glob;

  public static String evalScript(String engineName, String script) throws Exception {
    System.err.printf(
      "Evaluating script: %s\n", StringEscapeUtils.escapeJava(script)
    );
    if (glob == null) {
      mgr = new ScriptEngineManager();
      engine = mgr.getEngineByName("JavaScript");
      ctx = engine.getContext();
      glob = (ScriptObjectMirror) ctx.getBindings(ctx.getScopes().get(0));
      
      final List<File> scriptFiles
        = Ordering.usingToString().sortedCopy(
          FileUtils.listFiles(
            new File(".").getAbsoluteFile(),
            new SuffixFileFilter(".js", IOCase.INSENSITIVE),
            TrueFileFilter.TRUE
          )
        );
      
      for (final File scriptFile: scriptFiles) {
        System.err.printf(
          "Parsing script file: %s ...\n", scriptFile
        );
        final Object result = glob.eval(
          FileUtils.readFileToString(scriptFile)
        );
        System.err.printf(
          "Script file result: %s\n", result
        );
        for (final Map.Entry<String, Object> entry:
          glob.entrySet())
        {
          System.err.printf(
            "[%s] = %s\n", entry.getKey(), entry.getValue()
          );
        }
      }
    }
    final Object result = glob.eval(script);
    System.err.printf(
      "glob.eval(%s) returned: %s\n",
      StringEscapeUtils.escapeJava(script),
      result
    );
    return String.valueOf(result);
  }
}