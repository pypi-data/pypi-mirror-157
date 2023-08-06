from kivy.factory import Factory

from audio import Audio
from audiorecorder import  AudioRecorder
from camerawithmic import CameraWithMic
from custom_camera import CustomCamera, QrReader
from kivycamera import KivyCamera
from micphone import Micphone
from qrcodereader import QRCodeReader
from version import __version__
r = Factory.register
r('Audio', Audio)
r('AudioRecorder', AudioRecorder)
r('CameraWithMic', CameraWithMic)
r('CustomCamera', CustomCamera)
r('QrReader', QrReader)
r('KivyCamera', KivyCamera)
r('Micphone', Micphone)
r('QRCodeReader', QRCodeReader)
