# -*- coding: utf-8 -*-

"""
***************************************************************************
    ogr2ogrtopostgislist.py
    ---------------------
    Date                 : November 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'November 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterString
from processing.core.parameters import ParameterCrs
from processing.core.parameters import ParameterSelection
from processing.core.parameters import ParameterBoolean
from processing.core.parameters import ParameterExtent
from processing.core.parameters import ParameterTableField

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils

from processing.tools.postgis import uri_from_name, GeoDB
from processing.tools.system import isWindows
from processing.tools.vector import ogrConnectionString, ogrLayerName


class Ogr2OgrToPostGisList(GdalAlgorithm):

    DATABASE = 'DATABASE'
    INPUT_LAYER = 'INPUT_LAYER'
    SHAPE_ENCODING = 'SHAPE_ENCODING'
    GTYPE = 'GTYPE'
    GEOMTYPE = ['', 'NONE', 'GEOMETRY', 'POINT', 'LINESTRING', 'POLYGON', 'GEOMETRYCOLLECTION', 'MULTIPOINT', 'MULTIPOLYGON', 'MULTILINESTRING']
    S_SRS = 'S_SRS'
    T_SRS = 'T_SRS'
    A_SRS = 'A_SRS'
    HOST = 'HOST'
    PORT = 'PORT'
    USER = 'USER'
    DBNAME = 'DBNAME'
    PASSWORD = 'PASSWORD'
    SCHEMA = 'SCHEMA'
    TABLE = 'TABLE'
    PK = 'PK'
    PRIMARY_KEY = 'PRIMARY_KEY'
    GEOCOLUMN = 'GEOCOLUMN'
    DIM = 'DIM'
    DIMLIST = ['2', '3']
    SIMPLIFY = 'SIMPLIFY'
    SEGMENTIZE = 'SEGMENTIZE'
    SPAT = 'SPAT'
    CLIP = 'CLIP'
    WHERE = 'WHERE'
    GT = 'GT'
    OVERWRITE = 'OVERWRITE'
    APPEND = 'APPEND'
    ADDFIELDS = 'ADDFIELDS'
    LAUNDER = 'LAUNDER'
    INDEX = 'INDEX'
    SKIPFAILURES = 'SKIPFAILURES'
    PRECISION = 'PRECISION'
    PROMOTETOMULTI = 'PROMOTETOMULTI'
    OPTIONS = 'OPTIONS'

    def __init__(self):
        GdalAlgorithm.__init__(self)
        self.processing = False

    def name(self):
        return 'importvectorintopostgisdatabaseavailableconnections'

    def displayName(self):
        return self.tr('Import Vector into PostGIS database (available connections)')

    def group(self):
        return self.tr('Vector miscellaneous')

    def defineCharacteristics(self):
        self.addParameter(ParameterString(
            self.DATABASE,
            self.tr('Database (connection name)'),
            metadata={
                'widget_wrapper': {
                    'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'}}))
        self.addParameter(ParameterVector(self.INPUT_LAYER,
                                          self.tr('Input layer')))
        self.addParameter(ParameterString(self.SHAPE_ENCODING,
                                          self.tr('Shape encoding'), "", optional=True))
        self.addParameter(ParameterSelection(self.GTYPE,
                                             self.tr('Output geometry type'), self.GEOMTYPE, 0))
        self.addParameter(ParameterCrs(self.A_SRS,
                                       self.tr('Assign an output CRS'), '', optional=False))
        self.addParameter(ParameterCrs(self.T_SRS,
                                       self.tr('Reproject to this CRS on output '), '', optional=True))
        self.addParameter(ParameterCrs(self.S_SRS,
                                       self.tr('Override source CRS'), '', optional=True))
        self.addParameter(ParameterString(
            self.SCHEMA,
            self.tr('Schema name'),
            'public',
            optional=True,
            metadata={
                'widget_wrapper': {
                    'class': 'processing.gui.wrappers_postgis.SchemaWidgetWrapper',
                    'connection_param': self.DATABASE}}))
        self.addParameter(ParameterString(
            self.TABLE,
            self.tr('Table name, leave blank to use input name'),
            '',
            optional=True,
            metadata={
                'widget_wrapper': {
                    'class': 'processing.gui.wrappers_postgis.TableWidgetWrapper',
                    'schema_param': self.SCHEMA}}))
        self.addParameter(ParameterString(self.PK,
                                          self.tr('Primary key (new field)'), 'id', optional=True))
        self.addParameter(ParameterTableField(self.PRIMARY_KEY,
                                              self.tr('Primary key (existing field, used if the above option is left empty)'), self.INPUT_LAYER, optional=True))
        self.addParameter(ParameterString(self.GEOCOLUMN,
                                          self.tr('Geometry column name'), 'geom', optional=True))
        self.addParameter(ParameterSelection(self.DIM,
                                             self.tr('Vector dimensions'), self.DIMLIST, 0))
        self.addParameter(ParameterString(self.SIMPLIFY,
                                          self.tr('Distance tolerance for simplification'),
                                          '', optional=True))
        self.addParameter(ParameterString(self.SEGMENTIZE,
                                          self.tr('Maximum distance between 2 nodes (densification)'),
                                          '', optional=True))
        self.addParameter(ParameterExtent(self.SPAT,
                                          self.tr('Select features by extent (defined in input layer CRS)')))
        self.addParameter(ParameterBoolean(self.CLIP,
                                           self.tr('Clip the input layer using the above (rectangle) extent'),
                                           False))
        self.addParameter(ParameterString(self.WHERE,
                                          self.tr('Select features using a SQL "WHERE" statement (Ex: column=\'value\')'),
                                          '', optional=True))
        self.addParameter(ParameterString(self.GT,
                                          self.tr('Group N features per transaction (Default: 20000)'),
                                          '', optional=True))
        self.addParameter(ParameterBoolean(self.OVERWRITE,
                                           self.tr('Overwrite existing table'), True))
        self.addParameter(ParameterBoolean(self.APPEND,
                                           self.tr('Append to existing table'), False))
        self.addParameter(ParameterBoolean(self.ADDFIELDS,
                                           self.tr('Append and add new fields to existing table'), False))
        self.addParameter(ParameterBoolean(self.LAUNDER,
                                           self.tr('Do not launder columns/table names'), False))
        self.addParameter(ParameterBoolean(self.INDEX,
                                           self.tr('Do not create spatial index'), False))
        self.addParameter(ParameterBoolean(self.SKIPFAILURES,
                                           self.tr('Continue after a failure, skipping the failed feature'),
                                           False))
        self.addParameter(ParameterBoolean(self.PROMOTETOMULTI,
                                           self.tr('Promote to Multipart'),
                                           True))
        self.addParameter(ParameterBoolean(self.PRECISION,
                                           self.tr('Keep width and precision of input attributes'),
                                           True))
        self.addParameter(ParameterString(self.OPTIONS,
                                          self.tr('Additional creation options'), '', optional=True))

    def processAlgorithm(self, feedback):
        self.processing = True
        GdalAlgorithm.processAlgorithm(self, feedback)
        self.processing = False

    def getConsoleCommands(self):
        connection = self.getParameterValue(self.DATABASE)
        uri = uri_from_name(connection)
        if self.processing:
            # to get credentials input when needed
            uri = GeoDB(uri=uri).uri

        inLayer = self.getParameterValue(self.INPUT_LAYER)
        ogrLayer = ogrConnectionString(inLayer)[1:-1]
        shapeEncoding = self.getParameterValue(self.SHAPE_ENCODING)
        ssrs = self.getParameterValue(self.S_SRS)
        tsrs = self.getParameterValue(self.T_SRS)
        asrs = self.getParameterValue(self.A_SRS)
        schema = self.getParameterValue(self.SCHEMA)
        table = self.getParameterValue(self.TABLE)
        pk = self.getParameterValue(self.PK)
        primary_key = self.getParameterValue(self.PRIMARY_KEY)
        geocolumn = self.getParameterValue(self.GEOCOLUMN)
        dim = self.DIMLIST[self.getParameterValue(self.DIM)]
        simplify = self.getParameterValue(self.SIMPLIFY)
        segmentize = self.getParameterValue(self.SEGMENTIZE)
        spat = self.getParameterValue(self.SPAT)
        clip = self.getParameterValue(self.CLIP)
        where = self.getParameterValue(self.WHERE)
        gt = self.getParameterValue(self.GT)
        overwrite = self.getParameterValue(self.OVERWRITE)
        append = self.getParameterValue(self.APPEND)
        addfields = self.getParameterValue(self.ADDFIELDS)
        launder = self.getParameterValue(self.LAUNDER)
        index = self.getParameterValue(self.INDEX)
        skipfailures = self.getParameterValue(self.SKIPFAILURES)
        promotetomulti = self.getParameterValue(self.PROMOTETOMULTI)
        precision = self.getParameterValue(self.PRECISION)
        options = self.getParameterValue(self.OPTIONS)

        arguments = []
        arguments.append('-progress')
        arguments.append('--config PG_USE_COPY YES')
        if shapeEncoding:
            arguments.append('--config')
            arguments.append('SHAPE_ENCODING')
            arguments.append('"' + shapeEncoding + '"')
        arguments.append('-f')
        arguments.append('PostgreSQL')
        arguments.append('PG:"')
        for token in uri.connectionInfo(self.processing).split(' '):
            arguments.append(token)
        arguments.append('active_schema={}'.format(schema or 'public'))
        arguments.append('"')
        arguments.append("-lco DIM=" + dim)
        arguments.append(ogrLayer)
        arguments.append(ogrLayerName(inLayer))
        if index:
            arguments.append("-lco SPATIAL_INDEX=OFF")
        if launder:
            arguments.append("-lco LAUNDER=NO")
        if append:
            arguments.append('-append')
        if addfields:
            arguments.append('-addfields')
        if overwrite:
            arguments.append('-overwrite')
        if len(self.GEOMTYPE[self.getParameterValue(self.GTYPE)]) > 0:
            arguments.append('-nlt')
            arguments.append(self.GEOMTYPE[self.getParameterValue(self.GTYPE)])
        if geocolumn:
            arguments.append("-lco GEOMETRY_NAME=" + geocolumn)
        if pk:
            arguments.append("-lco FID=" + pk)
        elif primary_key is not None:
            arguments.append("-lco FID=" + primary_key)
        if not table:
            table = ogrLayerName(inLayer).lower()
        if schema:
            table = '{}.{}'.format(schema, table)
        arguments.append('-nln')
        arguments.append(table)
        if ssrs:
            arguments.append('-s_srs')
            arguments.append(ssrs)
        if tsrs:
            arguments.append('-t_srs')
            arguments.append(tsrs)
        if asrs:
            arguments.append('-a_srs')
            arguments.append(asrs)
        if spat:
            regionCoords = spat.split(',')
            arguments.append('-spat')
            arguments.append(regionCoords[0])
            arguments.append(regionCoords[2])
            arguments.append(regionCoords[1])
            arguments.append(regionCoords[3])
            if clip:
                arguments.append('-clipsrc spat_extent')
        if skipfailures:
            arguments.append('-skipfailures')
        if where:
            arguments.append('-where "' + where + '"')
        if simplify:
            arguments.append('-simplify')
            arguments.append(simplify)
        if segmentize:
            arguments.append('-segmentize')
            arguments.append(segmentize)
        if gt:
            arguments.append('-gt')
            arguments.append(gt)
        if promotetomulti:
            arguments.append('-nlt PROMOTE_TO_MULTI')
        if precision is False:
            arguments.append('-lco PRECISION=NO')
        if options:
            arguments.append(options)

        commands = []
        if isWindows():
            commands = ['cmd.exe', '/C ', 'ogr2ogr.exe',
                        GdalUtils.escapeAndJoin(arguments)]
        else:
            commands = ['ogr2ogr', GdalUtils.escapeAndJoin(arguments)]

        return commands

    def commandName(self):
        return "ogr2ogr"
