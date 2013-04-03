import numpy as np
import csv
from pandas import ExcelFile, read_csv, DataFrame
from os.path import exists, splitext
from datetime import datetime 
from nibabel import ecat


def _min_to_sec(minutes):
    """converts minutes to seconds, 
    assuming that input is a number representing minutes"""
    return minutes*60

def _sec_to_min(seconds):
    """converts seconds to minutes, 
    assuming that input is a number representing seconds"""
    return seconds/60.0 

def timestamp(filename):
    name, ext = splitext(filename)
    return name + '_' + str(datetime.today()).replace(' ', '-') \
                                             .split('.')[0] + ext

def correct_data(data):
    """
    If frame duration and frame stop time are switched, switch them back into the correct order.
    If there are any nan's, remove that frame.
    """
    n_rows, n_col = data.shape
    if data[n_rows - 1, 3] < data[n_rows - 1, 2]:
        data[:, [2, 3]] = data[:, [3, 2]]
    data = data[~np.isnan(data).any(axis=1)]
    return data
      
def guess_units(data):
    data = correct_data(data)
    n_rows = data.shape[0]
    if data[n_rows - 1, 3] >= 1000:
        return 'sec'
    return 'min'

def calc_file_numbers(data):
    """
    Given a data array, which uses expected frame numbers,
    generates output file numbers
    """
    file_numbers = []
    expected_frame = 1
    diff = 0
    for frame in data:
        diff = diff + frame[0] - expected_frame
        expected_frame = frame[0] + 1
        file_numbers.append(frame[0] - diff)
    return np.array(file_numbers)

def generate_output(data):
    """
    Given a data array, which uses expected frame numbers,
    generate an output array including the proper file numbers, etc.
    """
    file_nums = calc_file_numbers(data)
    file_nums.shape = (data.shape[0], 1)
    fn_data = np.hstack((file_nums, data))
    rows = data[-1,0]
    out_data = np.empty((rows, 5))
    row_num = 0
    diff = 0
    for frame in fn_data:
        new_diff = int(frame[1] - frame[0])
        for i in range(diff, new_diff):
            out_data[row_num] = [np.nan, frame[0] + i, np.nan, np.nan, np.nan]
            row_num = row_num + 1
        diff = new_diff

        out_data[row_num] = frame
        row_num = row_num + 1
    return out_data

class FrameError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class DataError(Exception):
    def __init__(self, msg = '', data = None, source = ''):
        self.msg = msg
        self.data = data
        self.source = source
    def __str__(self):
        return repr(self.msg) + ' from ' + repr(self.source) + ': ' + repr(self.data)

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
        missing_frames = []
        for frame in self.data:
            if frame[0] < 0:
                raise FrameError("Negative frame number") #make Error classes
            if frame[0] < curr:
                raise FrameError("Frames out of order") 
            if frame[0] != curr + 1:
                for i in range(curr + 1, int(frame[0])): #alternative?
                    missing_frames.append(i) 
            curr = int(frame[0])
            if frame[1] < curr_stop:
                raise FrameError("Overlapping frames") 
            if frame[0] - 1 not in missing_frames and abs(curr_stop - frame[1]) > eps:
                print curr_stop
                print frame
                raise FrameError("Misaligned frames")
            curr_start = frame[1]
            curr_stop = frame[3]
            if not self._check_frame(frame):
                raise FrameError("Bad frame")
        if missing_frames:
            print 'Missing frames: ' + repr(missing_frames)
        return True

    def get_units(self):
        """Return current units of timing array"""
        if self.units:
            return self.units

    def generate_empty_protocol(self, frame_num):
        """Generates empty csv/excel file with header for frametimes,
        which can then be imported by this class."""
        outarray = np.array(np.zeros((frame_num + 1, self.col_num + 2)), \
                             dtype = 'S12')
        outarray[0] = ['file number', 'expected frame', 'start time', 'duration', 'stop time', 'notes']
        for i, f in enumerate(outarray):
            if i != 0:
                f[0] = float(i)
                f[1] = f[0]
                f[2] = ''
                f[3] = ''
                f[4] = ''
                f[5] = ''
        print outarray
        return outarray

    def from_array(self, array, units):
        self.data = array
        self.data = correct_data(self.data)
        self.units = units
        try:
            self._validate_frames()
        except FrameError:
            raise DataError('Bad data', self.data, 'array')


    def _time_from_ecat(self, ecat_file, ft_array):
        shdrs = ecat.load(ecat_file).get_subheaders()
        mlist = ecat.load(ecat_file).get_mlist()
        framelist = mlist.get_series_framenumbers().values()
        for fn, shdr in zip(framelist, shdrs.subheaders):
            start = shdr['frame_start_time'] / 1000
            duration = shdr['frame_duration'] / 1000
            ft_array[fn, 2:5] = [start, duration, start + duration]
       

    def from_ecats(self, ecat_files, units=None):
        """Pulls timing info from ecat file(s) and stores in an array"""
        if not hasattr(ecat_files, '__iter__'):
            ecat_files = [ecat_files]
        nframes = 0
        for f in ecat_files:
            x, y, z, nf = ecat.load(f).get_shape()
            nframes += nf
        empty_ft = self.generate_empty_protocol(nframes)

        for ef in ecat_files:
            self._time_from_ecat(ef, empty_ft)

        self.data = np.array(empty_ft[1:,1:5]).astype(float)
        # call to correct_data fails due to empty_ft dtype
        if not units:
            self.units = guess_units(self.data)
        else:
            self.units = units
        try:
            self._validate_frames()
        except FrameError:
            raise DataError('Bad data', self.data, ecat_files)

    def from_csv(self, csv_file, units=None): 
        """Pulls timing info from csv and stores in an array.
        Parameters
        ---------
            csv_filename:
                the name of the csv file e.g. 'filename.csv'
            units:
                the units the imported data is in
        """
        try:
            with open(csv_file) as infile:
                header = infile.readline()
                if header[0].isdigit():
                    head = 0
                else:
                    head = 1
            #workaround for weird delimiter issues
            try:
                data = np.genfromtxt(csv_file,
                                        skip_header = head, usecols=(1,2,3,4))
            except:
                data = np.genfromtxt(csv_file, delimiter=',',
                                        skip_header = head, usecols=(1,2,3,4))
            data = correct_data(data)
            self.data = data[:, 0:4]

            if not units:
                self.units = guess_units(self.data)
            else:
                self.units = units
        except IOError:
            raise IOError("Error reading file " + csv_file + \
                           " Check if file exists or if file is blank")
        try:
            self._validate_frames()
        except FrameError:
            raise DataError('Bad data', self.data, csv_file)

    def from_excel(self, excel_file, units=None):
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
            print rec
            dat_arr = np.array(rec.tolist()) #pirate
            #get rid of the 'index' column from pandas
            data = dat_arr[0:dat_arr.shape[0], 2:self.col_num + 2]
            data = data.astype(np.float)
            self.data = correct_data(data)

            if not units:
                self.units = guess_units(self.data)
            else:
                self.units = units
        except IOError:
            print "Oops."
        try:
            self._validate_frames()
        except FrameError:
            raise DataError('Bad data', self.data, excel_file)

    def to_csv(self, outfile, units = None):
        """Export timing info to csv file
        Returns location of exported file.
        Automatically timestamps filename in format:
            yyyy-mm-dd-hh:mm:ss
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
        if self.data == None or self.units == None:
            raise DataError('Cannot export; no data!')
        if not units:
            units = self.units
        filename = timestamp(outfile)
        with open(filename, 'wb') as out_file:
            writer = csv.writer(out_file, delimiter = ',')
            writer.writerow(['file number','expected frame', 'start time', 'duration', 'stop time', 'notes'])
            data = self.get_data(units)

            out_data = generate_output(data)
            for frame in out_data:
                writer.writerow(frame)
        return filename

    def to_excel(self, outfile, units = None):
        """Export timing info to excel file.
        Returns location of exported file.
        Automatically timestamps filename in format:
            yyyy-mm-dd-hh:mm:ss

        Parameters
        ----------
            excel_file:
                the name of the file to export from. 
                e.g. file.xls
            units:
                the units to export the data in; one of ['min', 'sec']
        """
        if self.data == None or self.units == None:
            raise DataError('Cannot export; no data!')
        if not units:
            units = self.units
        try:
            filename = timestamp(outfile)
            data = self.get_data(units)
            data = generate_output(data)
            df = DataFrame(data, columns = ['file number', 'expected frame', 'start time', 'duration', 'stop time'])
            df.to_excel(filename, sheet_name = 'Sheet1', index = False)
            return filename
        except IOError:
            print 'Whoops'

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

    def get_data(self, units):
        """Return timing info as numpy array"""
        if units == 'min':
            return self.to_min()
        else:
            return self.to_sec()

    def get_midtimes(self, units=None):
        if not units:
            units = self.units
        n_rows, n_col = self.data.shape
        midtimes = np.zeros((n_rows, 2))
        for k, row in enumerate(self.data):
            midtimes[k, 0] = row[0]
            midtimes[k, 1] = (row[1] + row[3])/2.0 
        if self.units == 'min' and units == 'sec':
            return midtimes*60.0
        elif self.units == 'sec' and units == 'min':
            return midtimes/60.0
        return midtimes
