#!/usr/bin/env python3

# load functions
from deid.dicom import get_files, replace_identifiers, get_identifiers
from deid.config import DeidRecipe
from deid.utils import get_installdir
from deid.data import get_dataset
from deid.logger import bot
import pydicom as dicom
import numpy as np
import math
import os
import json


# set variables (global, template)
work_dir = "{work_dir}"
dicom_files = "{dicom_files}".split("\n")
dicom_recipe = "{dicom_recipe}"
dicom_base_recipe = "{dicom_base_recipe}"
dicom_recipe_data = "{dicom_recipe_data}"
output_folder = "{output_folder}"
verbose = "{verbose}"

# In case the script is running alone
if verbose == "{verbose}" or verbose == "TRUE":
  verbose = True
else:
  verbose = False

def mdebug(*s):
  if verbose:
    print(*s)

if not os.path.exists(work_dir):
  try:
    work_dir = os.path.dirname(__file__)
  except Exception as e:
    work_dir = "."
  # os.chdir(path=work_dir)

if output_folder == "{output_folder}":
  output_folder = os.path.join(work_dir, "deid-dicom")

if not os.path.exists(output_folder):
  os.makedirs(output_folder, mode=0o777, exist_ok=True)
output_folder = os.path.abspath(output_folder)

if len(dicom_files) == 1 and dicom_files[0] == '{dicom_files}':
  dicom_files = list(get_files(os.path.join(work_dir, "dicom")))
elif len(dicom_files) == 1:
  tmp = os.path.join(work_dir, dicom_files[0])
  if os.path.exists(tmp) and os.path.isdir(tmp):
    dicom_files = list(get_files(tmp))

dicom_files = [os.path.abspath(x) for x in dicom_files]
mdebug("Total %d files found!" % len(dicom_files))

dicom_base_exists = True
if not os.path.exists(dicom_base_recipe):
  dicom_base_recipe = os.path.join(work_dir, dicom_base_recipe)
  if not os.path.exists(dicom_base_recipe):
    dicom_base_recipe = os.path.join(work_dir, "dicom.deid")
    if not os.path.exists(dicom_base_recipe):
      dicom_base_recipe = 'dicom'
      dicom_base_exists = False
if dicom_base_exists:
  mdebug("Base recipe found: %s" % dicom_base_recipe)
else:
  mdebug("Base recipe not found. Use default dicom recipe")

if not os.path.exists(dicom_recipe):
  dicom_recipe = os.path.join(work_dir, dicom_recipe)
  if not os.path.exists(dicom_recipe):
    dicom_recipe = os.path.join(work_dir, "deid_recipe.txt")
    if not os.path.exists(dicom_recipe):
      dicom_recipe = None

if dicom_recipe is None:
  mdebug("Custom recipe not found, use default")
else:
  mdebug("Custom recipe found: %s" % dicom_recipe)

if not os.path.exists(dicom_recipe_data):
  dicom_recipe_data = os.path.join(work_dir, dicom_recipe_data)
  if not os.path.exists(dicom_recipe_data):
    dicom_recipe_data = os.path.join(work_dir, "deid_recipe_data.txt")
    if not os.path.exists(dicom_recipe_data):
      dicom_recipe_data = None

# Load data replace settings
default_data = {}
if dicom_recipe_data is not None:
  mdebug("Loading recipe data from: %s" % dicom_recipe_data)
  with open(dicom_recipe_data, "r") as f:
    default_data = json.load(f)

# mask information
mt = float(default_data.get("mask_top", 0))
mb = float(default_data.get("mask_bottom", 0.05))
ml = float(default_data.get("mask_left", 0))
mr = float(default_data.get("mask_right", 0.3))

# Load identifiers
# This is the function to get identifiers
old_level = bot.level
bot.level = -3
ids = get_identifiers(dicom_files=dicom_files, remove_private=False)
bot.level = old_level

# add default values
for item in ids:
  for k, v in default_data.items():
    ids[item][k] = v

# **
# Here you might save them in your special (IRB approvied) places
# And then provide replacement anonymous ids to put back in the data
# A cookie tumor example is below
# **

################################################################################
# The Deid Recipe
#
# The process of flagging images comes down to writing a set of filters to
# check if each image meets some criteria of interest. For example, I might
# create a filter called "xray" that is triggered when the Modality is CT or XR.
# We specify these fliters in a simple text file called a "deid recipe." When
# you work with the functions, you have the choice to instantiate the object
# in advance, or just provide a path to a recipe file. We will walk through
# examples  for both below, starting with working with a DeidRecipe object.
# If you aren't interested in this use case or just want to use a provided
# deid recipe file, continue to the step to replace_identifiers
#
##################################

# Create a DeidRecipe
recipe = DeidRecipe(deid=dicom_recipe, base=dicom_base_exists, default_base=dicom_base_recipe)
mdebug("Recipe format: %s" % recipe.get_format())

mdebug("Filter lists:")
for list_type in recipe.ls_filters():
  mdebug("  %s: %d items" % (list_type, len(recipe.get_filters(list_type))))
# To get a complete dict of all filters, key (index) is by filter group
# recipe.get_filters()

# To get the group names
# recipe.ls_filters()
# ['whitelist', 'blacklist']

# To get a list of specific filters under a group
# recipe.get_filters("blacklist")


################################################################################
# Header Actions
# A header action is a step (e.g., replace, remove, blank) to be applied to
# a dicom image header. The headers are also part of the deid recipe, and you
# don't need to necessarily use header actions and filters at the same time.
################################################################################

# We can get a complete list of actions
# recipe.get_actions()

# We can filter to an action type
mdebug("Actions:\n  Items to add/alter: %d" % len(recipe.get_actions(action="ADD")))
mdebug("  Items to remove: %d" %len(recipe.get_actions(action="REMOVE")))


# [{'action': 'ADD',
#  'field': 'IssuerOfPatientID',
#  'value': 'STARR. In an effort to remove PHI all dates are offset from their original values.'},
# {'action': 'ADD',
#  'field': 'PatientBirthDate',
#  'value': 'var:entity_timestamp'},
# {'action': 'ADD', 'field': 'StudyDate', 'value': 'var:item_timestamp'},
# {'action': 'ADD', 'field': 'PatientID', 'value': 'var:entity_id'},
# {'action': 'ADD', 'field': 'AccessionNumber', 'value': 'var:item_id'},
# {'action': 'ADD', 'field': 'PatientIdentityRemoved', 'value': 'Yes'}]

# or we can filter to a field
# recipe.get_actions(field="PatientID")

# [{'action': 'REMOVE', 'field': 'PatientID'},
# {'action': 'ADD', 'field': 'PatientID', 'value': 'var:entity_id'}]

# and logically, both
# recipe.get_actions(field="PatientID", action="REMOVE")
#  [{'action': 'REMOVE', 'field': 'PatientID'}]


################################################################################
# Replacing Identifiers
#
# The %header section of a deid recipe defines a set of actions and associated
# fields to perform them on. As we saw in the examples above, we could easily
# view and filter the actions based on the header field or action type.
#
# For this next section, we will pretend that we've just extracted ids from
# our data files (in a dictionary called ids) and we will prepare a second
# dictionary of updated fields.

##################################

# And then use the deid recipe and updated to create new files
cleaned_files = replace_identifiers(
    dicom_files=dicom_files, deid=recipe, ids=ids,
    output_folder=output_folder, save = True
)

def mask_dcm(image_path, mask_top = [0, 0.05], mask_left = [0, 0.3], save_snapshot=True):
  ds = dicom.dcmread(image_path)
  # Checking transfer syntax
  # Credit https://github.com/pydicom/pydicom/issues/73
  if ds.file_meta.TransferSyntaxUID.is_compressed:
    print("File `%s` was stored as `%s`, uncompress to edit..." % (image_path, ds.file_meta.TransferSyntaxUID.name))
    ds.decompress()
    #ds.PhotometricInterpretation = "RGB"
    #aa = dicom.pixel_data_handlers.util.convert_color_space(arr, "YBR_FULL_422", "RGB")
  # or [ds.NumberOfFrames, ds.Rows, ds.Columns, ds.SamplesPerPixel]
  sp = ds.pixel_array.shape
  color_chan = ds.SamplesPerPixel
  # edit margin 2 and 3
  xi, yi = (1, 2)
  if len(sp) <= 3:
    # edit margin 1,2
    xi, yi = (0, 1)
  # calculate xy
  x0 = math.floor(mask_top[0] * sp[xi])
  x0 = x0 if x0 >= 0 else 0
  x1 = math.ceil(mask_top[1] * sp[xi])
  x1 = x1 if x1 < sp[xi] else sp[xi]
  y0 = math.floor(mask_left[0] * sp[yi])
  y0 = y0 if y0 >= 0 else 0
  y1 = math.ceil(mask_left[1] * sp[yi])
  y1 = y1 if y1 < sp[yi] else sp[yi]
  # edit pixel_array
  arr = ds.pixel_array
  # Convert color space if not RGB (most likely to be YBR_FULL_422)
  if ds.PhotometricInterpretation != "RGB":
    print("File `%s`: converting color space from %s to RGB..." % (image_path, ds.PhotometricInterpretation))
    arr = dicom.pixel_data_handlers.util.convert_color_space(arr, ds.PhotometricInterpretation, "RGB")
    ds.PhotometricInterpretation = "RGB"
  sample = None
  if len(sp) == 2:
    arr[x0:x1,y0:y1] = 0
    sample = arr
  elif len(sp) == 3:
    arr[x0:x1,y0:y1,:] = 0
    if color_chan == 3:
      sample = arr
    else:
      sample = arr[:,:,1]
  elif len(sp) == 4:
    arr[:,x0:x1,y0:y1,:] = 0
    if color_chan == 3:
      sample = arr[1,:,:,:]
    else:
      sample = arr[1,:,:,1]
  else:
    raise Exception("DICOM image `%s` has abnormal dimensions: %d" % (image_path, len(sp)))
  ds.PixelData = arr.tobytes()
  # ds.PixelData.is_undefined_length = False
  ds.save_as(image_path)
  if save_snapshot:
    import matplotlib.pyplot as plt 
    fig = plt.figure(figsize=(10,10))
    plt.imshow(sample)
    fig.savefig("%s.png" % image_path, bbox_inches='tight', dpi=150)
    plt.close(fig)



for f in cleaned_files:
  # Example: Saved to /Users/dipterix/Dropbox/projects/dcmanony/dev/deid-dicom/AG_example with CW.dcm
  # Mask the images
  mask_dcm(f, mask_top = [mt, mb], mask_left = [ml, mr])
  # save a 
  if verbose:
    print("Saved to %s" % f)

mdebug("Done with the meta info")

# # We can load in a cleaned file to see what was done
# from pydicom import read_file
# 
# test_file = read_file('test.dcm')


# test_file
# (0008, 0018) SOP Instance UID                    UI: cookiemonster-image-1
# (0010, 0020) Patient ID                          LO: 'cookiemonster'
# (0012, 0062) Patient Identity Removed            CS: 'Yes'
# (0028, 0002) Samples per Pixel                   US: 3
# (0028, 0010) Rows                                US: 1536
# (0028, 0011) Columns                             US: 2048
# (7fe0, 0010) Pixel Data                          OB: Array of 738444 bytes
