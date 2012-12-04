import csv
import numpy as np
from pandas import ExcelFile, readcsv

class FrameTime:
    """
    Reads or generates timing file for use with graphical analysis.
    Format (number of frames X 4):
        frame_number, start_time, stop_time, duration    
    """ 
    def __init__(self):
        """
        col_num 
            number of columns
        """
        self.col_num = 4

    def isempty(self):
        if self.data:
            return False
        return True    

    def delete_frame(self, frame):
        """Delete a frame.
        Currently deletes based on position in array.
        Should eventually delete based on frame number."""
        self.data = numpy.delete(self.data, frame, 0) 

    def _min_to_sec(self, minutes):
        return minutes*60

    def _sec_to_min(self, seconds):
        return seconds/60.0 

    def _check_frame(self, frame):
        return frame.shape[1] == self.col_num 
                and frame.shape[0] == 1    
                and frame[3] == frame[2] - frame[1] 

    def _validate_frames(self):
        """ 
        all frames in order
        frames in order- missing frames
        frames out of order -exception
        negative frames - exception
        0, 1 indexing (fix?)
        overlapping timing, bad durations
        """
        curr = 0
        curr_time = 0
        for i in enumerate(a.shape[0]):
            frame = self.data[i] 
            if frame[0] < 0:
                raise Error("Negative frame number") #make Error classes
            if frame[0] < curr:
                raise Error("Frames out of order") 
            curr = frame[0]
            if frame[1] < curr_time:
                raise Error("Overlapping frames") 
            curr_time = frame[1]
            if not self._check_frame(frame)
                raise Error("Bad frame")
        return True

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
        try:
            infile = open(csv_filename, 'r')
            reader = csv.reader(infile)
            header = reader.readline()
            if header[0].isdigit():
                head = 0
            else:
                head = 1
            self.data = np.loadtxt(csv_filename, delimiter = ',', skiprows = head)
        except:
            raise IOError("Error reading file. Check if file exists or if file is blank")

    def from_excel(excel_file, units = 'sec'):
        """Pulls timing info from excel file and stores in an array"""
        pass

    def to_csv(units = 'sec'):
        """Export timing info to csv file"""

    def to_excel(units = 'sec'):
        """Export timing info to excel file"""

    def get_array(units = 'sec'):
        """Return timing info as numpy array"""
        return self.data

