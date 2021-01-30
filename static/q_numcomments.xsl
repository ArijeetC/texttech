<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <head>
                <title>2015 Movie Review</title>
            </head>
            <body>
            <h1>Movie Review</h1>
            <p>Query Results: Most discussed movies</p>
            <table border="1" style="margin-left: auto; margin-right: auto;">
                <tr>
                    <th style="text-align:left">movie_name</th>
                    <th style="text-align:left">genre</th>
                    <th style="text-align:left">year</th>
                    <th style="text-align:left">num_comments</th>
                </tr>

                <xsl:for-each select="movies/movie">
                    <xsl:sort select="num_comments" data-type="number" order="descending"/>
                    <xsl:if test="num_comments &gt;500">
                        <tr>
                            <td><xsl:value-of select="title"/></td>
                            <td><xsl:value-of select="genre"/></td>
                            <td><xsl:value-of select="year"/></td>
                            <td><xsl:value-of select="num_comments"/></td>
                        </tr>
                    </xsl:if>
                </xsl:for-each>
            </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>