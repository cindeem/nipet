import numpy as np
import csv
from pandas import ExcelFile, read_csv, DataFrame
from os.path import exists, splitext

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

    def set_units(self, units):
        """
        Set self.units to units; units is one of ['min', sec']
        """ 
        self.units = units

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
        """Pulls timing info from csv and stores in an array.
        Parameters
        ---------
            csv_filename:
                the name of the csv file e.g. 'filename.csv'
            units:
                the units the imported data is in
        """
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
            raise IOError("Error reading file " + csv_filename + \
                           " Check if file exists or if file is blank")

    def from_excel(self, excel_file, units = 'sec'):
        """Pulls timing info from excel file and stores in an array.
        Parameters
        ----------
            excel_file:
                the name of the file to import from. 
                e.g. file.xls
            units:
                the units the imported data is in
        """
        try:
            df = ExcelFile(excel_file).parse('Sheet1') #dataframe
            rec = df.to_records()

            #can be converted to numpy array
            #by using rec.astype all the same type
            #then calling .view(that type) with the result 
            #supposedly this is faster than the below method

            dat_arr = np.array(rec.tolist()) #pirate

            #get rid of the 'index' column from pandas
            self.data = dat_arr[0:dat_arr.shape[0], 1:self.col_num + 1]
        except IOError:
            print "Oops."
        self.units = units

    def to_csv(self, outfile, units = 'sec'):
        """Export timing info to csv file
        Parameters
        ----------
            outfile:
                the name of the file to export from. 
                e.g. file.csv
            units:
                the units to export the data in; one of ['min', 'sec']
        """
        #alternative
        #np.saveas('frametime_out.csv', self.data, delimiter = ',')
        #alternative #2: use pandas.DataFrame.to_csv
        if self.units == None:
            self.units = units
        if not exists(outfile):
            with open(outfile, 'wb') as out_file:
                writer = csv.writer(out_file, delimiter = ',')
                writer.writerow(['frame', 'start time', 'duration', 'stop time'])
                data = self.get_data(units)
                print data
                for frame in data:
                    writer.writerow(frame)
        else:
            name, ext = splitext(outfile)
            i = 0
            while exists(name + '-%d'%i + ext):
                i = i + 1
            self.to_csv(name + '-%d'%i + ext, units)

    def to_excel(self, outfile, units = 'sec'):
        """Export timing info to excel file.
        If 

        Parameters
        ----------
            excel_file:
                the name of the file to export from. 
                e.g. file.xls
            units:
                the units to export the data in; one of ['min', 'sec']
        """
        if not self.units:
            self.units = units
        if not exists(outfile):
            df = DataFrame(self.get_data(units), columns = ['frame', 'start time', 'duration', 'stop time'])
            df.to_excel(outfile, sheet_name = 'Sheet1', index = False)
        else:
            name, ext = splitext(outfile)
            i = 1
            while exists(name + ' (%d)'%i + ext):
                i = i + 1
            self.to_excel(name + '-%d'%i + ext, units)

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

    def get_data(self, units = 'sec'):
        """Return timing info as numpy array"""
        if units == 'min':
            return self.to_min()
        else:
            return self.to_sec()

