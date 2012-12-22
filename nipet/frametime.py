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
        frame_number, start_time, duration, stop_time    
    """ 
    def __init__(self):
        """
        Reads or generates timing file for use with graphical analysis.
        Format (number of frames X 4):
        frame_number, start_time, duration, stop_time    

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

    def _check_frame(self, frame, eps = 1e-4):
        """Checks a frame (1x4 array) for the proper shape,
        and if the duration is equal to stop_time - start_time."""
        print frame
        if frame.shape[0] != self.col_num:
            print "Bad number of columns"
            return False
        elif not (len(frame.shape) == 1 or frame.shape[1] == 1): 
            print "Extra rows"
            return False
        elif abs(frame[2] - (frame[3] - frame[1])) > eps:
            print "Frame entries unaligned"
            print frame
            return False
        else:
            return True

    def _validate_frames(self, eps = 1e-4):
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
        curr_start = 0
        curr_stop = 0
        for frame in self.data:
            if frame[0] < 0:
                raise ValueError("Negative frame number") #make Error classes
            if frame[0] < curr:
                raise ValueError("Frames out of order") 
            if frame[0] != curr + 1:
                missing_frames = True
            curr = frame[0]
            if frame[1] < curr_stop:
                raise ValueError("Overlapping frames") 
            if abs(curr_stop - frame[1]) > eps:
                print curr_stop
                print frame
                raise ValueError("Misaligned frames")
            curr_start = frame[1]
            curr_stop = frame[3]
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
        outarray = np.array(np.zeros((frame_num + 1, self.col_num)), \
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
            self.data = df.to_records()
        except IOError:
            print "Oops."
        self.units = units

    #need to write tests for this still
    def to_csv(self, units = 'sec'):
        """Export timing info to csv file"""
        #first way to do it
        #np.saveas('frametime_out.csv', self.data, delimiter = ',')
        #second way to do it
        with open('frametime_out.csv', 'wb') as outfile
        writer = csv.writer(outfile, delimiter = ',')
        writer.writerow(['frame', 'start time', 'duration', 'stop time'])
        for frame in self.data:
            writer.writerow(frame)

    def to_excel(self, units = 'sec'):
        """Export timing info to excel file"""

    def to_min(self):
        """Returns the frametime array in minutes."""
        if self.units == 'min':
            return self.data
        elif self.units == 'sec':
            return self.data * 1/60.0

    def to_sec(self):
        """Returns the frametime array in seconds."""
        if self.units == 'sec':
            return self.data
        elif self.units == 'min':
            return 60.0 * self.data

    def get_array(self, units = 'sec'):
        """Return timing info as numpy array"""
        if units == 'min':
            return self.to_min()
        else:
            return self.to_sec()

