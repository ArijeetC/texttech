<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
    
        <html>
            <head>
                <title>2020 Movie Review</title>
            </head>
            <body>
            <h1>2020 Movie Review</h1>
            <p>Query Results</p>
            <table border="1" style="margin-left: auto; margin-right: auto;">
                <tr>
                    <th style="text-align:left">movie_name</th>
                    <th style="text-align:left">genre</th>
                    <th style="text-align:left">year</th>
                    <th style="text-align:left">label</th>
                    <th style="text-align:left">percentage</th>
                </tr>
                
                <xsl:for-each select="movies/movie[position() &lt; 11]">
                <!--enter the condition here-->
                    <xsl:sort select="percentage" data-type="number" order="descending"/>
                    <xsl:if test="year =2020">
                    <tr>
                        <td><xsl:value-of select="title"/></td>
                        <td><xsl:value-of select="genre"/></td>
                        <td><xsl:value-of select="year"/></td>
                        <td><xsl:value-of select="label"/></td>
                        <td><xsl:value-of select="percentage"/></td>
                    </tr>
                    </xsl:if>
                </xsl:for-each>
            </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>