# A short script to de-identify DICOM images using `pydicom` and `deid` package

## System requirement

* python (>= 3.6)
* matplotlib
* pydicom
* numpy
* deid

## Installation guide

> If you have R (>= 3.6) installed, skip to Section "Run the app from R"

**For Windows users**, please:

1. Download and install `python3` first, **make sure** python is [added to your PATH environment](https://datatofish.com/add-python-to-windows-path/)
2. Once python 3 is installed, use [`pip` to install](https://pip.pypa.io/en/stable/installing/) the other four libraries

```
python.exe -m pip install matplotlib pydicom numpy deid
```

**For Linux/OSX users**, py3 is natively installed, run these in terminals:

```
python3 -m pip install matplotlib pydicom numpy deid
```

If failed, either create a virtual environment or install these packages by adding `--user` option:

```
python3 -m pip install --user matplotlib pydicom numpy deid
```

> Notice: `deid` package depends on an old version of `pydicom` library (1.3.0). The version is too old to convert colorspace from `YBR_FULL_422` to `RGB`. Please use the following command to check `pydicom` version. If the version is too low, update it.

The code to check `pydicom` version: (Please go to terminal/cmd.exe, enter `python`, hit return button to enter python mode, then run the following code)

```
import pydicom
# Check if it's less than 1.4.2, if yes, need to upgrade
pydicom.__version__
exit()
```

Code to update `pydicom`: in the terminal environment, type:

```
python3 -m pip install -U pydicom
```

If you use `--user` in the previous steps, add to the command before `-U` option: `python3 -m pip install --user -U pydicom`.

Ignore the error message.

## Run the app directly using `Python`

1. Check [here](https://github.com/dipterix/deid-dicom/archive/refs/tags/v0.3.zip) for zipped apps, or [here](https://github.com/dipterix/deid-dicom/releases/tag/v0.3) if the previous link does not work. Download, extract to some directory (say desktop). 

2. Copy-paste your DICOM images to `dicom/` folder (under `deid-dicom-0.3/app/`)

3. Remove folder `deid-dicom/` if there the folder exists (IMPORTANT)

3. Edit `deid_recipe_data.txt`:
  * `mask_*`: the percentage of images to be masked out. Sometimes the DICOM pixel data has patient information. You might want to mask these pixels out. By default, the mask will be 0.05% in height and 0.3% in width. This means if your image size is `500 x 600`, then the top area of size `25 x 180` will be masked out
  * `patient_id`: current patient ID

4. Run `dicom-deid.py`. For Linux/OSX users, you should be able to double-click (or right-click and open) the script. In case the script is not executable, or your operating system is Windows, open terminal, `cd` all the way to the app directory, type:

```
python ./dicom-deid.py
```

(`python` might be `python3` or `python.exe`, depends on where your python path is)

5. You should be able to see folder `deid-dicom/` created. The de-identified images will be in this folder. There will be `png` files that display the snapshots (usually useful to adjust masks)


## Run the app from R

If you have [`R` installed](https://cran.r-project.org/), the following commands will

* Download python and install dependencies
* Download the script app to your desktop
* De-identify the images

1. One-time set up: (only run once and no need to run in the future)

```r
# Install packages 
install.packages("remotes")
remotes::install_github("ravepy")

# Configure miniconda environment
ravepy::configure(packages = c('matplotlib', 'pydicom', 'numpy', 'deid'))
```

2. Download the latest version (v0.3 as of 2021-06-16)

```r
app_dir <- "~/Desktop/DICOM-app"
url <- "https://github.com/dipterix/deid-dicom/archive/refs/tags/v0.3.zip"

# Download the script to Desktop
tmpfile <- tempfile(fileext = ".zip")
utils::download.file(url, destfile = tmpfile)
unzip(tmpfile, exdir = app_dir)
```

3. Please go to your `desktop > DICOM-app > deid-dicom-0.3`, copy-paste the DICOM images to be de-identified to `dicom/` folder. 

4. Go back to `R`, run the following commands. To make sure correct python is loaded, **restart R session first**. Run the following commands

```r
work_dir <- "~/Desktop/DICOM-app/deid-dicom-0.3/app"

output_dir <- file.path(work_dir, "deid-dicom")
if(dir.exists(output_dir)){ unlink(output_dir, recursive = TRUE) }
ravepy:::run_script('dicom-deid.py', work_dir = work_dir)
```




