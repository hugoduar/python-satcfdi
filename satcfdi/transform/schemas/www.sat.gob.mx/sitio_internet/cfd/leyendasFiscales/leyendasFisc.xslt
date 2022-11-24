<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:leyendasFisc="http://www.sat.gob.mx/leyendasFiscales" version="2.0"><xsl:output method="text" version="1.0" encoding="UTF-8" indent="no"/><xsl:template match="leyendasFisc:LeyendasFiscales"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@version"/></xsl:call-template><xsl:for-each select="./leyendasFisc:Leyenda"><xsl:apply-templates select="."/></xsl:for-each></xsl:template><xsl:template match="leyendasFisc:Leyenda"><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@disposicionFiscal"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@norma"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@textoLeyenda"/></xsl:call-template></xsl:template></xsl:stylesheet>