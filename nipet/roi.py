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
    """
    Performs similar function to os.path.splitext,
    but properly splits off archive extensions specified
    by archive_exts
    """
    name, ext = splitext(filename)
    if ext in archive_exts:
        name, ext2 = splitext(name)
        ext = ext + ext2
    return name, ext

def rois_over_time(input_files, mask_file, output_file, output_type):
    """
    Returns the frames in the ROIs specified by mask_file from input_files,
    in a variety of formats.
     
    Parameters
    --------
    input_files:
        A string containing a 4-d .nii file,
        or a list of strings containing a list of .nii frames
    mask_file:
        File containing the mask to be used
    output_file:
        Base filename of output file. If output_type does not involve
        outputting a file, this will be ignored.
    output_type:
        Specify what the output should be.
        The valid options are:
            frames_files
                multiple frames of data with mask applied
                written to output files
            4d_file
                4d data block with mask applied
                written to output file
            frames
                Frames of data with the masked applied as an np array
            4d
                4d block of data as an np array, with the mask applied to each frame
    """

    return process_input(input_files, mask_file, output_file, output_type)

def values_over_time(input_files, mask_file):
    """
    Returns the values in the ROIs in input_files specified by mask_file
     
    Parameters
    --------
    input_files:
        A string containing a 4-d .nii file,
        or a list of strings containing a list of .nii frames
    mask_file:
        File containing the mask to be used
   """
 
    return process_input(input_files, mask_file, None, 'values')

def stats_over_time(input_files, mask_file):
    """

    Returns the mean values and standard deviations in the ROIs in input_files specified by mask_value
 
    Parameters
    --------
    input_files:
        A string containing a 4-d .nii file,
        or a list of strings containing a list of .nii frames
    mask_file:
        File containing the mask to be used
    """
 
    return process_input(input_files, mask_file, None, 'stats')

def process_input(input_files, mask_file, output_type, output_file=None, fill_value=0):
    """
    Processes 4-D input data, and returns output.
    
    Parameters
    ---------
    input_files:
        A string containing a 4-d .nii file,
        or a list of strings containing a list of .nii frames
    mask_file:
        File containing the mask to be used
    output_file:
        Base filename of output file. If output_type does not involve
        outputting a file, this will be ignored.
    output_type:
        Specify what the output should be.
        The valid options are:
            'frames_files' : returns list of strings 
                multiple frames of data with mask applied
                written to output files
            4d_file : string
                4d data block with mask applied
                written to output file
            frames : array
                Frames of data with the masked applied as an np array
            4d : array 
                4d block of data as an np array, with the mask applied to each frame
            values : array
                An array of the values that were not masked in each frame 
            stats : flattened array
                An np array with the mean and std for desired values in each frame
    """
    f = _pick_function(input_files, output_type, output_file)
    output, affine = process_files(f, input_files, mask_file, fill_value)

    if isinstance(output, list):
        output = np.array(output)
    if isinstance(affine, list):
        affine = affine[0]
   
    if output_type == 'frames_files':
        if output_file is None:
            raise Exception("must specify an output file for output type")
        name, ext = split_archive_ext(output_file)
        outfiles = []
        for k, frame in enumerate(output):
            outfile = name + '_frame_%04d'%k + ext
            outfiles.append(outfile)
            new_img = ni.Nifti1Image(data=frame, affine=affine) 
            ni.save(new_img, outfile)
        return outfiles
    elif output_type == '4d_file':
        if output_file is None:
            raise Exception("must specify an output file for output type")
        name, ext = split_archive_ext(output_file)
        new_img = ni.Nifti1Image(data=output, affine=affine) 
        ni.save(new_img, output_file)
        return output_file
    elif output_type == 'frames' or output_type == '4d':
        return output, affine
    elif output_type == 'stats' or output_type == 'values':
        return output
    else:
        raise Exception('Output should be "frames", "4d", "values", or "stats"')
            
def _pick_function(input_files, output_type, output_file):
    """
    desired_output:
        One of the options listed in process_input

    """
    if isinstance(input_files, list): 
        if output_type == 'frames' or output_type == '4d':
            f = frame_data
        elif output_type == 'frames_files' or output_type == '4d_file':
            if output_file == None:
                raise Exception('Must specify an output file if requested output is %s'%output_type)
            f = frame_data
        elif output_type == 'values':
            f = frame_values
        elif output_type == 'stats':
            f = frame_stats 
        else:
            raise Exception('output_type should be in "frames_file", "4d_file", \
                            "frames", "4d", "values", or "stats"')
    elif isinstance(input_files, str):
        if output_type == 'frames' or output_type == '4d':
            f = apply_mask
        elif output_type == 'frames_files' or output_type == '4d_file':
            if output_file == None:
                raise Exception('Must specify an output file if requested output is %s'%output_type)
            f = apply_mask
        elif output_type == 'values':
            f = extract_values
        elif output_type == 'stats':
            f = get_stats 
        else:
            raise Exception('output_type should be in "frames_file", "4d_file", \
                            "frames", "4d", "values", or "stats"')
 
    return f

  
def process_files(f, input_files, mask_file, fill_value = 0):
    """
    Processes input masked with the mask defined in mask_file
    with the function f.

    Parameters
    ----------
    f
        A function that takes a single input file or array, a mask file or array, and a fill value,
        and returns some data as an array
    input_files
        A string defining a 4-D file, or a list of strings defining 3-D files
        A single 3-D file should still be passed in in a list.
    mask_file
        A string that gives a file defining a mask
    """
    if isinstance(input_files, str):
        img = ni.load(input_files)
        data = img.get_data()
        affine = img.get_affine()
        mask_img = ni.load(mask_file)
        mask = mask_img.get_data()
        if len(data.shape) != 4:
            raise Exception('Not a 4-D data file')
        frame_num = data.shape[0]
        output = []
        for k, frame in enumerate(data):
            output.append(np.array(f(frame, mask, 0)))
        output = np.array(output)
            
    elif isinstance(input_files, list):
        output = []
        affines = []
        for k, infile in enumerate(input_files):
            img = ni.load(infile)
            affines.append(img.get_affine())
            output.append(f(infile, mask_file, 0))
        # are all affines the same?
        affine = affines[0]

    else:
        raise Exception('Input %s should be the name of a 4d .nii file, or a list of 3d .nii files'% input_files)
    return output, affine
     
def frame_data(frame_file, mask_file, fill_value=0):
    """
    Returns the data in the .nii file specified by frame_file,
    after filling in all values not in the ROI specified by mask_file
    with 0.
    """
    img = ni.load(frame_file)
    data = img.get_data()
    mask = reslice_mask(frame_file, mask_file)
    return apply_mask(data, mask, fill_value = fill_value)

def frame_values(frame_file, mask_file, fill_value=0):
    """
    Returns the values of the data in ROIs in the .nii file specified by frame_file,
    after filling in all values not in the ROI specified by mask_file
    with 0.
    
    """
    img = ni.load(frame_file) 
    data = img.get_data()
    mask = reslice_mask(frame_file, mask_file)
    return extract_values(data, mask, fill_value = fill_value)
    
def frame_stats(frame_file, mask_file, fill_value = 0):
    """
    Returns the mean and std for data in the ROIs in the .nii file specified by frame_file,
    after filling in all values not in the ROI specified by mask_file
    with 0.
    
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
    Given 3-D data in an np array and a mask, returns a masked array
    with the mask applied to the data.
    Assumes that the mask has (1 = valid), so it inverts the mask
    in order to use numpy's masked array libraries.
    """
    if data.shape != mask.shape:
        raise Exception('data and mask shape don\'t match')
    mask = invert_mask(mask)
    valid_data = np.ma.MaskedArray(data, np.logical_or(np.isnan(data), data == 0))
    m_array = np.ma.MaskedArray(valid_data, mask=mask, fill_value=fill_value)
    return m_array

def apply_mask(data, mask, fill_value=0):
    """
    Given an np array of data and mask, and a fill value,
    returns data after all masked values have been filled with fill_value
    """
    return mask_array(data, mask, fill_value).filled()

def extract_values(data, mask, fill_value=0):
    """
    Given 3-D data and a mask, return all non masked values after
    the mask has been applied to the data.
    """
    return np.array(mask_array(data, mask, fill_value).compressed())

def get_stats(data, mask, fill_value=0):
    output_data = apply_mask(data, mask, fill_value = fill_value)
    return np.mean(np.ma.MaskedArray(output_data, np.isnan(data))), \
           np.std(np.ma.MaskedArray(output_data, np.isnan(data)))

def convert_mask(mask, type):
    """
    Convert mask to datatype type:
        int
        bool
    """
    return np.array(mask, dtype = type)

def threshold_to_binary(mask, threshold, exclusive = True):
    """
    Converts a threshold style mask into a binary mask
    """
    if exclusive:
        return mask > threshold
    return mask >= threshold

def invert_mask(mask):
    """
    inverts a binary mask
    returns a boolean mask
    """
    return mask < 1

