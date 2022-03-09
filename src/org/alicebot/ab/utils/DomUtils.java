package org.alicebot.ab.utils;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class DomUtils {

  public static Node parseFile(String fileName) throws ParserConfigurationException, SAXException, IOException {
  File file = new File(fileName);
  DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
  DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
    // from AIMLProcessor.evalTemplate and AIMLProcessor.validTemplate:
    // dbFactory.setIgnoringComments(true); // fix this
  dbFactory.setCoalescing(true);
  dbFactory.setExpandEntityReferences(true);
  dbFactory.setIgnoringComments(true);
  dbFactory.setIgnoringElementContentWhitespace(true);
  dbFactory.setValidating(false);
  dbFactory.setXIncludeAware(false);
  final Document doc = dBuilder.parse(file);
  doc.getDocumentElement().normalize();
  Node root = doc.getDocumentElement();
  return root;
  }

  public static Node parseString(String string) throws Exception {
  try (InputStream is = new ByteArrayInputStream(string.getBytes(StandardCharsets.UTF_16))) {
    DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
    DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
    // from AIMLProcessor.evalTemplate and AIMLProcessor.validTemplate:

    Document doc = dBuilder.parse(is);
    doc.getDocumentElement().normalize();
    Node root = doc.getDocumentElement();
    return root;
  }

  }

  /**
  convert an XML node to an XML statement
  @param node urrent XML node
  @return ML string
  */
  public static String nodeToString(Node node) {
    //MagicBooleans.trace("nodeToString(node: " + node + ")");
  StringWriter sw = new StringWriter();
  try {
    Transformer t = TransformerFactory.newInstance().newTransformer();
    t.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
    t.setOutputProperty(OutputKeys.INDENT, "no");
    t.transform(new DOMSource(node), new StreamResult(sw));
  } catch (TransformerException te) {
    System.out.println("nodeToString Transformer Exception");
  }
  String result = sw.toString();
    //MagicBooleans.trace("nodeToString() returning: " + result);
  return result;
  }
}
