<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <head>
                <title>Movie Review</title>
            </head>
            <body>
            <h1>Word count</h1>
            <p>Query Results</p>
            <table border="1" style="margin-left: auto; margin-right: auto;">
                <tr>
                    <th style="text-align:left">Word</th>
                    <th style="text-align:left">Count</th>
                </tr>
                
                <xsl:for-each select="words/word">
                <xsl:sort select="count" data-type="number" order="descending"/>
                <xsl:if test="count &gt;60">
                    <tr>
                        <td><xsl:value-of select="name"/></td>
                        <td><xsl:value-of select="count"/></td>
                    </tr>
                </xsl:if>
                </xsl:for-each>
            </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
