from vayaAuto import __BASE__
import sys
import configparser
import time
import copy
import yaml
import threading
from yaml.loader import SafeLoader
import logging
from subprocess import Popen, PIPE
from vayaAuto.section import Section
import os
logger = logging.getLogger()

# EXPORT_PREFIX = 'saveFile_{export}'
# VIS_PREFIX = 'visShow'
# PIPE0_PREFIX = 'Pipe-0_{algo}-algo'


def osPath(func):
    def wrapper(*args, **kwargs):

        if os.name == 'nt':
            osArgs = []
            for i, arg in enumerate(args):
                if isinstance(arg, str):
                    osArg = os.sep.join(arg.split('/'))
                    osArgs.append(osArg)
                else:
                    osArgs.append(arg)
            func(*tuple(osArgs), **kwargs)
        else:
            func(*tuple(args), **kwargs)
    return wrapper


class VayaDrive(object):
    VD, VDCONSOLE = 0, 1

    @osPath
    def __init__(self, vaya_dir_path, console=False):
        self.temp_ini_file_path = os.path.join(__BASE__, 'temp.ini')
        # self.delete_temp_ini()
        self.vaya_dir_path = vaya_dir_path
        self.log_catcher_thread = None
        self.version = None
        self.is_paused = False
        self.compiled = False
        self.configuration = {}
        self.b_configuration = {}
        self.exe_path = None
        # self.set_exe_path(vaya_dir_path)
        self.default_config_folder = os.path.join(vaya_dir_path, 'DefaultConfigs')
        self.default_config_paths = {}
        self.parent_dir = os.path.abspath(os.path.join(vaya_dir_path, os.pardir))
        self._seq_output_folder = ''
        self._consoleMode = 0
        self.vayadrive_process = None
        if os.path.isdir(self.default_config_folder):
            self.gather_default_configs(self.default_config_folder)
        else:
            logger.info(f'not found default config folder in {self.default_config_folder}')
        self.consoleMode = str(console).lower()
        # if console:
        #     self.consoleMode = 'true'
        # else:
        #     self.consoleMode = 'false'

        self.set_vaya_config()
        self.generate_properties()

    def generate_properties(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(f'{here}/configurations/vayadrive_params.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
            for sec, options in data.items():
                for attr_name, option in options.items():
                    # setattr(VayaDrive, attr_name, None)
                    try:
                        if not hasattr(self, attr_name):
                            setattr(VayaDrive, attr_name, property(self.get_func(sec, option),
                                                                   self.set_func(sec, option)))
                    except KeyError as e:
                        logger.info(f'Unable to set attribute {attr_name}')

    # """
    # create GLOBAL TAB get and set functions
    # """
    def get_func(self, section, option):
        def getf(self):
            return self.configuration[section][option].value
        return getf

    def set_func(self, section, option):
        def setf(self, value):
            self.set_explicit_param(section=section, option=option, value=value)
        return setf
    # @property
    # def output_folder(self):
    #     return self.configuration['Global']['OutputLocation'].value
    #
    # @output_folder.setter
    # def output_folder(self, value):
    #     self.set_explicit_param(section='Global', option='OutputLocation', value=value)
    #
    # @property
    # def debugRenderVisuals(self):
    #     return self.configuration['Global']['DebugRenderVisuals'].value
    #
    # @debugRenderVisuals.setter
    # def debugRenderVisuals(self, value):
    #     self.set_explicit_param(section='Global', option='DebugRenderVisuals', value=value)
    #
    # @property
    # def exportDataToFiles(self):
    #     return self.configuration['Global']['ExportDataToFiles'].value
    #
    # @exportDataToFiles.setter
    # def exportDataToFiles(self, value):
    #     self.set_explicit_param(section='Global', option='ExportDataToFiles', value=value)
    #
    # @property
    # def runningMode(self):
    #     return self.configuration['Global']['RunningMode'].value
    #
    # @runningMode.setter
    # def runningMode(self, value):
    #     self.set_explicit_param(section='Global', option='RunningMode', value=value)
    #
    # @property
    # def runTo(self):
    #     return self.configuration['Global']['RunTo'].value
    #
    # @runTo.setter
    # def runTo(self, value):
    #     self.set_explicit_param(section='Global', option='RunTo', value=value)
    #
    # @property
    # def runFrom(self):
    #     return self.configuration['Global']['RunFrom'].value
    #
    # @runFrom.setter
    # def runFrom(self, value):
    #     self.set_explicit_param(section='Global', option='RunFrom', value=value)
    #
    # @property
    # def stopAfterLastFrame(self):
    #     return self.configuration['Global']['StopAfterLastFrame'].value
    #
    # @stopAfterLastFrame.setter
    # def stopAfterLastFrame(self, value):
    #     self.set_explicit_param(section='Global', option='StopAfterLastFrame', value=value)
    #
    # @property
    # def inputLocation(self):
    #     return self.configuration['Global']['InputLocation'].value
    #
    # @inputLocation.setter
    # def inputLocation(self, value):
    #     self.set_explicit_param(section='Global', option='InputLocation', value=value)
    #
    # """
    # create Reader-Sensor TAB get and set functions
    # """
    #
    # @property
    # def recordLocation(self):
    #     return self.configuration['Reader-Sensors']['RECORD_LOCATION_String'].value
    #
    # @recordLocation.setter
    # def recordLocation(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='RECORD_LOCATION_String', value=value)
    #
    # @property
    # def recordToDisk(self):
    #     return self.configuration['Reader-Sensors']['RECORD_TO_DISK_Bool'].value
    #
    # @recordToDisk.setter
    # def recordToDisk(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='RECORD_TO_DISK_Bool', value=value)
    #
    # @property
    # def createFrame(self):
    #     return self.configuration['Reader-Sensors']['CREATE_FRAMES_Bool'].value
    #
    # @createFrame.setter
    # def createFrame(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='CREATE_FRAMES_Bool', value=value)
    #
    # @property
    # def egomotionSpeedUpdate(self):
    #     return self.configuration['Reader-Sensors']['ENABLE_EGOMOTION_SPEED_UPDATES_Bool'].value
    #
    # @egomotionSpeedUpdate.setter
    # def egomotionSpeedUpdate(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='ENABLE_EGOMOTION_SPEED_UPDATES_Bool', value=value)
    #
    # @property
    # def obd2SpeedUpdates(self):
    #     return self.configuration['Reader-Sensors']['ENABLE_OBD2_SPEED_UPDATES_Bool'].value
    #
    # @obd2SpeedUpdates.setter
    # def obd2SpeedUpdates(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='ENABLE_OBD2_SPEED_UPDATES_Bool', value=value)
    #
    # @property
    # def calibrationFolder(self):
    #     return self.configuration['Reader-Sensors']['DEFAULT_CALIB_FOLDER_String'].value
    #
    # @calibrationFolder.setter
    # def calibrationFolder(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DEFAULT_CALIB_FOLDER_String', value=value)
    #
    # @property
    # def disable_camera0(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_0_Bool'].value
    #
    # @disable_camera0.setter
    # def disable_camera0(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_0_Bool', value=value)
    #
    # @property
    # def disable_camera1(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_1_Bool'].value
    #
    # @disable_camera1.setter
    # def disable_camera1(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_1_Bool', value=value)
    #
    # @property
    # def disable_camera2(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_2_Bool'].value
    #
    # @disable_camera2.setter
    # def disable_camera2(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_2_Bool', value=value)
    #
    # @property
    # def disable_camera3(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_3_Bool'].value
    #
    # @disable_camera3.setter
    # def disable_camera3(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_3_Bool', value=value)
    #
    # @property
    # def disable_camera4(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_4_Bool'].value
    #
    # @disable_camera4.setter
    # def disable_camera4(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_4_Bool', value=value)
    #
    # @property
    # def disable_camera5(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_5_Bool'].value
    #
    # @disable_camera5.setter
    # def disable_camera5(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_5_Bool', value=value)
    #
    # @property
    # def disable_camera6(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_6_Bool'].value
    #
    # @disable_camera6.setter
    # def disable_camera6(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_6_Bool', value=value)
    #
    # @property
    # def disable_camera7(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CAMERA_7_Bool'].value
    #
    # @disable_camera7.setter
    # def disable_camera7(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CAMERA_7_Bool', value=value)
    #
    # @property
    # def disable_canbus(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_CANBUS_Bool'].value
    #
    # @disable_canbus.setter
    # def disable_canbus(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_CANBUS_Bool', value=value)
    #
    # @property
    # def disable_gps(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_GPS_Bool'].value
    #
    # @disable_gps.setter
    # def disable_gps(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_GPS_Bool', value=value)
    #
    # @property
    # def disable_imu(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_IMU_Bool'].value
    #
    # @disable_imu.setter
    # def disable_imu(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_IMU_Bool', value=value)
    #
    # @property
    # def disable_lidar0(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_LIDAR_0_Bool'].value
    #
    # @disable_lidar0.setter
    # def disable_lidar0(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_LIDAR_0_Bool', value=value)
    #
    # @property
    # def disable_lidar1(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_LIDAR_1_Bool'].value
    #
    # @disable_lidar1.setter
    # def disable_lidar1(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_LIDAR_1_Bool', value=value)
    #
    # @property
    # def disable_radar0(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_0_Bool'].value
    #
    # @disable_radar0.setter
    # def disable_radar0(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_0_Bool', value=value)
    #
    # @property
    # def disable_radar1(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_1_Bool'].value
    #
    # @disable_radar1.setter
    # def disable_radar1(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_1_Bool', value=value)
    #
    # @property
    # def disable_radar2(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_2_Bool'].value
    #
    # @disable_radar2.setter
    # def disable_radar2(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_2_Bool', value=value)
    #
    # @property
    # def disable_radar3(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_3_Bool'].value
    #
    # @disable_radar3.setter
    # def disable_radar3(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_3_Bool', value=value)
    #
    #
    # @property
    # def disable_radar4(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_4_Bool'].value
    #
    # @disable_radar4.setter
    # def disable_radar4(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_4_Bool', value=value)
    #
    # @property
    # def disable_radar5(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_5_Bool'].value
    #
    # @disable_radar5.setter
    # def disable_radar5(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_5_Bool', value=value)
    #
    # @property
    # def disable_radar6(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_6_Bool'].value
    #
    # @disable_radar6.setter
    # def disable_radar6(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_6_Bool', value=value)
    #
    # @property
    # def disable_radar7(self):
    #     return self.configuration['Reader-Sensors']['DISABLE_SENSOR_ID_RADAR_7_Bool'].value
    #
    # @disable_radar7.setter
    # def disable_radar7(self, value):
    #     self.set_explicit_param(section='Reader-Sensors', option='DISABLE_SENSOR_ID_RADAR_7_Bool', value=value)
    #
    # """
    # create Pipe-0 TAB sensor enable get and set functions
    # """
    #
    # @property
    # def enableCanbus(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CANBUS_Bool'].value
    #
    # @enableCanbus.setter
    # def enableCanbus(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CANBUS_Bool', value=value)
    #
    # @property
    # def enableImu(self):
    #     return self.configuration['Pipe-0']['SensorEnable_IMU_Bool'].value
    #
    # @enableImu.setter
    # def enableImu(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_IMU_Bool', value=value)
    #
    # @property
    # def enableGps(self):
    #     return self.configuration['Pipe-0']['SensorEnable_GPS_Bool'].value
    #
    # @enableGps.setter
    # def enableGps(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_GPS_Bool', value=value)
    #
    # @property
    # def enableLidar0(self):
    #     return self.configuration['Pipe-0']['SensorEnable_LIDAR_0_Bool'].value
    #
    # @enableLidar0.setter
    # def enableLidar0(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_LIDAR_0_Bool', value=value)
    #
    # @property
    # def enableLidar1(self):
    #     return self.configuration['Pipe-0']['SensorEnable_LIDAR_1_Bool'].value
    #
    # @enableLidar1.setter
    # def enableLidar1(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_LIDAR_1_Bool', value=value)
    #
    # @property
    # def enableCamera0(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CAMERA_0_Bool'].value
    #
    # @enableCamera0.setter
    # def enableCamera0(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CAMERA_0_Bool', value=value)
    #
    # @property
    # def enableCamera1(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CAMERA_1_Bool'].value
    #
    # @enableCamera1.setter
    # def enableCamera1(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CAMERA_1_Bool', value=value)
    #
    # @property
    # def enableCamera2(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CAMERA_2_Bool'].value
    #
    # @enableCamera2.setter
    # def enableCamera2(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CAMERA_2_Bool', value=value)
    #
    # @property
    # def enableCamera3(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CAMERA_3_Bool'].value
    #
    # @enableCamera3.setter
    # def enableCamera3(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CAMERA_3_Bool', value=value)
    #
    # @property
    # def enableCamera4(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CAMERA_3_Bool'].value
    #
    # @enableCamera4.setter
    # def enableCamera4(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CAMERA_4_Bool', value=value)
    #
    # @property
    # def enableCamera5(self):
    #     return self.configuration['Pipe-0']['SensorEnable_CAMERA_5_Bool'].value
    #
    # @enableCamera5.setter
    # def enableCamera5(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_CAMERA_5_Bool', value=value)
    #
    # @property
    # def enableRadar0(self):
    #     return self.configuration['Pipe-0']['SensorEnable_RADAR_0_Bool'].value
    #
    # @enableRadar0.setter
    # def enableRadar0(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_RADAR_0_Bool', value=value)
    #
    # @property
    # def enableRadar1(self):
    #     return self.configuration['Pipe-0']['SensorEnable_RADAR_1_Bool'].value
    #
    # @enableRadar1.setter
    # def enableRadar1(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_RADAR_1_Bool', value=value)
    #
    # @property
    # def enableRadar2(self):
    #     return self.configuration['Pipe-0']['SensorEnable_RADAR_2_Bool'].value
    #
    # @enableRadar2.setter
    # def enableRadar2(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_RADAR_2_Bool', value=value)
    #
    # @property
    # def enableRadar3(self):
    #     return self.configuration['Pipe-0']['SensorEnable_RADAR_3_Bool'].value
    #
    # @enableRadar3.setter
    # def enableRadar3(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_RADAR_3_Bool', value=value)
    #
    # @property
    # def enableRadar4(self):
    #     return self.configuration['Pipe-0']['SensorEnable_RADAR_4_Bool'].value
    #
    # @enableRadar4.setter
    # def enableRadar4(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SensorEnable_RADAR_4_Bool', value=value)
    #
    # """ Pipe-0 algos """
    #
    # @property
    # def egoMotionVX(self):
    #     return self.configuration['Pipe-0']['EGO_MOTION_VX_Bool'].value
    #
    # @egoMotionVX.setter
    # def egoMotionVX(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='EGO_MOTION_VX_Bool', value=value)
    #
    # @property
    # def egoMotionCanbus(self):
    #     return self.configuration['Pipe-0']['EGO_MOTION_CANBUS_Bool'].value
    #
    # @egoMotionCanbus.setter
    # def egoMotionCanbus(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='EGO_MOTION_CANBUS_Bool', value=value)
    #
    # @property
    # def geoLocalozation(self):
    #     return self.configuration['Pipe-0']['GEO_LOCALIZATION_Bool'].value
    #
    # @geoLocalozation.setter
    # def geoLocalozation(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='GEO_LOCALIZATION_Bool', value=value)
    #
    # @property
    # def upSampleV4(self):
    #     return self.configuration['Pipe-0']['UP_SAMPLE_V4_Bool'].value
    #
    # @upSampleV4.setter
    # def upSampleV4(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='UP_SAMPLE_V4_Bool', value=value)
    #
    #
    # @property
    # def terrainModel(self):
    #     return self.configuration['Pipe-0']['TERRAIN_MODEL_Bool'].value
    #
    # @terrainModel.setter
    # def terrainModel(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='TERRAIN_MODEL_Bool', value=value)
    #
    # @property
    # def obstacleDetectorV3(self):
    #     return self.configuration['Pipe-0']['OBSTACLE_DETECTORV3_Bool'].value
    #
    # @obstacleDetectorV3.setter
    # def obstacleDetectorV3(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='OBSTACLE_DETECTORV3_Bool', value=value)
    #
    # @property
    # def framingSensor(self):
    #     return self.configuration['Pipe-0']['FRAMING_SENSOR_Enum'].value
    #
    # @framingSensor.setter
    # def framingSensor(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='FRAMING_SENSOR_Enum', value=value)
    #
    #
    #
    # @property
    # def obstacleTrackerGlobal(self):
    #     return self.configuration['Pipe-0']['OBJECT_TRACKER_GLOBAL_Bool'].value
    #
    # @obstacleTrackerGlobal.setter
    # def obstacleTrackerGlobal(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='OBJECT_TRACKER_GLOBAL_Bool', value=value)
    #
    # @property
    # def displayManager(self):
    #     return self.configuration['Pipe-0']['DISPLAY_MANAGER_Bool'].value
    #
    # @displayManager.setter
    # def displayManager(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='DISPLAY_MANAGER_Bool', value=value)
    #
    # @property
    # def groundSurfaceV2(self):
    #     return self.configuration['Pipe-0']['GROUND_SURFACE_V2_Bool'].value
    #
    # @groundSurfaceV2.setter
    # def groundSurfaceV2(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='GROUND_SURFACE_V2_Bool', value=value)
    #
    # @property
    # def lrcf360(self):
    #     return self.configuration['Pipe-0']['LRCF360_Bool'].value
    #
    # @lrcf360.setter
    # def lrcf360(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='LRCF360_Bool', value=value)
    #
    # @property
    # def egoMotionMM(self):
    #     return self.configuration['Pipe-0']['EGO_MOTION_MM_Bool'].value
    #
    # @egoMotionMM.setter
    # def egoMotionMM(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='EGO_MOTION_MM_Bool', value=value)
    #
    # @property
    # def semanticNet(self):
    #     return self.configuration['Pipe-0']['SEMANTIC_NET_Bool'].value
    #
    # @semanticNet.setter
    # def semanticNet(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='SEMANTIC_NET_Bool', value=value)
    #
    # @property
    # def lanePerception(self):
    #     return self.configuration['Pipe-0']['LANE_PERCEPTION_Bool'].value
    #
    # @lanePerception.setter
    # def lanePerception(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='LANE_PERCEPTION_Bool', value=value)
    #
    # @property
    # def imagePreproc(self):
    #     return self.configuration['Pipe-0']['IMAGE_PREPROC_Bool'].value
    #
    # @imagePreproc.setter
    # def imagePreproc(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='IMAGE_PREPROC_Bool', value=value)
    #
    # @property
    # def radarPreproc(self):
    #     return self.configuration['Pipe-0']['RADAR_PREPROC_Bool'].value
    #
    # @radarPreproc.setter
    # def radarPreproc(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='RADAR_PREPROC_Bool', value=value)
    #
    # @property
    # def lidarPreproc(self):
    #     return self.configuration['Pipe-0']['LIDAR_PREPROC_Bool'].value
    #
    # @lidarPreproc.setter
    # def lidarPreproc(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='LIDAR_PREPROC_Bool', value=value)
    #
    # @property
    # def envModelGeneratorV2(self):
    #     return self.configuration['Pipe-0']['ENV_MODEL_GENERATOR_V2_Bool'].value
    #
    # @envModelGeneratorV2.setter
    # def envModelGeneratorV2(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='ENV_MODEL_GENERATOR_V2_Bool', value=value)
    #
    # @property
    # def bevProjection(self):
    #     return self.configuration['Pipe-0']['BEV_PROJECTION_Bool'].value
    #
    # @bevProjection.setter
    # def bevProjection(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='BEV_PROJECTION_Bool', value=value)
    #
    # @property
    # def bevProjectionDepthNet(self):
    #     return self.configuration['Pipe-0']['BEV_PROJECTION_DEPTHNET_Bool'].value
    #
    # @bevProjectionDepthNet.setter
    # def bevProjectionDepthNet(self, value):
    #     self.set_explicit_param(section='Pipe-0', option='BEV_PROJECTION_DEPTHNET_Bool', value=value)

    @property
    def seq_output_folder(self):
        return self._seq_output_folder

    @seq_output_folder.setter
    def seq_output_folder(self, value):
        self._seq_output_folder = value

    @property
    def consoleMode(self):
        return self._consoleMode

    @consoleMode.setter
    def consoleMode(self, value):

        if str(value).lower() == 'true':
            self._consoleMode = self.VDCONSOLE
        else:
            self._consoleMode = self.VD
        logger.info(f'vayadrive console mode = {self._consoleMode}')
        self.set_exe_path(self.vaya_dir_path)

    # @osPath
    def record_mode(self, calib_folder, output_folder):
        self.runningMode = '7'
        self.createFrames = 'false'
        self.recordToDisk = 'true'
        self.defaultCalibFolderString = calib_folder
        self.recordLocationString = output_folder

    # @osPath
    def live_mode(self, calib_folder, output_folder):
        self.runningMode = '7'
        self.createFrames = 'true'
        self.recordToDisk = 'false'
        self.defaultCalibFolderString = calib_folder
        self.recordLocationString = output_folder

    def playback_mode(self):
        self.runningMode = '5'

    def gather_default_configs(self, default_config):

        for file in os.listdir(default_config):
            file_path = os.path.join(default_config, file)
            if os.path.isdir(file_path):
                self.gather_default_configs(file_path)
            elif file.endswith(r'.ini'):
                self.default_config_paths[os.path.splitext(file)[0]] = file_path

    def set_explicit_param(self, **kwargs):
        sec = kwargs.pop('section')
        option = kwargs.pop('option')
        value = kwargs.pop('value')
        if sec not in self.configuration.keys():
            section = Section(sec)
            self.configuration[sec] = section
        if option not in self.configuration[sec].keys():
            self.configuration[sec].add_option(option)
        self.configuration[sec][option].value = str(value)

    # @osPath
    def find_vd_exe_path(self, path, posix):
        for (root, dirs, files) in os.walk(path, topdown=True):
            if self.consoleMode and f"VayaDriveConsole{posix}" in files:
                return root
            elif not self.consoleMode and f'VayaDrive{posix}' in files:
                return root
        else:
            logger.error('not found EXE path')
            raise VayaException(f'couldn\'t find VayaDrive exe file')

    # @osPath
    def set_exe_path(self, path):
        if os.name == 'nt':
            posix = '.exe'
            build_folder = 'build_vs2019'
        else:
            posix = ''
            build_folder = 'build_Release'
        if os.path.isdir(os.path.join(path, 'Release')):
            path = os.path.join(path, 'Release')
        elif os.path.isdir(os.path.join(path, build_folder)):
            path = os.path.join(path, build_folder, 'Release')
        else:
            path = self.find_vd_exe_path(path, posix)
            self.compiled = True
        if self.consoleMode:
            self.exe_path = os.path.join(path, f'VayaDriveConsole{posix}')
        else:
            self.exe_path = os.path.join(path, f"VayaDrive{posix}")
        logger.info(f'found exe - {self.exe_path}')
        logger.info(f'compiled version = {self.compiled}')

    def set_vaya_config(self):
        if self.configuration:
            self.configuration = {}
        # self.delete_temp_ini()
        self.run_vayadrive(nogui=True, export_full_ini=True)
        config = configparser.ConfigParser()
        config.optionxform = str
        with open(self.temp_ini_file_path, "r") as f:
            lines = f.readlines()
            if len(lines) == 0:
                raise VayaException(f'Unable to dump full config using -d \n'
                                    f'-----PROCESS OUTPUT-----\n'
                                    f'{self.vayadrive_process.stderr.readlines()}')
        with open(self.temp_ini_file_path, "w") as f:
            for line in lines:
                if any([word in line for word in ['DefaultValue','Units', ' ', '%']]):
                    continue
                else:
                    f.write(line)

        config.read(self.temp_ini_file_path)
        for sec in config.sections():

            section = Section(sec)
            for option in config[sec]:
                section.add_option(option)
                try:
                    section[option].value = config.get(sec, option)
                except Exception as e:
                    raise VayaException(f'Get an exception \n{e}')
                self.configuration[sec] = section

        self.b_configuration = copy.deepcopy(self.configuration)

    @osPath
    def set_configuration_with_ini(self, ini_path, reset=False):
        if reset:
            self.reset()
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(ini_path)
        for sec in config.sections():
            for option in config[sec]:
                if sec not in self.configuration.keys():
                    section = Section(sec)
                    self.configuration[sec] = section
                if option not in self.configuration[sec].keys():
                    self.configuration[sec].add_option(option)
                self.configuration[sec][option].value = config.get(sec, option)


    def export_ini_file(self):

        config = configparser.ConfigParser()
        config.optionxform = str
        for name, sec in self.configuration.items():
            config[name] = {}
            for option_name, option in sec:
                if option.value is None:
                    continue
                # print(f'insert value to ini file\nsection: {sec}\noption: {option} value: {str(option.value)}\n-------------------')
                config[name][option_name] = str(option.value)
        # self.ini_path = os.path.join(self.vaya_dir_path, 'override.ini')
        with open(self.temp_ini_file_path, 'w') as configfile:
            config.write(configfile)

    def run_vayadrive(self, nogui=False, autostart=False, get_process=False, export_full_ini=False, force_run=False,
                      qt=False, preset=False, o_params=[], non_blocking_mode=False):
        self.seq_output_folder = ''
        self.export_ini_file()
        call_list = [self.exe_path]
        if nogui:
            call_list.append('-nogui')
        if autostart:
            call_list.append('-autostart')
        if preset:
            call_list.append(f'-p{self.temp_ini_file_path}')
        else:
            call_list.append(f'-c{self.temp_ini_file_path}')
        if o_params:
            call_list += o_params
        if export_full_ini:
            call_list.append(f'-d')
        env = dict(os.environ)
        if not self.compiled:
            if os.name == 'posix':  # LINUX
                dependencies = self.extract_dependencies_linux()
                dependencies = dependencies
                try:
                    ld_library_path = env['LD_LIBRARY_PATH']
                    env['LD_LIBRARY_PATH'] = dependencies + ld_library_path
                except:
                    env['LD_LIBRARY_PATH'] = dependencies
            elif os.name == 'nt':  # WINDOWS
                dependencies = self.extract_dependencies_windows()
                win_path = env['PATH']
                env['PATH'] = dependencies + win_path
        if qt:
            return {'call_list': call_list, 'env': env, 'cwd': self.vaya_dir_path}
        else:
            # logger.info(f'Popen - { {"call_list": call_list, "env": env, "cwd": self.vaya_dir_path}}')
            self.vayadrive_process = Popen(call_list, cwd=self.vaya_dir_path, env=env, stderr=PIPE)

        if get_process:
            return self.vayadrive_process
        if export_full_ini:
            time.sleep(1)
            self.vayadrive_process.kill()
        if non_blocking_mode:
            self.log_catcher_thread = threading.Thread(target=self.catch_log, args=(export_full_ini, force_run))
            self.log_catcher_thread.start()
        else:
            self.catch_log(export_full_ini, force_run)


    def catch_log(self, export_full_ini, force_run):
        while self.vayadrive_process.poll() is None:
            output = self.vayadrive_process.stderr.readline().decode("utf-8")
            sys.stdout.write(output)
            if 'ERROR' in output and not force_run:
                self.vayadrive_process.kill()
                if not export_full_ini:
                    raise VayaException(f'Found error in VD log\n{output}')
                # raise VayaException(f'Found error in VD log\n{output}')
            if 'Output folder created:' in output:
                self.seq_output_folder = output.split()[-1]
            if 'Pause: 1' in output:
                self.is_paused = True
            elif 'Pause: 0' in output:
                self.is_paused = False
            if not self.version and 'Version' in output:
                self.version = output.split('Version: ')[-1][:-1]

    def enabled_cameras(self):
        for name, option in self.configuration['Pipe-0'].items():
            if 'SensorEnable_CAMERA' in name and option.value == 'true':
                yield option.name.split('_')[2]

    def enabled_radars(self):
        for name, option in self.configuration['Pipe-0'].items():
            if 'SensorEnable_Radar' in name and option.value == 'true':
                yield option.name.split('_')[2]

    def enabled_lidars(self):
        for name, option in self.configuration['Pipe-0'].items():
            if 'SensorEnable_LIDAR' in name and option.value == 'true':
                yield option.name.split('_')[2]

    def delete_temp_ini(self):
        if os.path.isfile(self.temp_ini_file_path):
            os.remove(self.temp_ini_file_path)

    def extract_dependencies_linux(self):
        run_sh = os.path.join(self.vaya_dir_path, 'cmake_vv_scripts', 'cmake_run_release.sh')
        depends = ''
        with open(run_sh, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'EXPORT' in line and line.index('EXPORT') == 0:
                    depends += line.split('=')[1][:-1] + ':'
        depends += f'../Libs/PCL/PCL-1.8.1/lib/ubuntu1804:'
        # logger.info(f'set dependencies to env {depends}')
        return depends + f'../Libs/PCL/PCL-1.8.1/lib/ubuntu1804:'

    def extract_dependencies_windows(self):
        run_bat = os.path.join(self.vaya_dir_path, 'cmake_run_vs2019.bat')
        with open(run_bat, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'PATH' in line:
                    return line[9:-7]
        return False

    def reset(self):
        self.configuration = copy.deepcopy(self.b_configuration)

    def find_version(self, timeout: int = 2):
        """
        :param timeout: how much time to wait for vd version to be extracted from log (seconds)
        :return: version string if found, 0 otherwise
        """
        self.run_vayadrive(non_blocking_mode=True)
        timeout_target = time.time() + timeout*60  # 2 seconds
        while True:
            if time.time() > timeout_target or self.version:
                break

        self.vayadrive_process.kill()
        if not self.version:
            print('SW version details were not found!')
            return 0
        return self.version


class VayaException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = 'VayaException has been raised'
