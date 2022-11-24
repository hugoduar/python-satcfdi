<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns:vehiculousado="http://www.sat.gob.mx/vehiculousado" version="2.0"><xsl:output method="text" version="1.0" encoding="UTF-8" indent="no"/><xsl:template match="/">|<xsl:apply-templates select="/vehiculousado:VehiculoUsado"/>||</xsl:template><xsl:template match="vehiculousado:VehiculoUsado"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@Version"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@montoAdquisicion"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@montoEnajenacion"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@claveVehicular"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@marca"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@tipo"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@modelo"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@numeroMotor"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@numeroSerie"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@NIV"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@valor"/></xsl:call-template><xsl:apply-templates select="./vehiculousado:InformacionAduanera"/></xsl:template><xsl:template match="vehiculousado:InformacionAduanera"><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@numero"/></xsl:call-template><xsl:call-template name="Requerido"><xsl:with-param name="valor" select="./@fecha"/></xsl:call-template><xsl:call-template name="Opcional"><xsl:with-param name="valor" select="./@aduana"/></xsl:call-template></xsl:template></xsl:stylesheet>