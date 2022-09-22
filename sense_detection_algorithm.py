# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SenseRemoteDetection
                                 A QGIS plugin
 AI detection algorithms for remote sensing images.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-09-21
        copyright            : (C) 2022 by atlas@SenseTime
        email                : xuxiang@sensetime.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'atlas@SenseTime'
__date__ = '2022-09-21'
__copyright__ = '(C) 2022 by atlas@SenseTime'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import re
import os
import inspect
import subprocess
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QSettings
from qgis.core import (QgsSettings,
                       QgsProcessingAlgorithm,
                       QgsMessageLog,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorDestination)

def store_sdk_info(sdk_dir, sdk_model):
  s = QgsSettings()
  s.setValue("st/sdk_dir", sdk_dir)
  s.setValue("st/sdk_model",  sdk_model)

def read_sdk_info():
  s = QgsSettings()
  sdk_dir = s.value("st/sdk_dir", "")
  sdk_model  = s.value("st/sdk_model", "")
  return sdk_dir, sdk_model

class SenseRemoteDetectionAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'

    SDK_DIR = 'SDK_DIR'

    MODEL_FILE = 'MODEL_FILE'

    DEVICE = 'DEVICE'
    # DEVICE_OPTIONS = ['trt', 'cuda', 'cpu']
    DEVICE_OPTIONS = ['gpu', 'cpu']

    RESAMPLE = 'RESAMPLE'

    BANDS = 'BANDS'

    LOGNAME = 'SenseTime'

    UI_INPUT = 'Input Imagery'
    UI_SDK_LOCATION = 'SDK Location'
    UI_MODEL = 'Model'
    UI_DEVICE = 'Device'
    UI_RESAMPLE = 'Resample Resolution'
    UI_OUTPUT = 'Output'
    UI_ALG_NAME = 'image segmentation'
    UI_ALG_GROUP = 'AI Algorithms'

    UI_ERROR_OUTPUT_FORMAT = 'file format of output file error, please set shapefile output. If you are using temp file output, please modify the value of Setting->Options->Processing->General->Default output vector layer extension to shp'
    TRANS = {
        UI_INPUT: {
            'en': UI_INPUT,
            'zh': '输入文件'
        },
        UI_SDK_LOCATION: {
            'en': UI_SDK_LOCATION,
            'zh': 'SDK 目录'
        },
        UI_MODEL: {
            'en': UI_MODEL,
            'zh': '模型'
        },
        UI_DEVICE: {
            'en': UI_DEVICE,
            'zh': '设备'
        },
        UI_RESAMPLE: {
            'en': UI_RESAMPLE,
            'zh': '重采样分辨率'
        },
        UI_OUTPUT: {
            'en': UI_OUTPUT,
            'zh': '输出文件'
        },
        UI_ERROR_OUTPUT_FORMAT: {
            'en': UI_ERROR_OUTPUT_FORMAT,
            'zh': '输出文件的格式错误，请设置为shapefile格式输出。如果是临时文件，请修改设置->选项->常规->默认输出矢量图层扩展名的值为shp'
        },
        UI_ALG_NAME: {
            'en': UI_ALG_NAME,
            'zh': '大模型分割'
        },
        UI_ALG_GROUP: {
            'en': UI_ALG_GROUP,
            'zh': 'AI 算法'
        }
    }

    def initAlgorithm(self, config):
        self.locale = QSettings().value('locale/userLocale')[0:2]

        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr(self.UI_INPUT)
            )
        )

        sdk_dir, sdk_model = read_sdk_info()
        self.addParameter(
            QgsProcessingParameterFile(
                self.SDK_DIR,
                self.tr(self.UI_SDK_LOCATION),
                QgsProcessingParameterFile.Folder,
                '',
                sdk_dir
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.MODEL_FILE,
                self.tr(self.UI_MODEL),
                QgsProcessingParameterFile.File,
                '',
                sdk_model
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.DEVICE,
                self.tr(self.UI_DEVICE),
                self.DEVICE_OPTIONS,
                False,
                0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.RESAMPLE,
                self.tr(self.UI_RESAMPLE),
                 QgsProcessingParameterNumber.Double,
                 None,
                 True
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr(self.UI_OUTPUT)
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        source = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        sourceFile = source.dataProvider().dataSourceUri()
        QgsMessageLog.logMessage('source name = {}'.format(sourceFile), self.LOGNAME)

        sdk_dir = self.parameterAsFile(parameters, self.SDK_DIR, context)
        QgsMessageLog.logMessage('sdk dir = {}'.format(sdk_dir), self.LOGNAME)

        model_file = self.parameterAsFile(parameters, self.MODEL_FILE, context)
        QgsMessageLog.logMessage('model file = {}'.format(model_file), self.LOGNAME)

        device = self.DEVICE_OPTIONS[self.parameterAsEnum(parameters, self.DEVICE, context)]
        QgsMessageLog.logMessage('device = {}'.format(device), self.LOGNAME)

        sinkFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        QgsMessageLog.logMessage('output layer = {}'.format(sinkFile), self.LOGNAME)
        
        #sdk_dir = os.path.split(os.path.realpath(__file__))[0]
        QgsMessageLog.logMessage('sdk directory = {}'.format(sdk_dir), self.LOGNAME)

        store_sdk_info(sdk_dir, model_file)
        sdk_exe = os.path.join(sdk_dir, 'sl.seg.predict.exe')

        # force save shpfile
        filename, file_extension = os.path.splitext(sinkFile)
        if file_extension != '.shp':
            feedback.reportError(self.tr(self.UI_ERROR_OUTPUT_FORMAT))
            return {self.OUTPUT: sinkFile}
            
        cmd = [sdk_exe, 
            "-m", model_file,
            "-i", sourceFile,
            "-o", sinkFile, 
            "--device", device,
            "-a", "10.10.41.103:8181",
            "-v", "debug"
        ]

        my_env = os.environ.copy()
        my_env["PATH"] = sdk_dir + ":" + my_env["PATH"]
        my_env["PROJ_LIB"] = sdk_dir

        proc = subprocess.Popen(cmd, shell=True,
          stdout=(subprocess.PIPE),
          stderr=(subprocess.PIPE),
          env=my_env
          )
        
        try:
            while proc.poll() is None:
                if feedback.isCanceled():
                    proc.kill()
                    break
                if proc.stdout.readable():
                    output = proc.stdout.readline()
                    if output is not None and output != "" and output.decode('utf-8') is not None and output.decode('utf-8') != "":
                        msg = output.decode('utf-8')
                        feedback.pushInfo("{}".format(msg))
                        ret = re.search(r"\d*%", msg)
                        if ret:
                            feedback.setProgress(int(ret.group().strip('%')))
        except Exception as e:
            QgsMessageLog.logMessage('exception = {}'.format(e), self.LOGNAME)
        return {self.OUTPUT: sinkFile}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'image segmentation'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'AI Algorithms'

    def tr(self, string):
        return self.TRANS[string][self.locale] 

    def createInstance(self):
        return SenseRemoteDetectionAlgorithm()

    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'logo.png')))
        return icon