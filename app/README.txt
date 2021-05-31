This is a project to de-identify DICOM images

# ------------------------------- System Requirements ---------------------------------
+ Python 3.x
+ deid
+ numpy
+ pydicom
+ matplotlib

See "Installation" section to install the dependencies

# ------------------------------------ Usage ---------------------------------------------
*. Extract dcmanony.zip, enter dcmanony folder
*. Create a folder called "dicom"
*. If folder deid-dicom/ exists, remove it
*. Copy your dicom image to dicom/ folder
*. Open "deid_recipe_data.txt", edit patient_id (e.g. "YAB"), make sure it's quoted, save the file.

On Windows/linux/osx:
*. Open terminal (cmd.exe on windows, you can find it in start menu)
*. cd to the dcmanony directory, enter:
	python ./dicom-deid.py

Alternative method on linux/osx
*. Double-click on `dicom-deid.py`

*. The de-identified DICOM images will be in the deid-dicom/ folder

# ------------------------------------ Installation ------------------------------------
*. If you don't have python 3, please install it (google it). Always install python first.
*. Check python version, use terminal (cmd.exe on windows, or terminal apps in osx and linux)
> python -V
> pip -V

*. You should see version number with "3.x.x". If not, please change "python" to "python3", and "pip" to "pip3" and try again
*. If you use python3 and pip3, please change all the "pip" and "python" in the following commands accordingly

*. To install deid, use the following command
> pip install deid numpy pydicom matplotlib

*. On osx/linux, you might encounter permission denied error. If this is the case, try:
> pip install --user deid numpy pydicom matplotlib
