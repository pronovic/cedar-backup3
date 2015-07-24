<!--
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#              C E D A R
#          S O L U T I O N S       "Software done right."
#           S O F T W A R E
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
# Author   : Kenneth J. Pronovici <pronovic@ieee.org>
# Language : XSLT
# Project  : Cedar Backup, release 2
# Revision : $Id: html-stylesheet.xsl 575 2006-09-04 17:49:19Z pronovic $
# Purpose  : XSLT stylesheet for HTML Docbook output (single page).
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
-->
<!--
   This stylesheet was originally taken from the Subversion project's book
   (http://svnbook.red-bean.com/) and has been modifed for use with Cedar
   Backup.

   The original stylesheet was (c) 2000-2004 CollabNet (see CREDITS).

   The major change that I have made to the stylesheet is to use Debian's
   catalog system for locating the official Docbook stylesheet, rather than
   expecting it to be part of the source tree.  If your operating system does
   not have a working catalog system, then specify an absolute path to a valid
   stylesheet below where html/docbook.xsl is imported (or switch to a real
   operating system).
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version='1.0'>

   <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl"/>

   <xsl:param name="html.stylesheet">styles.css</xsl:param>
   <xsl:param name="toc.section.depth">3</xsl:param>
   <xsl:param name="annotate.toc">0</xsl:param>

   <xsl:template match="sect1" mode="toc">
      <xsl:param name="toc-context" select="."/>
      <xsl:call-template name="subtoc">
         <xsl:with-param name="toc-context" select="$toc-context"/>
         <xsl:with-param name="nodes" select="sect2|refentry|bridgehead[$bridgehead.in.toc != 0]"/>
      </xsl:call-template>
   </xsl:template>

   <xsl:template match="sect2" mode="toc">
      <xsl:param name="toc-context" select="."/>

      <xsl:call-template name="subtoc">
         <xsl:with-param name="toc-context" select="$toc-context"/>
         <xsl:with-param name="nodes" select="sect3|refentry|bridgehead[$bridgehead.in.toc != 0]"/>
      </xsl:call-template>
   </xsl:template>

</xsl:stylesheet>
