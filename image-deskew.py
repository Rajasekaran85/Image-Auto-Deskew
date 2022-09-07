import sys
import os
import numpy as np
from skimage import io
from skimage.transform import rotate
from PIL import Image
from deskew import determine_skew
from skimage import util
import re
import glob
import tifffile as tiff

print("\n Image Auto-Deskew - TIFF & JPEG Format \n")
print("\n Date: 07 September 2022 \n\n")

'''
- Getting the Input file path from user
- Tool will apply the deskew and output placed in the "De-Skew_output" folder
'''

filepath = input("Enter the Input Image file path: ")
output_directory = "De-Skew_output"
output = filepath + "/" + output_directory + "/"

if os.path.exists(output):
    pass
else:
    os.mkdir(output)


#Applying the de-skew in the JPEG files

for fname in glob.glob(filepath + "/" + "*.jpg"):
	input_image = fname
	filename = os.path.basename(fname)
	print(filename)
	image1 = Image.open(input_image)
	img_dpi = str(image1.info['dpi'])
	patn = re.sub(r"[\(\)]", "", img_dpi)
	sp = patn.split(",")[0]
	dpi_val = round(float(sp))
	image1.close()
	image = io.imread(input_image)
	skew = determine_skew(image)
	rotated = rotate(image, skew, resize=True) * 255
	io.imsave(output + filename, rotated.astype(np.uint8), dpi=(dpi_val,dpi_val), quality=90)


#Applying the de-skew in the TIFF files

for tif_fname in glob.glob(filepath + "/" + "*.tif"):
	tif_input_image = tif_fname
	tif_filename = os.path.basename(tif_fname)
	print(tif_filename)

	image2 = Image.open(tif_input_image)
	tif_img_dpi = str(image2.info['dpi'])
	patn2 = re.sub(r"[\(\)]", "", tif_img_dpi)
	sp2 = patn2.split(",")[0]
	tif_dpi_val = round(float(sp2))
	comp_img = str(image2.info['compression'])
	mode_img = str(image2.mode)
	image2.close()

	# Group4 compression images will not apply the deskew, just write the error message on the text file
	if comp_img == "group4":
		error_file = filepath + "/" + "error.log"
		f = open(error_file, "a+")
		f.write(tif_filename + " : Image is Group 4 Compression\n")
		f.close()

	# For Black & White images
	elif mode_img == "1":
		tif_image = tiff.imread(tif_input_image)
		tif_skew = determine_skew(tif_image)
		tif_rotated = rotate(tif_image, tif_skew, resize=True) * 255
		inverted_img = util.invert(tif_rotated) # skew function inverted the output image, so used the invert() method
		io.imsave(output + "test-" + tif_filename, inverted_img.astype(np.uint8))
		image3 = Image.open(output + "test-" + tif_filename)
		bw_conv = image3.convert('1')       # converting into black and white
		bw_conv.save(output + tif_filename, dpi=(tif_dpi_val,tif_dpi_val)) # for retaining the original dpi value
		image3.close()
		os.remove(output + "test-" + tif_filename)

	# For Color / Grayscale images
	else:
		tif_image = tiff.imread(tif_input_image)
		tif_skew = determine_skew(tif_image)
		tif_rotated = rotate(tif_image, tif_skew, resize=True) * 255
		io.imsave(output + "test-" + tif_filename, tif_rotated.astype(np.uint8))
		image3 = Image.open(output + "test-" + tif_filename)
		image3.save(output + tif_filename, dpi=(tif_dpi_val,tif_dpi_val))
		image3.close()
		os.remove(output + "test-" + tif_filename)

print("Process Completed")
