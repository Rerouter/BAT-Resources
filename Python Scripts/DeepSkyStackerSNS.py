# Written by Ryan Favelle

import subprocess
import os
import shutil
from tkinter import Tk, filedialog

root = Tk()  # pointing root to Tk() to use it as Tk() in program.
root.withdraw()  # Hides small tkinter window.
root.attributes('-topmost', True)  # Opened windows will be active. above all windows despite of selection.
open_file = filedialog.askdirectory()  # Returns opened path as str

Directory = open_file
LightImages = []
BiasImages = []
DarkImages = []
FlatsImages = []
DarkFlatsImages = []
PixelScale = 0
Goal_Post = 2.5
SupportedFileFormats = ("crw", "cr2", "cr3", "nef", "raf", "dng", "kdc", "dcr", "fits")

if os.path.isfile((Directory + "/info.txt")):
    f = open(Directory + "/info.txt", "r")
    for line in f:
        if "Arcsec / Pixel:" in line:
            if len(line.split(":", 1)) == 2:
                PixelScale = float(line.split(':', 1)[1])

    PixelSize = 0
    FocalLength = 0
    if PixelScale == 0:
        for line in f:
            if "Pixel Size:" in line:
                PixelSize = float(line.split(':', 1)[1])
            if "Focal Length:" in line:
                FocalLength = float(line.split(':', 1)[1])
            if "Barlow Magnification:" in line:
                BarlowMag = float(line.split(':', 1)[1])
            else:
                BarlowMag = 1.0
            if PixelSize and FocalLength:
                PixelScale = 206256 * PixelSize / FocalLength / BarlowMag

if os.path.isdir(Directory + "/Lights"):
    for filename in os.listdir(Directory + "/Lights"):
        if filename.lower().endswith(SupportedFileFormats):
            LightImages.append(filename)
if os.path.isdir(Directory + "/Bias"):
    for filename in os.listdir(Directory + "/Bias"):
        if filename.lower().endswith(SupportedFileFormats):
            BiasImages.append(filename)
if os.path.isdir(Directory + "/Darks"):
    for filename in os.listdir(Directory + "/Darks"):
        if filename.lower().endswith(SupportedFileFormats):
            DarkImages.append(filename)
if os.path.isdir(Directory + "/Flats"):
    for filename in os.listdir(Directory + "/Flats"):
        if filename.lower().endswith(SupportedFileFormats):
            FlatsImages.append(filename)
if os.path.isdir(Directory + "/DarkFlats"):
    for filename in os.listdir(Directory + "/DarkFlats"):
        if filename.lower().endswith(SupportedFileFormats):
            DarkFlatsImages.append(filename)

# Generate Registration Template
Template_top = """DSS file list
CHECKED	TYPE	FILE"""
Template_bottom = """#WS#Software\\DeepSkyStacker\\FitsDDP|BayerPattern=4
#WS#Software\\DeepSkyStacker\\FitsDDP|BlueScale=1.0000
#WS#Software\\DeepSkyStacker\\FitsDDP|Brighness=1.0000
#WS#Software\\DeepSkyStacker\\FitsDDP|DSLR=
#WS#Software\\DeepSkyStacker\\FitsDDP|FITSisRAW=0
#WS#Software\\DeepSkyStacker\\FitsDDP|ForceUnsigned=0
#WS#Software\\DeepSkyStacker\\FitsDDP|Interpolation=Bilinear
#WS#Software\\DeepSkyStacker\\FitsDDP|RedScale=1.0000
#WS#Software\\DeepSkyStacker\\RawDDP|AHD=0
#WS#Software\\DeepSkyStacker\\RawDDP|BlackPointTo0=1
#WS#Software\\DeepSkyStacker\\RawDDP|BlueScale=1.0000
#WS#Software\\DeepSkyStacker\\RawDDP|Brighness=1.0000
#WS#Software\\DeepSkyStacker\\RawDDP|CameraWB=1
#WS#Software\\DeepSkyStacker\\RawDDP|Interpolation=Bilinear
#WS#Software\\DeepSkyStacker\\RawDDP|NoWB=0
#WS#Software\\DeepSkyStacker\\RawDDP|RawBayer=0
#WS#Software\\DeepSkyStacker\\RawDDP|RedScale=1.0000
#WS#Software\\DeepSkyStacker\\RawDDP|SuperPixels=0
#WS#Software\\DeepSkyStacker\\Register|ApplyMedianFilter=1
#WS#Software\\DeepSkyStacker\\Register|DetectHotPixels=1
#WS#Software\\DeepSkyStacker\\Register|DetectionThreshold=4
#WS#Software\\DeepSkyStacker\\Register|PercentStack=80
#WS#Software\\DeepSkyStacker\\Register|StackAfter=0
#WS#Software\\DeepSkyStacker\\Stacking|AlignChannels=0
#WS#Software\\DeepSkyStacker\\Stacking|AlignmentTransformation=0
#WS#Software\\DeepSkyStacker\\Stacking|ApplyFilterToCometImages=1
#WS#Software\\DeepSkyStacker\\Stacking|BackgroundCalibration=0
#WS#Software\\DeepSkyStacker\\Stacking|BackgroundCalibrationInterpolation=1
#WS#Software\\DeepSkyStacker\\Stacking|BadLinesDetection=0
#WS#Software\\DeepSkyStacker\\Stacking|CometStackingMode=0
#WS#Software\\DeepSkyStacker\\Stacking|CreateIntermediates=0
#WS#Software\\DeepSkyStacker\\Stacking|DarkFactor=1.0000
#WS#Software\\DeepSkyStacker\\Stacking|DarkOptimization=0
#WS#Software\\DeepSkyStacker\\Stacking|Dark_Iteration=5
#WS#Software\\DeepSkyStacker\\Stacking|Dark_Kappa=2.0000
#WS#Software\\DeepSkyStacker\\Stacking|Dark_Method=7
#WS#Software\\DeepSkyStacker\\Stacking|Debloom=0
#WS#Software\\DeepSkyStacker\\Stacking|Flat_Iteration=5
#WS#Software\\DeepSkyStacker\\Stacking|Flat_Kappa=2.0000
#WS#Software\\DeepSkyStacker\\Stacking|Flat_Method=7
#WS#Software\\DeepSkyStacker\\Stacking|HotPixelsDetection=1
#WS#Software\\DeepSkyStacker\\Stacking|IntermediateFileFormat=1
#WS#Software\\DeepSkyStacker\\Stacking|Light_Iteration=5
#WS#Software\\DeepSkyStacker\\Stacking|Light_Kappa=2.0000
#WS#Software\\DeepSkyStacker\\Stacking|Light_Method=4
#WS#Software\\DeepSkyStacker\\Stacking|LockCorners=1
#WS#Software\\DeepSkyStacker\\Stacking|Mosaic=1
#WS#Software\\DeepSkyStacker\\Stacking|Offset_Iteration=5
#WS#Software\\DeepSkyStacker\\Stacking|Offset_Kappa=2.0000
#WS#Software\\DeepSkyStacker\\Stacking|Offset_Method=7
#WS#Software\\DeepSkyStacker\\Stacking|PCS_ColdDetection=500
#WS#Software\\DeepSkyStacker\\Stacking|PCS_ColdFilter=1
#WS#Software\\DeepSkyStacker\\Stacking|PCS_DetectCleanCold=0
#WS#Software\\DeepSkyStacker\\Stacking|PCS_DetectCleanHot=0
#WS#Software\\DeepSkyStacker\\Stacking|PCS_HotDetection=500
#WS#Software\\DeepSkyStacker\\Stacking|PCS_HotFilter=1
#WS#Software\\DeepSkyStacker\\Stacking|PCS_ReplaceMethod=1
#WS#Software\\DeepSkyStacker\\Stacking|PCS_SaveDeltaImage=0
#WS#Software\\DeepSkyStacker\\Stacking|PerChannelBackgroundCalibration=1
#WS#Software\\DeepSkyStacker\\Stacking|PixelSizeMultiplier=1
#WS#Software\\DeepSkyStacker\\Stacking|RGBBackgroundCalibrationMethod=2
#WS#Software\\DeepSkyStacker\\Stacking|SaveCalibrated=0
#WS#Software\\DeepSkyStacker\\Stacking|SaveCalibratedDebayered=0
#WS#Software\\DeepSkyStacker\\Stacking|SaveCometImages=0
#WS#Software\\DeepSkyStacker\\Stacking|UseDarkFactor=0
"""

f = open(Directory + "/SNSRegisterFilelist.txt", "w+")
f.write(Template_top + "\n")
for file in LightImages:
    f.write("""1	light	.\\Lights\\""" + file + "\n")
for file in DarkImages:
    f.write("""1	dark	.\\Darks\\""" + file + "\n")
for file in FlatsImages:
    f.write("""1	flat	.\\Flats\\""" + file + "\n")
for file in DarkFlatsImages:
    f.write("""1	darkflat	.\\DarkFlats\\""" + file + "\n")
for file in BiasImages:
    f.write("""1	offset	.\\Bias\\""" + file + "\n")
f.write(Template_bottom)
f.close()

# Call Deep Sky Stacker to generate file info
file_list_loc = str(os.path.join(Directory.replace('/', '\\') + os.sep, 'SNSRegisterFilelist.txt'))
subprocess.call('"C:\\Program Files\\DeepSkyStacker (64 bit)\\DeepSkyStackerCL.exe"' + ' /r "' + file_list_loc + '"')

FilelistResults = []
# Get Image Scores
print("Get Image Scores")
if os.path.isdir(Directory + "/Lights"):
    for filename in os.listdir(Directory + "/Lights"):
        if filename.lower().endswith('.info.txt'):
            mean_radius_value = []
            f = open(Directory + "/Lights/" + filename, "r")
            for line in f:
                if "MeanRadius" in line:
                    mean_radius_value.append(float(line.split('= ', 1)[1]))

            FWHM_Pixels = round(sum(mean_radius_value) / len(mean_radius_value) * 1.5555 * PixelScale, 2)
            if FWHM_Pixels <= Goal_Post:
                print("Including: " + filename + " FWHM: " + str(FWHM_Pixels))
                FilelistResults.append(filename.split('.Info.txt')[0])
            else:
                print("Rejecting: " + filename + " FWHM: " + str(FWHM_Pixels) + " > " + str(Goal_Post))
StackingLights = []
for image in LightImages:
    for file in FilelistResults:
        if image[0:len(FilelistResults[0])] == file:
            StackingLights.append(image)

# Generate Stacking Template

f = open(Directory + "/SNSStackingFilelist.txt", "w+")
f.write(Template_top + "\n")
for file in StackingLights:
    f.write("""1	light	.\\Lights\\""" + file + "\n")
for file in DarkImages:
    f.write("""1	dark	.\\Darks\\""" + file + "\n")
for file in FlatsImages:
    f.write("""1	flat	.\\Flats\\""" + file + "\n")
for file in DarkFlatsImages:
    f.write("""1	darkflat	.\\DarkFlats\\""" + file + "\n")
for file in BiasImages:
    f.write("""1	offset	.\\Bias\\""" + file + "\n")
f.write(Template_bottom)
f.close()

# Call Deep Sky Stacker to Stack Images
file_list_loc = str(os.path.join(Directory.replace('/', '\\') + os.sep, 'SNSStackingFilelist.txt'))
tile_save_loc = str(os.path.join(Directory.replace('/', '\\') + os.sep, 'SNSDSSTile.tif'))
subprocess.call('"C:\\Program Files\\DeepSkyStacker (64 bit)\\DeepSkyStackerCL.exe"' + ' /S "' + file_list_loc + '"')
if os.path.isfile(str(os.path.join(Directory.replace('/', '\\') + os.sep, 'Lights\\Autosave.tif'))):
    shutil.move(str(os.path.join(Directory.replace('/', '\\') + os.sep, 'Lights\\Autosave.tif')), tile_save_loc)
if os.path.isfile(str(os.path.join(Directory.replace('/', '\\') + os.sep, 'Lights\\SNSStackingFilelist.tif'))):
    shutil.move(str(os.path.join(Directory.replace('/', '\\') + os.sep, 'Lights\\SNSStackingFilelist.tif')), tile_save_loc)
