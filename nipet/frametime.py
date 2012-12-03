import numpy as np
import csv

class FrameTime:
    """
    Generates timing file for use with graphical analysis.
    Format (number of frames X 4):
        frame_number, start_time, stop_time, duration    
    """ 
    def __init__(self):
        self.data_size = 4
        self.clear()

    def isempty(self):
        return self.data == np.array([[0], [0], [0], [0]])     

    def clear(self):
        self.data = np.array([[0], [0], [0], [0]])     

    def _min_to_sec(self, minutes):
        return minutes*60

    def _sec_to_min(self, seconds):
        return seconds/60.0 

    def _validate_frames(self):
        """ 
        all frames in order
        frames in order- missing frames
        frames out of order -exception
        negative frames - exception
        0, 1 indexing (fix?)
        overlapping timing, bad durations
        """
        pass

    def get_units(self):
        """Return current units of timing array"""
        if self.units:
            return self.units

    def generate_empty_protocol(self, frame_num):
        pass

    def from_ecat(self, ecat_file):
        """Pulls timing info from ecat and stores in an array"""
        pass

    def from_csv(self, csv_filename, units = 'sec'): 
        """Pulls timing info from csv and stores in an array"""
        infile = open(csv_filename, 'r')
        reader = csv.reader(infile)
        header = reader.readline()
        self.units = units 
        for row in reader:
            self._append_frame(frame)
        self.data = np.remove(self.data, 0, 1)

    def _entry_to_frame(self, row):
        frame = np.array(row)
        frame = frame.reshape((self.data_size, 1))
        return frame

    def _append_frame(self, frame):
        if self._check_frame(frame):
            self.data = np.hstack((self.data, frame)) 
            
    def _check_frame(self, frame):
        return self.data.shape[0] == self.data_size 
                and self.data.shape[1] == 1    

    def from_excel(excel_file, units = 'sec'):
        """Pulls timing info from excel file and stores in an array"""
        pass

    def to_csv(units = 'sec'):
        """Export timing info to csv file"""

    def to_excel(units = 'sec'):
        """Export timing info to excel file"""

    def get_array(units = 'sec'):
        """Return timing info as numpy array"""

