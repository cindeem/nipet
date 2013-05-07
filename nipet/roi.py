import numpy as np
import nibabel as ni
from scipy.ndimage import affine_transform
from os.path import splitext

"""
Note that np masked arrays use True to indicate that a value is masked.
This is converted to the more intuitive False to indicate that a value is masked,
but the former is used internally, so be careful 
when accessing the mask element of masked arrays
"""
def split_archive_ext(filename, archive_exts = ['.gz']):
    name, ext = splitext(filename)
    if ext in archive_exts:
        name, ext2 = splitext(name)
        ext = ext + ext2
    return name, ext

def rois_over_time(input_files, mask_file, output_file, output_type):
    return process_input(input_files, mask_file, output_file, output_type)

def values_over_time(input_files, mask_file):
    return process_input(input_files, mask_file, None, 'values')

def stats_over_time(input_files, mask_file, output_file, output_type):
    return process_input(input_files, mask_file, None, 'stats')

def process_input(input_files, mask_file, output_file, output_type):
    """
    Takes in 4d data in either a list or a 4d data block,
    and outputs:
        frames_files - multiple frames of data with mask applied
            written to output file
        4d_file - 4d data block with mask applied
            written to output file
        frames - frames of data as an np array
        4d - 4d block of data as an np array
        values - values of the ROIs over time
        stats - the mean and std over time
    ""
    """
    if output_type == 'frames' or output_type == '4d':
        f = frame_data

    elif output_type == 'frames_files' or output_type == '4d_file':
        f = frame_data
    elif output_type == 'values':
        f = frame_values
    elif output_type == 'stats':
        f = frame_stats 
    else:
        raise Exception('Output should be "frames", "4d", "values", or "stats"')

    if isinstance(input_files, str):
        img = ni.load(input_files)
        data = img.get_data()
        affine = img.get_affine()
        frame_num = data.shape[0]
        output = np.zeros(frame_num)
        for k, frame in enumerate(data):
            output[k] = np.array(f(infile, mask_file, 0))
            
    elif isinstance(input_files, list):
        output = []
        affines = []
        for k, infile in enumerate(input_files):
            img = ni.load(infile)
            affines.append(img.get_affine())
            output.append(np.array(f(infile, mask_file, 0)))
        # are all affines the same?
        affine = affines[0]
        output = np.array(output)

    else:
        raise Exception('Input should be the name of a 4d .nii file, or a list of 3d .nii files')
        
    if output_type == 'frames_files':
        name, ext = split_archive_ext(output_file)
        outfiles = []
        for k, frame in enumerate(output):
            outfile = name + '_frame_%04d'%k + ext
            outfiles.append(outfile)
            new_img = ni.Nifti1Image(data=frame, affine=affine) 
            ni.save(new_img, outfile)
        return outfiles
    elif output_type == '4d_file':
        name, ext = split_archive_ext(filename)
        new_img = ni.Nifti1Image(data=output, affine=affine) 
        ni.save(new_img, output_file)
        return output_file
    elif output_type == 'frames' or output_type == '4d' or output_type == 'values':
        return output, affine

    elif output_type == 'stats':
        return output
    else:
        raise Exception('Output should be "frames", "4d", "values", or "stats"')
            
   
def frame_data(frame_file, mask_file, fill_value=0):
    img = ni.load(frame_file)
    data = img.get_data()
    mask = reslice_mask(frame_file, mask_file)
    return apply_mask(data, mask, fill_value = fill_value)

def frame_values(frame_file, mask_file, fill_value=0):
    """
    applies mask to frame,
    returns vector of relevant data points
    """
    img = ni.load(frame_file) 
    data = img.get_data()
    mask = reslice_mask(frame_file, mask_file)
    return extract_values(data, mask, fill_value = fill_value)
    
def frame_stats(frame_file, mask_file, fill_value = 0):
    """
    applies mask to frame,
    returns mean and std of relevant data
    """
    data = frame_data(frame_file, mask_file, fill_value = fill_value)
    return np.mean(np.ma.MaskedArray(data, np.isnan(data))), \
           np.std(np.ma.MaskedArray(data, np.isnan(data)))

def reslice_mask(data_file, mask_file, order = 0):
    """
    Reslices a mask to data, given
    a file defining the mask and a file defining the data.
    """
    img = ni.load(data_file)
    mask_img = ni.load(mask_file)
    transform = np.eye(4)
    new_transform = np.dot(np.linalg.inv(mask_img.get_affine()),
                           np.dot(transform, img.get_affine()))

    new_mask = affine_transform(mask_img.get_data().squeeze(),
                                new_transform[:3, :3],
                                offset = new_transform[3, :3],
                                output_shape = img.get_shape()[:3],
                                order = order)
    return new_mask

def mask_array(data, mask, fill_value = 0):
    """
    Given 3-D data and a mask, returns a masked array
    with the mask applied to the data.
    Assumes that the mask is (1 = valid), so it inverts the mask
    """
    if data.shape != mask.shape:
        raise Exception('data and mask shape don\'t match')
    mask = invert_mask(mask)
    valid_data = np.ma.MaskedArray(data, np.isnan(data))
    m_array = np.ma.MaskedArray(valid_data, mask=mask, fill_value=fill_value)
    return m_array

def apply_mask(data, mask, fill_value=0):
    """
    Returns data with mask applied.
    """
    return mask_array(data, mask, fill_value).filled()

def extract_values(data, mask, fill_value=0):
    """
    Given 3-D data and a mask, return the values from the data
    after mask has been applied in a vector
    """
    return mask_array(data, mask, fill_value).compressed()

def convert_mask(mask, type):
    """
    Convert mask to datatype type:
        int
        bool
    """
    return np.array(mask, dtype = type)

def threshold_to_binary(mask, threshold):
    """
    Converts a threshold style mask into a binary mask
    """
    return mask > threshold

def invert_mask(mask):
    """
    inverts a mask
    returns a boolean mask
    """
    return mask < 1

