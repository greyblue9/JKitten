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
import java.util.ArrayList;
import java.util.TreeMap;
import java.util.*;

/**
Nodemapper data structure. In order to minimize memory overhead this class has no methods.
Operations on Nodemapper objects are performed by NodemapperOperator class
*/
public class Nodemapper extends AbstractMap<String, Nodemapper> {
  
  public static final Map<String, Nodemapper> byPattern = new  TreeMap<>();

  /* public static int idCnt=0;
   public int id;*/
  public Category category = null;

  public int height = MagicNumbers.max_graph_height;

  public StarBindings starBindings = null;

  public TreeMap<String, Nodemapper> map = null;

  public String key = null;

  public Nodemapper value = null;

  public boolean shortCut = false;

  public ArrayList<String> sets;
  
  @Override
  public int hashCode() {
    int hash = 0x77;
    hash = (hash << 3) ^ ((category != null) ? category.hashCode(): 0);
    hash = (hash << 3) ^ ((map != null) ? map.keySet().hashCode(): 0);
    hash = (hash << 3) ^ ((value != null) ? value.hashCode(): 0);
    hash = (hash << 3) ^ height;
    return hash;
  }
  
  @Override
  public boolean equals(final Object other) {
    if (!(other instanceof Nodemapper)) return false;
    Nodemapper o = (Nodemapper) other;
    return (
       (category != null && category.equals(o.category))
      || (category == null && o.category == null)
    ) && (
       (map != null && map.keySet().equals(o.map.keySet()))
      || (map == null && o.map == null)
    ) && (
       (value != null && value.equals(o.value))
      || (value == null && o.value == null)
    ) && (
       (height == o.height)
    );
  }
  
  @Override
  public String toString() {
    return String.format(
      "NodeMapper(key=%s, height=%s, category=%s, value=%s map=%s)",
      key, height, category, value, map
    );
  }
  
  public void setCategory(Category category) {
    if (this.category != null) {
      final String oldPattern = this.category.getPattern();
      byPattern.remove(oldPattern);
    }
    this.category = category;
    if (category != null) {
      final String pattern = category.getPattern();
      byPattern.put(pattern, this);
    }
  }
  
  /**
  number of branches from node
   *
  @param node odemapper object
  @return umber of branches
  */
  @Override
  public int size() {
    TreeSet set = new TreeSet();
    if (this.shortCut) set.add("<THAT>");
    if (this.key != null) set.add(this.key);
    if (this.map != null) set.addAll(this.map.keySet());
    return set.size();
  }

  /**
  insert a new link from this node to another, by adding a key, value pair
   *
  @param node odemapper object
  @param key ey word
  @param value ord maps to this next node
  */
  @Override
  public Nodemapper put(String key, Nodemapper value) {
    if (this.map != null) {
      return this.map.put(key, value);
    } else {
      // this.type == unary_node_mapper
      final Nodemapper oldValue = (key.equals(this.key))
        ? this.value
        : null;
      this.key = key;
      this.value = value;
      return oldValue;
    }
  }

  /**
  get the node linked to this one by the word key
  
  @param node odemapper object
  @param key ey word to map
  @return he mapped node or null if the key is not found
  */
  @Override
  public Nodemapper get(Object key) {
    if (this.map != null) {
      return this.map.get(key);
    } else {
      // this.type == unary_node_mapper
      if (key.equals(this.key)) return this.value; else return null;
    }
  }

  /**
  check whether a node contains a particular key
   *
  @param node odemapper object
  @param key ey to test
  @return rue or false
  */
  @Override
  public boolean containsKey(Object key) {
    //System.out.println("containsKey: Node="+this+" Map="+this.map);
    if (this.map != null) {
      return this.map.containsKey(key);
    } else {
      // this.type == unary_node_mapper
      if (key.equals(this.key)) return true; else return false;
    }
  }

  /**
  print all node keys
   *
  @param node Nodemapper object
  */
  public void printKeys() {
    Set set = this.keySet();
    Iterator iter = set.iterator();
    while (iter.hasNext()) {
      System.out.println("" + iter.next());
    }
  }

  /**
  get key set of a node
   *
  @param node odemapper object
  @return et of keys
  */
  @Override
  public Set<String> keySet() {
    if (this.map != null) {
      return this.map.keySet();
    } else {
      // this.type == unary_node_mapper
      Set set = new TreeSet<String>();
      if (this.key != null) set.add(this.key);
      return set;
    }
  }

  /**
  get key set of a node
   *
  @param node odemapper object
  @return et of keys
  */
  @Override
  public Set<Map.Entry<String, Nodemapper>> entrySet() {
    final Set<Map.Entry<String, Nodemapper>> entries
      = new TreeSet<>();
    
    for (final String key: this.keySet()) {
      final Nodemapper value = this.get(key);
      final Map.Entry<String, Nodemapper> entry
        = new AbstractMap.SimpleEntry<>(key, value);
      entries.add(entry);
    }
    return entries;
  }

  /**
  test whether a node is a leaf
   *
  @param node odemapper object
  @return rue or false
  */
  public boolean isLeaf() {
    return (this.category != null);
  }
  
  /**
  upgrade a node from a singleton to a multi-way map
   *
  @param node odemapper object
  */
  public void upgrade() {
    // System.out.println("Upgrading "+this.id);
    // this.type = MagicNumbers.hash_node_mapper;
    this.map = new TreeMap<String, Nodemapper>();
    this.map.put(this.key, this.value);
    this.key = null;
    this.value = null;
  }
}
