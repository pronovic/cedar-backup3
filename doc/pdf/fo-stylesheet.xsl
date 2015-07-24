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
# Revision : $Id: fo-stylesheet.xsl 936 2009-03-29 19:35:00Z pronovic $
# Purpose  : XSLT stylesheet for FO Docbook output (used for PDF and Postscript)
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
   stylesheet below where fo/docbook.xsl is imported (or switch to a real
   operating system).

   I have also modified the stylesheet to include "admonition" graphics (for
   warning, tip, note, etc.) in the PDF output, and I now use my own greyscale
   images for PDF and Postscript (taken from nwalsh's originals and modified)
   rather than converting the color images from O'Reilly.
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version='1.0'>

   <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl"/>

   <xsl:param name="fop.extensions" select="1"/>
   <xsl:param name="variablelist.as.blocks" select="1"/>

   <xsl:param name="hyphenate">false</xsl:param>

   <xsl:param name="paper.type" select="'USletter'"/>

   <xsl:param name="page.margin.bottom" select="'0.8in'"/>
   <xsl:param name="page.margin.top" select="'0.8in'"/>

   <xsl:param name="footer.rule" select="0"/>

   <xsl:param name="admon.graphics" select="1"/>
   <xsl:param name="admon.graphics.extension" select="'.png'"/>
   <xsl:param name="admon.graphics.path">images/pdf/</xsl:param>

</xsl:stylesheet>
