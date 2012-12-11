import numpy as np
from pandas import ExcelFile, read_csv

def _min_to_sec(minutes):
    """converts minutes to seconds, 
    assuming that input is a number representing minutes"""
    return minutes*60

def _sec_to_min(seconds):
    """converts seconds to minutes, 
    assuming that input is a number representing seconds"""
    return seconds/60.0 


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
        self.units = None
        self.data = None

    def isempty(self):
        if self.data:
            return False
        return True    

    def delete_frame(self, frame_num):
        """Delete a frame.
        Currently deletes based on position in array.
        Should eventually delete based on frame number."""
        to_delete = self.data[frame_num] 
        self.data = np.delete(self.data, frame_num, 0) 
        return to_delete

    def _check_frame(self, frame):
        """Checks a frame (1x4 array) for the proper shape,
        and if the duration is equal to stop_time - start_time."""
        return frame.shape[0] == self.col_num \
                and True if len(frame.shape) == 1 else frame.shape[1] == 1 \
                and frame[3] == frame[2] - frame[1] 

    def _validate_frames(self):
        """ 
        Possible cases:
            all frames in order 
            frames in order- warning: missing frames
            frames out of order - exception
            negative frames - exception
            0, 1 indexing (fix?)
            overlapping timing, bad durations - exception
            Does timing have to overlap exactly?
        """
        curr = 0 #can replace with fnum in loop
        curr_time = 0
        for fnum, frame in enumerate(self.data):
            if frame[0] < 0:
                raise ValueError("Negative frame number") #make Error classes
            if frame[0] < curr:
                raise ValueError("Frames out of order") 
            if frame[0] != curr + 1:
                missing_frames = True
            curr = frame[0]
            if frame[1] < curr_time:
                raise ValueError("Overlapping frames") 
            curr_time = frame[1]
            if not self._check_frame(frame):
                raise ValueError("Bad frame")
        if missing_frames:
            print "Missing frames"
        return True

    def get_units(self):
        """Return current units of timing array"""
        if self.units:
            return self.units

    def generate_empty_protocol(self, frame_num):
        """Generates empty csv/excel file with header for frametimes,
        which can then be imported by this class."""
        outarray = np.array(np.zeros((frame_num + 1, self.col_num)),\
                             dtype = 'S12')
        outarray[0] = ['frame number', 'start time', 'duration', 'stop time']
        for i, f in enumerate(outarray):
            if i != 0:
                f[0] = float(i)
                f[1] = ''
                f[2] = ''
                f[3] = ''
        return outarray


    def from_ecat(self, ecat_file):
        """Pulls timing info from ecat and stores in an array"""
        pass

    def from_csv(self, csv_filename, units = 'sec'): 
        """Pulls timing info from csv and stores in an array"""
        try:
            with open(csv_filename) as infile:
                header = infile.readline()
                if header[0].isdigit():
                    head = 0
                else:
                    head = 1
            self.data = np.loadtxt(csv_filename, delimiter = ',', 
                                    skiprows = head)
            self.units = units
        except:
            raise IOError("Error reading file. \
                           Check if file exists or if file is blank")

    def from_excel(self, excel_file, units = 'sec'):
        """Pulls timing info from excel file and stores in an array"""
        try:
            df = ExcelFile(excel_file).parse('Sheet1') #dataframe
            df.to_records()
        except:
            print "Oops."
        self.units = units

    def to_csv(self, units = 'sec'):
        """Export timing info to csv file"""

    def to_excel(self, units = 'sec'):
        """Export timing info to excel file"""

    def get_array(self, units = 'sec'):
        """Return timing info as numpy array"""
        return self.data

