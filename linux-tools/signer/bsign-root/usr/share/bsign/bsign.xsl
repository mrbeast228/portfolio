<?xml version="1.0"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html"/>
    <xsl:variable name = "locale" select = "/report/@locale = 'en_GB'" />

    <xsl:template match="/">
        <xsl:param name = "xattr" select = "/report/signatures/signature[ source = 'xattr' ]" />
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                <title>Report</title>
                <style>
                    li { font-family : monospace;
                         list-style-type : none; }
                </style>
            </head>
            <body>
                <h3 align="center">
                    <xsl:choose>
                        <xsl:when test = "/report/mode = 'info'">
                            <xsl:choose>
                                <xsl:when test = "$locale">
                                    <xsl:text>Signature information</xsl:text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Информация о подписях</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:when>
                        <xsl:when test = "/report/mode = 'check'">
                            <xsl:choose>
                                <xsl:when test = "$locale">
                                    <xsl:text>Check signatures</xsl:text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Проверка подписей</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:when>
                    </xsl:choose>
                </h3>
                <table border="1" cellspacing="0" cellpadding="5" align="center">
                    <xsl:choose>
                            <xsl:when test = "count( $xattr ) > 1">
                                <tr>
                                    <th rowspan="2">
                                        <xsl:choose>
                                            <xsl:when test = "$locale">
                                                <xsl:text>File</xsl:text>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:text>Файл</xsl:text>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </th>
                                    <th colspan="2">
                                        <xsl:choose>
                                            <xsl:when test = "$locale">
                                                <xsl:text>Attributes</xsl:text>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:text>Аттрибуты</xsl:text>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </th>
                                </tr>
                                <tr>
                                    <th>
                                        <xsl:choose>
                                            <xsl:when test = "$locale">
                                                <xsl:text>ELF-file</xsl:text>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:text>ELF-файла</xsl:text>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </th>
                                    <th>
                                        <xsl:choose>
                                            <xsl:when test = "$locale">
                                                <xsl:text>External</xsl:text>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:text>Расширенные</xsl:text>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </th>
                                </tr>
                                <xsl:apply-templates select = "$xattr"
                                                     mode = "multiple" />
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:apply-templates select = "$xattr"
                                                     mode = "single" />
                            </xsl:otherwise>
                    </xsl:choose>
                </table>
            </body>
        </html>
    </xsl:template>

    <xsl:template match = "signature"
                  mode = "multiple" >
        <xsl:param name = "internal" select = "/report/signatures/signature[ source ='internal']" />
        <tr>
            <td>
                <xsl:value-of select = "file" />
            </td>
             <td>
                <xsl:apply-templates select = "$internal/.[file = current()/file]/result"/>
            </td>
            <td>
                <xsl:apply-templates select = "result"/>
            </td>
        </tr>
    </xsl:template>

    <xsl:template match = "signature"
                  mode = "single" >
        <xsl:param name = "internal" select = "/report/signatures/signature[ source ='internal']" />
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>File: </xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Файл: </xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "./file" />
            </td>
        </tr>
        <xsl:apply-templates select = "$internal/.[file = current()/file]"
                             mode = "quant"/>
        <xsl:apply-templates select = "."
                             mode = "quant" />
    </xsl:template>

   <xsl:template match = "signature"
                 mode = "quant" >
        <tr>
            <th colspan="2">
                <xsl:choose>
                    <xsl:when test = "source = 'internal'">
                        <xsl:choose>
                            <xsl:when test = "$locale">
                                <xsl:text>ELF-file attributes</xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>Аттрибуты ELF-файла</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                    <xsl:when test = "source = 'xattr'">
                        <xsl:choose>
                            <xsl:when test = "$locale">
                                <xsl:text>External</xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>Расширенные аттрибуты</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                </xsl:choose>
            </th>
        </tr>
        <xsl:apply-templates select = "version"/>
        <xsl:apply-templates select = "id"/>
        <xsl:apply-templates select = "hash"/>
        <xsl:apply-templates select = "sign"/>
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>State:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Состояние:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:apply-templates select = "result"/>
            </td>
        </tr>
    </xsl:template>

   <xsl:template match = "version" >
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Version:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Версия:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "." />
            </td>
        </tr>
    </xsl:template>

       <xsl:template match = "id" >
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Id:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Идентификатор:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "." />
            </td>
        </tr>
    </xsl:template>

   <xsl:template match = "hash" >
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Hash type:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Тип хэша:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "type" />
            </td>
        </tr>
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Hash:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Хэш:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:apply-templates select = "value"/>
            </td>
        </tr>
    </xsl:template>

       <xsl:template match = "sign" >
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Signature size:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Размер подписи:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "size" />
            </td>
        </tr>
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Signature:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Подпись:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:apply-templates select = "value"/>
            </td>
        </tr>
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Signer:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Подписант:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "signer" />
            </td>
        </tr>
        <tr>
            <th>
                <xsl:choose>
                    <xsl:when test = "$locale">
                        <xsl:text>Timestamp:</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>Метка времени:</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </th>
            <td>
                <xsl:value-of select = "timestamp" />
            </td>
        </tr>
    </xsl:template>

    <xsl:template match="part">
        <li><xsl:value-of select = "."/></li>
    </xsl:template>

    <xsl:template match = "result" >
        <xsl:choose>
            <xsl:when test = "type = 'good'">
                <font color="green"><xsl:value-of select = "value" /></font>
            </xsl:when>
            <xsl:otherwise>
                <font color="red"><xsl:value-of select = "value" /></font>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
