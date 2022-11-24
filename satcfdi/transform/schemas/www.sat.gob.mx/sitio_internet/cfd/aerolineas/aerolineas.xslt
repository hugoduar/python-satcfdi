<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:aerolineas="http://www.sat.gob.mx/aerolineas" version="2.0"><xsl:template match="aerolineas:Aerolineas"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Version"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@TUA"/></xsl:call-template><xsl:apply-templates select="./aerolineas:OtrosCargos"/></xsl:template><xsl:template match="aerolineas:OtrosCargos"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@TotalCargos"/></xsl:call-template><xsl:for-each select="./aerolineas:Cargo"><xsl:apply-templates select="."/></xsl:for-each></xsl:template><xsl:template match="aerolineas:Cargo"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@CodigoCargo"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Importe"/></xsl:call-template></xsl:template></xsl:stylesheet>