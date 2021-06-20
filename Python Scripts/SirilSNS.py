#  Written by Ryan Favelle
#  python -m pip install git+https://gitlab.com/free-astro/pysiril/uploads/3f945f98ac4d92cd1e1a6fa2717ccf56/pysiril-0.0.9-py3-none-any.whl
#  Siril needs to be in the default installation location,

import sys
import os

from pysiril.siril import *
from pysiril.wrapper import *
from tkinter import Tk, filedialog

root = Tk()  # pointing root to Tk() to use it as Tk() in program.
root.withdraw()  # Hides small tkinter window.
root.attributes('-topmost', True)  # Opened windows will be active. above all windows despite of selection.
open_file = filedialog.askdirectory()  # Returns opened path as str

Directory = open_file
PixelScale = 0
Goal_Post = 2.5

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

Scaled_Goal_Post = Goal_Post/PixelScale

# ==============================================================================
# EXAMPLE OSC_Processing with functions wrapper
# ==============================================================================

# 1. defining command blocks for creating masters and processing lights
def master_bias(bias_dir, process_dir):
    cmd.cd(bias_dir)
    cmd.convert('bias', out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.stack('bias', type='rej', sigma_low=3, sigma_high=3, norm='no')


def master_flat(flat_dir, process_dir):
    cmd.cd(flat_dir)
    cmd.convert('flat', out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.preprocess('flat', bias='bias_stacked')
    cmd.stack('pp_flat', type='rej', sigma_low=3, sigma_high=3, norm='mul')


def master_dark(dark_dir, process_dir):
    cmd.cd(dark_dir)
    cmd.convert('dark', out=process_dir, fitseq=True)
    cmd.cd(process_dir)
    cmd.stack('dark', type='rej', sigma_low=3, sigma_high=3, norm='no')


def light(light_dir, process_dir, hasflats=True, hasdarks=True, hasbias=True):
    cmd.cd(light_dir)
    cmd.convert('light', out=process_dir, fitseq=True )
    cmd.cd(process_dir)
    if hasflats and hasdarks and hasbias:
        cmd.preprocess('light', dark='dark', flat='flat', bias='bias', cfa=True, equalize_cfa=True, debayer=True )
    if hasflats and hasdarks and not hasbias:
        cmd.preprocess('light', dark='dark', flat='flat', cfa=True, equalize_cfa=True, debayer=True )
    if hasflats and not hasdarks and hasbias:
        cmd.preprocess('light', flat='flat', bias='bias', cfa=True, debayer=True)
    if hasflats and not hasdarks and not hasbias:
        cmd.preprocess('light', flat='flat', cfa=True, debayer=True)
    if hasdarks and not hasflats and hasbias:
        cmd.preprocess('light', dark='dark', bias='bias', cfa=True, debayer=True)
    if hasdarks and not hasflats and not hasbias:
        cmd.preprocess('light', dark='dark', cfa=True, debayer=True)
    if not hasflats and not hasdarks and not hasbias:
        cmd.preprocess('light', cfa=True, debayer=True)
    cmd.register('pp_light')
    cmd.stack('r_pp_light', type='rej', sigma_low=3, sigma_high=3, norm='addscale', filter_fwhm=Scaled_Goal_Post, output_norm=True, out='../SNSSirilTile')
    cmd.close()


# ==============================================================================
#  2. Starting pySiril
app = Siril()
workdir = Directory

try:
    cmd = Wrapper(app)  # 2. its wrapper
    app.Open()  # 2. ...and finally Siril

    #  3. Set preferences
    process_dir = '../sirilprocess'
    cmd.set16bits()
    cmd.setext('fit')

    #  4. Prepare master frames
    flatsdir = workdir + '/flats'
    hasflats = 0
    if (os.path.isdir(flatsdir)) and (len(os.listdir(flatsdir)) != 0):
        master_flat(workdir + '/flats', process_dir)
        hasflats = 1

    hasdarks = 0
    darksdir = workdir + '/darks'
    if (os.path.isdir(darksdir)) and (len(os.listdir(darksdir)) != 0):
        master_dark(workdir + '/darks', process_dir)
        hasdarks = 1

    hasbias = 0
    biasdir = workdir + '/bias'
    if (os.path.isdir(biasdir)) and (len(os.listdir(biasdir)) != 0):
        master_bias(workdir + '/bias', process_dir)
        hasbias = 1

    #  5. Calibrate the light frames, register and stack them
    light(workdir + '/lights', process_dir, hasflats, hasdarks, hasbias)

except Exception as e:
    print("\n**** ERROR *** " + str(e) + "\n")

# 6. Closing Siril and deleting Siril instance
app.Close()
del app
