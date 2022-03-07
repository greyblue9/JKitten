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
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class NodemapperOperator {

    /**
     * number of branches from node
     *
     * @param node odemapper object
     * @return umber of branches
     */
  public static int size(Nodemapper node) {
    HashSet set = new HashSet();
    if (node.shortCut) set.add("<THAT>");
    if (node.key != null) set.add(node.key);
    if (node.map != null) set.addAll(node.map.keySet());
    return set.size();
  }

    /**
     * insert a new link from this node to another, by adding a key, value pair
     *
     * @param node odemapper object
     * @param key ey word
     * @param value ord maps to this next node
     */
  public static void put(Nodemapper node, String key, Nodemapper value) {
    if (node.map != null) {
      node.map.put(key, value);
    } else {
            // node.type == unary_node_mapper
      node.key = key;
      node.value = value;
    }
  }

    /**
     * get the node linked to this one by the word key
     *
     * @param node odemapper object
     * @param key ey word to map
     * @return he mapped node or null if the key is not found
     */
  public static Nodemapper get(Nodemapper node, String key) {
    if (node.map != null) {
      return node.map.get(key);
    } else {
            // node.type == unary_node_mapper
      if (key.equals(node.key)) return node.value; else return null;
    }
  }

    /**
     * check whether a node contains a particular key
     *
     * @param node odemapper object
     * @param key ey to test
     * @return rue or false
     */
  public static boolean containsKey(Nodemapper node, String key) {
        //System.out.println("containsKey: Node="+node+" Map="+node.map);
    if (node.map != null) {
      return node.map.containsKey(key);
    } else {
            // node.type == unary_node_mapper
      if (key.equals(node.key)) return true; else return false;
    }
  }

    /**
     * print all node keys
     *
     * @param node Nodemapper object
     */
  public static void printKeys(Nodemapper node) {
    Set set = keySet(node);
    Iterator iter = set.iterator();
    while (iter.hasNext()) {
      System.out.println("" + iter.next());
    }
  }

    /**
     * get key set of a node
     *
     * @param node odemapper object
     * @return et of keys
     */
  public static Set<String> keySet(Nodemapper node) {
    if (node.map != null) {
      return node.map.keySet();
    } else {
            // node.type == unary_node_mapper
      Set set = new HashSet<String>();
      if (node.key != null) set.add(node.key);
      return set;
    }
  }

    /**
     * test whether a node is a leaf
     *
     * @param node odemapper object
     * @return rue or false
     */
  public static boolean isLeaf(Nodemapper node) {
    return (node.category != null);
  }

    /**
     * upgrade a node from a singleton to a multi-way map
     *
     * @param node odemapper object
     */
  public static void upgrade(Nodemapper node) {
        //System.out.println("Upgrading "+node.id);
        //node.type = MagicNumbers.hash_node_mapper;
    node.map = new HashMap<String, Nodemapper>();
    node.map.put(node.key, node.value);
    node.key = null;
    node.value = null;
  }
}
