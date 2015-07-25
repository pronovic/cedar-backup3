# -*- coding: iso-8859-1 -*-
# vim: set ft=python ts=3 sw=3 expandtab:
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#              C E D A R
#          S O L U T I O N S       "Software done right."
#           S O F T W A R E
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Copyright (c) 2004-2006,2010,2015 Kenneth J. Pronovici.
# All rights reserved.
#
# Portions Copyright (c) 2000 Fourthought Inc, USA.
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License,
# Version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copies of the GNU General Public License are available from
# the Free Software Foundation website, http://www.gnu.org/.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : Python 3 (>= 3.4)
# Project  : Cedar Backup, release 3
# Purpose  : Provides general XML-related functionality.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

########################################################################
# Module documentation
########################################################################

"""
Provides general XML-related functionality.

What I'm trying to do here is abstract much of the functionality that directly
accesses the DOM tree.  This is not so much to "protect" the other code from
the DOM, but to standardize the way it's used.  It will also help extension
authors write code that easily looks more like the rest of Cedar Backup.

@sort: createInputDom, createOutputDom, serializeDom, isElement, readChildren, 
       readFirstChild, readStringList, readString, readInteger, readBoolean,
       addContainerNode, addStringNode, addIntegerNode, addBooleanNode,
       TRUE_BOOLEAN_VALUES, FALSE_BOOLEAN_VALUES, VALID_BOOLEAN_VALUES

@var TRUE_BOOLEAN_VALUES: List of boolean values in XML representing C{True}.
@var FALSE_BOOLEAN_VALUES: List of boolean values in XML representing C{False}.
@var VALID_BOOLEAN_VALUES: List of valid boolean values in XML.

@author: Kenneth J. Pronovici <pronovic@ieee.org>
"""
# pylint: disable=C0111,C0103,W0511,W0104,W0106

########################################################################
# Imported modules
########################################################################

# System modules
import sys
import re
import logging
import codecs
from io import StringIO

# XML-related modules
from xml.parsers.expat import ExpatError
from xml.dom.minidom import Node
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString


########################################################################
# Module-wide constants and variables
########################################################################

logger = logging.getLogger("CedarBackup3.log.xml")

TRUE_BOOLEAN_VALUES   = [ "Y", "y", ]
FALSE_BOOLEAN_VALUES  = [ "N", "n", ]
VALID_BOOLEAN_VALUES  = TRUE_BOOLEAN_VALUES + FALSE_BOOLEAN_VALUES


########################################################################
# Functions for creating and parsing DOM trees
########################################################################

def createInputDom(xmlData, name="cb_config"):
   """
   Creates a DOM tree based on reading an XML string.
   @param name: Assumed base name of the document (root node name).
   @return: Tuple (xmlDom, parentNode) for the parsed document
   @raise ValueError: If the document can't be parsed.
   """
   try:
      xmlDom = parseString(xmlData)
      parentNode = readFirstChild(xmlDom, name)
      return (xmlDom, parentNode)
   except (IOError, ExpatError) as e:
      raise ValueError("Unable to parse XML document: %s" % e)

def createOutputDom(name="cb_config"):
   """
   Creates a DOM tree used for writing an XML document.
   @param name: Base name of the document (root node name).
   @return: Tuple (xmlDom, parentNode) for the new document
   """
   impl = getDOMImplementation()
   xmlDom = impl.createDocument(None, name, None)
   return (xmlDom, xmlDom.documentElement)


########################################################################
# Functions for reading values out of XML documents
########################################################################

def isElement(node):
   """
   Returns True or False depending on whether the XML node is an element node.
   """
   return node.nodeType == Node.ELEMENT_NODE

def readChildren(parent, name):
   """
   Returns a list of nodes with a given name immediately beneath the
   parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   Underneath, we use the Python C{getElementsByTagName} method, which is
   pretty cool, but which (surprisingly?) returns a list of all children
   with a given name below the parent, at any level.  We just prune that
   list to include only children whose C{parentNode} matches the passed-in
   parent.

   @param parent: Parent node to search beneath.
   @param name: Name of nodes to search for.

   @return: List of child nodes with correct parent, or an empty list if
   no matching nodes are found.
   """
   lst = []
   if parent is not None:
      result = parent.getElementsByTagName(name)
      for entry in result:
         if entry.parentNode is parent:
            lst.append(entry)
   return lst

def readFirstChild(parent, name):
   """
   Returns the first child with a given name immediately beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: First properly-named child of parent, or C{None} if no matching nodes are found.
   """
   result = readChildren(parent, name)
   if result is None or result == []:
      return None
   return result[0]

def readStringList(parent, name):
   """
   Returns a list of the string contents associated with nodes with a given
   name immediately beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   First, we find all of the nodes using L{readChildren}, and then we
   retrieve the "string contents" of each of those nodes.  The returned list
   has one entry per matching node.  We assume that string contents of a
   given node belong to the first C{TEXT_NODE} child of that node.  Nodes
   which have no C{TEXT_NODE} children are not represented in the returned
   list.

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: List of strings as described above, or C{None} if no matching nodes are found.
   """
   lst = []
   result = readChildren(parent, name)
   for entry in result:
      if entry.hasChildNodes():
         for child in entry.childNodes:
            if child.nodeType == Node.TEXT_NODE:
               lst.append(child.nodeValue)
               break
   if lst == []:
      lst = None
   return lst

def readString(parent, name):
   """
   Returns string contents of the first child with a given name immediately
   beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  We assume that string
   contents of a given node belong to the first C{TEXT_NODE} child of that
   node.

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: String contents of node or C{None} if no matching nodes are found.
   """
   result = readStringList(parent, name)
   if result is None:
      return None
   return result[0]

def readInteger(parent, name):
   """
   Returns integer contents of the first child with a given name immediately
   beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: Integer contents of node or C{None} if no matching nodes are found.
   @raise ValueError: If the string at the location can't be converted to an integer.
   """
   result = readString(parent, name)
   if result is None:
      return None
   else:
      return int(result)

def readLong(parent, name):
   """
   Returns long integer contents of the first child with a given name immediately
   beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: Long integer contents of node or C{None} if no matching nodes are found.
   @raise ValueError: If the string at the location can't be converted to an integer.
   """
   result = readString(parent, name)
   if result is None:
      return None
   else:
      return int(result)

def readFloat(parent, name):
   """
   Returns float contents of the first child with a given name immediately
   beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: Float contents of node or C{None} if no matching nodes are found.
   @raise ValueError: If the string at the location can't be converted to a
   float value.
   """
   result = readString(parent, name)
   if result is None:
      return None
   else:
      return float(result)

def readBoolean(parent, name):
   """
   Returns boolean contents of the first child with a given name immediately
   beneath the parent.

   By "immediately beneath" the parent, we mean from among nodes that are
   direct children of the passed-in parent node.  

   The string value of the node must be one of the values in L{VALID_BOOLEAN_VALUES}.

   @param parent: Parent node to search beneath.
   @param name: Name of node to search for.

   @return: Boolean contents of node or C{None} if no matching nodes are found.
   @raise ValueError: If the string at the location can't be converted to a boolean.
   """
   result = readString(parent, name)
   if result is None:
      return None
   else:
      if result in TRUE_BOOLEAN_VALUES:
         return True
      elif result in FALSE_BOOLEAN_VALUES:
         return False
      else:
         raise ValueError("Boolean values must be one of %s." % VALID_BOOLEAN_VALUES)


########################################################################
# Functions for writing values into XML documents
########################################################################

def addContainerNode(xmlDom, parentNode, nodeName):
   """
   Adds a container node as the next child of a parent node.

   @param xmlDom: DOM tree as from C{impl.createDocument()}.
   @param parentNode: Parent node to create child for.
   @param nodeName: Name of the new container node.

   @return: Reference to the newly-created node.
   """
   containerNode = xmlDom.createElement(nodeName)
   parentNode.appendChild(containerNode)
   return containerNode

def addStringNode(xmlDom, parentNode, nodeName, nodeValue):
   """
   Adds a text node as the next child of a parent, to contain a string.

   If the C{nodeValue} is None, then the node will be created, but will be
   empty (i.e. will contain no text node child).

   @param xmlDom: DOM tree as from C{impl.createDocument()}.
   @param parentNode: Parent node to create child for.
   @param nodeName: Name of the new container node.
   @param nodeValue: The value to put into the node.

   @return: Reference to the newly-created node.
   """
   containerNode = addContainerNode(xmlDom, parentNode, nodeName)
   if nodeValue is not None:
      textNode = xmlDom.createTextNode(nodeValue)
      containerNode.appendChild(textNode)
   return containerNode

def addIntegerNode(xmlDom, parentNode, nodeName, nodeValue):
   """
   Adds a text node as the next child of a parent, to contain an integer.

   If the C{nodeValue} is None, then the node will be created, but will be
   empty (i.e. will contain no text node child).

   The integer will be converted to a string using "%d".  The result will be
   added to the document via L{addStringNode}.

   @param xmlDom: DOM tree as from C{impl.createDocument()}.
   @param parentNode: Parent node to create child for.
   @param nodeName: Name of the new container node.
   @param nodeValue: The value to put into the node.

   @return: Reference to the newly-created node.
   """
   if nodeValue is None:
      return addStringNode(xmlDom, parentNode, nodeName, None)
   else:
      return addStringNode(xmlDom, parentNode, nodeName, "%d" % nodeValue) # %d works for both int and long

def addLongNode(xmlDom, parentNode, nodeName, nodeValue):
   """
   Adds a text node as the next child of a parent, to contain a long integer.

   If the C{nodeValue} is None, then the node will be created, but will be
   empty (i.e. will contain no text node child).

   The integer will be converted to a string using "%d".  The result will be
   added to the document via L{addStringNode}.

   @param xmlDom: DOM tree as from C{impl.createDocument()}.
   @param parentNode: Parent node to create child for.
   @param nodeName: Name of the new container node.
   @param nodeValue: The value to put into the node.

   @return: Reference to the newly-created node.
   """
   if nodeValue is None:
      return addStringNode(xmlDom, parentNode, nodeName, None)
   else:
      return addStringNode(xmlDom, parentNode, nodeName, "%d" % nodeValue) # %d works for both int and long

def addBooleanNode(xmlDom, parentNode, nodeName, nodeValue):
   """
   Adds a text node as the next child of a parent, to contain a boolean.

   If the C{nodeValue} is None, then the node will be created, but will be
   empty (i.e. will contain no text node child).

   Boolean C{True}, or anything else interpreted as C{True} by Python, will
   be converted to a string "Y".  Anything else will be converted to a
   string "N".  The result is added to the document via L{addStringNode}.

   @param xmlDom: DOM tree as from C{impl.createDocument()}.
   @param parentNode: Parent node to create child for.
   @param nodeName: Name of the new container node.
   @param nodeValue: The value to put into the node.

   @return: Reference to the newly-created node.
   """
   if nodeValue is None:
      return addStringNode(xmlDom, parentNode, nodeName, None)
   else:
      if nodeValue:
         return addStringNode(xmlDom, parentNode, nodeName, "Y")
      else:
         return addStringNode(xmlDom, parentNode, nodeName, "N")


########################################################################
# Functions for serializing DOM trees
########################################################################

def serializeDom(xmlDom, indent=3):
   """
   Serializes a DOM tree and returns the result in a string.
   @param xmlDom: XML DOM tree to serialize
   @param indent: Number of spaces to indent, as an integer
   @return: String form of DOM tree, pretty-printed.
   """
   xmlBuffer = StringIO()
   serializer = Serializer(xmlBuffer, "UTF-8", indent=indent)
   serializer.serialize(xmlDom)
   xmlData = xmlBuffer.getvalue()
   xmlBuffer.close()
   return xmlData 

class Serializer(object):

   """
   XML serializer class.

   This is a customized serializer that I hacked together based on what I found
   in the PyXML distribution.  Basically, around release 2.7.0, the only reason
   I still had around a dependency on PyXML was for the PrettyPrint
   functionality, and that seemed pointless.  So, I stripped the PrettyPrint
   code out of PyXML and hacked bits of it off until it did just what I needed
   and no more.  

   This code started out being called PrintVisitor, but I decided it makes more
   sense just calling it a serializer.  I've made nearly all of the methods
   private, and I've added a new high-level serialize() method rather than
   having clients call C{visit()}.

   Anyway, as a consequence of my hacking with it, this can't quite be called a
   complete XML serializer any more.  I ripped out support for HTML and XHTML,
   and there is also no longer any support for namespaces (which I took out
   because this dragged along a lot of extra code, and Cedar Backup doesn't use
   namespaces).  However, everything else should pretty much work as expected.

   @copyright: This code, prior to customization, was part of the PyXML
   codebase, and before that was part of the 4DOM suite developed by
   Fourthought, Inc.  It its original form, it was Copyright (c) 2000
   Fourthought Inc, USA; All Rights Reserved.
   """

   def __init__(self, stream=sys.stdout, encoding="UTF-8", indent=3):
      """
      Initialize a serializer.
      @param stream: Stream to write output to.
      @param encoding: Output encoding.
      @param indent: Number of spaces to indent, as an integer
      """
      self.stream = stream
      self.encoding = encoding
      self._indent = indent * " "
      self._depth = 0
      self._inText = 0

   def serialize(self, xmlDom):
      """
      Serialize the passed-in XML document.
      @param xmlDom: XML DOM tree to serialize
      @raise ValueError: If there's an unknown node type in the document.
      """
      self._visit(xmlDom)
      self.stream.write("\n")

   def _write(self, text):
      obj = _encodeText(text, self.encoding)
      self.stream.write(obj)
      return

   def _tryIndent(self):
      if not self._inText and self._indent:
         self._write('\n' + self._indent*self._depth)
      return

   def _visit(self, node):
      """
      @raise ValueError: If there's an unknown node type in the document.
      """
      if node.nodeType == Node.ELEMENT_NODE:
         return self._visitElement(node)

      elif node.nodeType == Node.ATTRIBUTE_NODE:
         return self._visitAttr(node)

      elif node.nodeType == Node.TEXT_NODE:
         return self._visitText(node)

      elif node.nodeType == Node.CDATA_SECTION_NODE:
         return self._visitCDATASection(node)

      elif node.nodeType == Node.ENTITY_REFERENCE_NODE:
         return self._visitEntityReference(node)

      elif node.nodeType == Node.ENTITY_NODE:
         return self._visitEntity(node)

      elif node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
         return self._visitProcessingInstruction(node)

      elif node.nodeType == Node.COMMENT_NODE:
         return self._visitComment(node)

      elif node.nodeType == Node.DOCUMENT_NODE:
         return self._visitDocument(node)

      elif node.nodeType == Node.DOCUMENT_TYPE_NODE:
         return self._visitDocumentType(node)

      elif node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
         return self._visitDocumentFragment(node)

      elif node.nodeType == Node.NOTATION_NODE:
         return self._visitNotation(node)

      # It has a node type, but we don't know how to handle it
      raise ValueError("Unknown node type: %s" % repr(node))

   def _visitNodeList(self, node, exclude=None):
      for curr in node:
         curr is not exclude and self._visit(curr)
      return

   def _visitNamedNodeMap(self, node):
      for item in list(node.values()):
         self._visit(item)
      return

   def _visitAttr(self, node):
      self._write(' ' + node.name)
      value = node.value
      text = _translateCDATA(value, self.encoding)
      text, delimiter = _translateCDATAAttr(text)
      self.stream.write("=%s%s%s" % (delimiter, text, delimiter))
      return

   def _visitProlog(self):
      self._write("<?xml version='1.0' encoding='%s'?>" % (self.encoding or 'utf-8'))
      self._inText = 0
      return

   def _visitDocument(self, node):
      self._visitProlog()
      node.doctype and self._visitDocumentType(node.doctype)
      self._visitNodeList(node.childNodes, exclude=node.doctype)
      return

   def _visitDocumentFragment(self, node):
      self._visitNodeList(node.childNodes)
      return

   def _visitElement(self, node):
      self._tryIndent()
      self._write('<%s' % node.tagName)
      for attr in list(node.attributes.values()):
         self._visitAttr(attr)
      if len(node.childNodes):
         self._write('>')
         self._depth = self._depth + 1
         self._visitNodeList(node.childNodes)
         self._depth = self._depth - 1
         not (self._inText) and self._tryIndent()
         self._write('</%s>' % node.tagName)
      else:
         self._write('/>')
      self._inText = 0
      return

   def _visitText(self, node):
      text = node.data
      if self._indent:
         text.strip()
      if text:
         text = _translateCDATA(text, self.encoding)
         self.stream.write(text)
         self._inText = 1
      return

   def _visitDocumentType(self, doctype):
      if not doctype.systemId and not doctype.publicId: return
      self._tryIndent()
      self._write('<!DOCTYPE %s' % doctype.name)
      if doctype.systemId and '"' in doctype.systemId:
         system = "'%s'" % doctype.systemId
      else:
         system = '"%s"' % doctype.systemId
      if doctype.publicId and '"' in doctype.publicId:
         # We should probably throw an error
         # Valid characters:  <space> | <newline> | <linefeed> |
         #                    [a-zA-Z0-9] | [-'()+,./:=?;!*#@$_%]
         public = "'%s'" % doctype.publicId
      else:
         public = '"%s"' % doctype.publicId
      if doctype.publicId and doctype.systemId:
         self._write(' PUBLIC %s %s' % (public, system))
      elif doctype.systemId:
         self._write(' SYSTEM %s' % system)
      if doctype.entities or doctype.notations:
         self._write(' [')
         self._depth = self._depth + 1
         self._visitNamedNodeMap(doctype.entities)
         self._visitNamedNodeMap(doctype.notations)
         self._depth = self._depth - 1
         self._tryIndent()
         self._write(']>')
      else:
         self._write('>')
      self._inText = 0
      return

   def _visitEntity(self, node):
      """Visited from a NamedNodeMap in DocumentType"""
      self._tryIndent()
      self._write('<!ENTITY %s' % (node.nodeName))
      node.publicId and self._write(' PUBLIC %s' % node.publicId)
      node.systemId and self._write(' SYSTEM %s' % node.systemId)
      node.notationName and self._write(' NDATA %s' % node.notationName)
      self._write('>')
      return

   def _visitNotation(self, node):
      """Visited from a NamedNodeMap in DocumentType"""
      self._tryIndent()
      self._write('<!NOTATION %s' % node.nodeName)
      node.publicId and self._write(' PUBLIC %s' % node.publicId)
      node.systemId and self._write(' SYSTEM %s' % node.systemId)
      self._write('>')
      return

   def _visitCDATASection(self, node):
      self._tryIndent()
      self._write('<![CDATA[%s]]>' % (node.data))
      self._inText = 0
      return

   def _visitComment(self, node):
      self._tryIndent()
      self._write('<!--%s-->' % (node.data))
      self._inText = 0
      return

   def _visitEntityReference(self, node):
      self._write('&%s;' % node.nodeName)
      self._inText = 1
      return

   def _visitProcessingInstruction(self, node):
      self._tryIndent()
      self._write('<?%s %s?>' % (node.target, node.data))
      self._inText = 0
      return

def _encodeText(text, encoding):
   """Encodes the passed-in text as UTF-8."""
   return text.encode("utf-8")

def _translateCDATAAttr(characters):
   """
   Handles normalization and some intelligence about quoting.

   @copyright: This code, prior to customization, was part of the PyXML
   codebase, and before that was part of the 4DOM suite developed by
   Fourthought, Inc.  It its original form, it was Copyright (c) 2000
   Fourthought Inc, USA; All Rights Reserved.
   """
   if not characters:
      return '', "'"
   if "'" in characters:
      delimiter = '"'
      new_chars = re.sub('"', '&quot;', characters)
   else:
      delimiter = "'"
      new_chars = re.sub("'", '&apos;', characters)
   #FIXME: There's more to normalization
   #Convert attribute new-lines to character entity
   # characters is possibly shorter than new_chars (no entities)
   if "\n" in characters:
      new_chars = re.sub('\n', '&#10;', new_chars)
   return new_chars, delimiter

#Note: Unicode object only for now
def _translateCDATA(characters, encoding='UTF-8', prev_chars='', markupSafe=0):
   """
   @copyright: This code, prior to customization, was part of the PyXML
   codebase, and before that was part of the 4DOM suite developed by
   Fourthought, Inc.  It its original form, it was Copyright (c) 2000
   Fourthought Inc, USA; All Rights Reserved.
   """
   CDATA_CHAR_PATTERN = re.compile('[&<]|]]>')
   CHAR_TO_ENTITY = { '&': '&amp;', '<': '&lt;', ']]>': ']]&gt;', }
   ILLEGAL_LOW_CHARS = '[\x01-\x08\x0B-\x0C\x0E-\x1F]'
   ILLEGAL_HIGH_CHARS = '\xEF\xBF[\xBE\xBF]'
   XML_ILLEGAL_CHAR_PATTERN = re.compile('%s|%s'%(ILLEGAL_LOW_CHARS, ILLEGAL_HIGH_CHARS))
   if not characters:
      return ''
   if not markupSafe:
      if CDATA_CHAR_PATTERN.search(characters):
         new_string = CDATA_CHAR_PATTERN.subn(lambda m, d=CHAR_TO_ENTITY: d[m.group()], characters)[0]
      else:
         new_string = characters
      if prev_chars[-2:] == ']]' and characters[0] == '>':
         new_string = '&gt;' + new_string[1:]
   else:
      new_string = characters
   #Note: use decimal char entity rep because some browsers are broken
   #FIXME: This will bomb for high characters.  Should, for instance, detect
   #The UTF-8 for 0xFFFE and put out &#xFFFE;
   if XML_ILLEGAL_CHAR_PATTERN.search(new_string):
      new_string = XML_ILLEGAL_CHAR_PATTERN.subn(lambda m: '&#%i;' % ord(m.group()), new_string)[0]
   new_string = _encodeText(new_string, encoding)
   return new_string

