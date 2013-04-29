import numpy as np
import nibabel as ni

"""
Note that np masked arrays use True to indicate that a value is masked.
This is converted to the more intuitive False to indicate that a value is masked,
but the former is represented internally, so be careful of using that
"""
def reslice_mask(data, mask):
    """
    Reslices a mask to data
    """
    pass

def mask_array(data, mask):
    """
    Given 3-D data and a mask, returns a masked array
    with the mask applied to the data.
    """
    if data.shape != mask.shape:
        mask = reslice_mask(data, mask)
    mask = convert_mask(mask)
    m_array = np.ma.MaskedArray(data, mask=mask)
    return m_array

def apply_mask(data, mask):
    """
    Returns data with mask applied.
    """
    return mask_array(data, mask).data

def retrieve_values(data, mask):
    """
    Given 3-D data and a mask, return the values from the data
    after mask has been applied in a vector
    """
    m_arr = mask_array(data, mask)
    return m_arr[m_data.mask < 1].data

def calc_mean_std(data):
    """
    Given a vector of data, calculate mean/stddev
    """
    return np.mean(data), np.std(data)

def convert_mask(mask):
    """Converts a mask into desired format.
    """
    pass

def _to_boolean(self, mask):
    """
    Converts int or float mask to boolean
    """
    z = np.zeros(mask.shape)
    return mask > z

def _to_binary(self, mask):
    """
    Converts float or boolean mask to int
    """
    return np.array(mask, dtype=int)

def invert_mask(mask):
    """
    inverts a mask
    """
    pass

def mask_to_ismasked(mask):
    """
    takes mask (1 = keep value), inverts to ismasked sense (1 = masked)
    """
    return mask < 1

