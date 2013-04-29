import numpy as np
import nibabel as ni
from scipy.ndimage import affine_transform

"""
Note that np masked arrays use True to indicate that a value is masked.
This is converted to the more intuitive False to indicate that a value is masked,
but the former is represented internally, so be careful of using that
"""
def data_4d(data_block, mask_file):
    """
    Does stuff with data in a 4d data block
    """
    for frame in data_block:
        mask = reslice_mask(frame, mask_file)
        mask_array(frame, mask)

def frame_data(frame, mask_file, fill_value):
    """
    applies mask to frame,
    returns vector of relevant data points
    """
    img = ni.load(frame) 
    data = img.get_data()
    mask = reslice_mask(frame, mask_file)
    return extract_values(data, mask, fill_value = fill_value)
    
def frame_stats(frame, mask_file):
    """
    applies mask to frame,
    returns mean and std of relevant data
    """
    data = data_from_frame(frame, mask_file, fill_value = fill_value)
    return mean(data), std(data)

def apply_mask_to_frame(frame, mask_file): 
    """
    Applies mask to frame,
    returns a nifti image with the masked data and same affine
    """
    img = ni.load(frame) 
    data = img.get_data()
    mask = reslice_mask(frame, mask_filerame, mask_file)
    new_affine = img.affine()
    new_data = apply_mask(data, mask, fill_value=0)
    return Nifti1Image(new_data, new_affine)

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
    m_array = np.ma.MaskedArray(data, mask=mask, fill_value=fill_value)
    return m_array

def apply_mask(data, mask, fill_value):
    """
    Returns data with mask applied.
    """
    return mask_array(data, mask, fill_value).filled()

def extract_values(data, mask, fill_value):
    """
    Given 3-D data and a mask, return the values from the data
    after mask has been applied in a vector
    """
    return mask_array(data, mask, fill_value).compressed()

def mean(data):
    """
    Given a vector of data, calculate mean
    """
    return np.mean(data)

def std(data):
    """
    Given a vector of data, calculate mean
    """   
    return np.std(data)

def convert_mask(mask, type):
    """
    Convert mask to datatype type:
        int
        bool
    """
    return np.array(mask, dtype = type)

def invert_mask(mask):
    """
    inverts a mask
    returns a boolean mask
    """
    return mask < 1

