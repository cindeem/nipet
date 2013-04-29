import numpy as np
import csv
from pandas import ExcelFile, read_csv, DataFrame
from os.path import exists, splitext
import logging
from datetime import datetime 
archive_exts = ['gz']
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
    if ext in archive_exts:
        name, ext2 = splitext(name)
        ext = ext + ext2
    return name + '_' + str(datetime.today()).replace(' ', '-') \
                                             .split('.')[0] + ext
      
def guess_units(data):
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
        self.start = 1
        self.stop = 2
        self.duration = 3

    def correct_data_order(self, data):
        """
        If frame duration and frame stop time are switched, switch them back into the correct order.
        If there are any nan's, remove that frame.
        """
        n_rows, n_col = data.shape
        if data[n_rows - 1, self.stop] < data[n_rows - 1, self.duration]:
            data[:, [self.stop, self.duration]] = data[:, [self.duration, self.stop]]
        data = data[~np.isnan(data).any(axis=1)]
        return data

    def generate_output(self, data):
        """
        Given a data array, which uses expected frame numbers,
        generate an output array for writing to a file
        including the proper file numbers, etc.
        """
        return data


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
        if frame.shape[0] != self.col_num:
            logging.error('Bad number of columns')
            raise FrameError('Bad number of columns')
            return False
        elif not (len(frame.shape) == 1 or frame.shape[1] == 1): 
            logging.error('Extra rows')
            raise FrameError('Extra rows')
            return False
        elif abs(frame[self.duration] - (frame[self.stop] - frame[self.start])) > eps:
            logging.error('Frame entries unaligned')
            raise FrameError('Frame entries unaligned')
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
            curr = curr + 1
            if curr != frame[0]:
                raise FrameError('Numbers not consecutive') #make Error classes
                logging.error('Numbers not consecutive')
            if frame[0] < 0:
                logging.error('Negative frame number')
                raise FrameError("Negative frame number") #make Error classes
            if frame[self.start] < curr_stop:
                logging.error('Frames overlapping')
                raise FrameError("Overlapping frames") 
            curr_start = frame[self.start]
            curr_stop = frame[self.stop]
            self._check_frame(frame)
        return True

    def get_units(self):
        """Return current units of timing array"""
        if self.units:
            return self.units

    def generate_empty_protocol(self, frame_num):
        """Generates empty data array 
        """
        outarray = np.array(np.zeros((frame_num, self.col_num)))
        for i, f in enumerate(outarray):
            f[0] = float(i) + 1
            f[1] = np.nan
            f[2] = np.nan
            f[3] = np.nan
        print outarray
        return outarray

    def from_array(self, array, units):
        """Imports timing info from array in same format.
        Doesn't perform any checks, so be careful when using this method
        """
        self.data = array
        self.units = units
        return self 

    def _time_from_ecat(self, ecat_file, ft_array):
        """ fills in a fiels of empty ft_array using
        data from the ecat mlist and subheaders"""
        shdrs = ecat.load(ecat_file).get_subheaders()
        mlist = ecat.load(ecat_file).get_mlist()
        framelist = mlist.get_series_framenumbers().values()
        for fn, shdr in zip(framelist, shdrs.subheaders):
            start = shdr['frame_start_time'] / 1000
            duration = shdr['frame_duration'] / 1000
            idx = np.where(ft_array[:,0] == fn)
            ft_array[idx, 1:] = [start, duration, start + duration]
       
    def from_ecats(self, ecat_files, units=None):
        """Pulls timing info from ecat file(s) and stores in an array"""
        if not hasattr(ecat_files, '__iter__'):
            ecat_files = [ecat_files]
        nframes = 0
        for f in ecat_files:
            hdr = ecat.load(f).get_header()
            if hdr['num_frames'] > nframes:
                nframes = hdr['num_frames']
                print nframes
        empty_ft = self.generate_empty_protocol(nframes)

        for ef in ecat_files:
            self._time_from_ecat(ef, empty_ft)

        self.data = np.array(empty_ft[0:,0:4]).astype(float)
        # call to correct_data fails due to empty_ft dtype
        if not units:
            self.units = guess_units(self.data)
        else:
            self.units = units
        try:
            self.data = self.correct_data_order(self.data)
            self._validate_frames()
        except FrameError:
            raise DataError('Bad data', self.data, ecat_files)
        return self 

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
                                     delimiter = ',',
                                     skip_header = head)
            except:
                data = np.genfromtxt(csv_file, 
                                     skip_header = head)
            data = self.correct_data_order(data)
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
        return self 

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
            data = dat_arr[0:dat_arr.shape[0], 1:self.col_num + 1]
            data = data.astype(np.float)
            self.data = self.correct_data_order(data)

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
        return self 

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
            writer.writerow(['file number', 'start time', 'duration', 'stop time'])
            data = self.get_data(units)

            out_data = self.generate_output(data)
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
            data = self.generate_output(data)
            df = DataFrame(data, columns = ['file number', 'start time', 'duration', 'stop time'])
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

    def get_start_times(self, units = None):
        if not units:
            units = self.units
        n_rows, n_col = self.data.shape
        start_times = np.zeros((n_rows, 2))
        for k, row in enumerate(self.data):
            start_times[k, 0] = row[0]
            start_times[k, 1] = row[self.start] 
        if self.units == 'min' and units == 'sec':
            return start_times*60.0
        elif self.units == 'sec' and units == 'min':
            return start_times/60.0
        return start_times

    def get_stop_times(self, units = None):
        if not units:
            units = self.units
        n_rows, n_col = self.data.shape
        stop_times = np.zeros((n_rows, 2))
        for k, row in enumerate(self.data):
            stop_times[k, 0] = row[0]
            stop_times[k, 1] = row[self.stop] 
        if self.units == 'min' and units == 'sec':
            return stop_times*60.0
        elif self.units == 'sec' and units == 'min':
            return stop_times/60.0
        return stop_times


    def get_midtimes(self, units=None):
        if not units:
            units = self.units
        n_rows, n_col = self.data.shape
        midtimes = np.zeros((n_rows, 2))
        for k, row in enumerate(self.data):
            midtimes[k, 0] = row[0]
            midtimes[k, 1] = row[self.start] + row[self.duration]/2.0 
        if self.units == 'min' and units == 'sec':
            return midtimes*60.0
        elif self.units == 'sec' and units == 'min':
            return midtimes/60.0
        return midtimes

    def times_to_frames(self, start, stop):
        """
        Given start, stop
        finds range of frames spanning exactly start-stop,
        returns array with all of those indices.
        Should rename.
        """
        if start not in self.data[:, self.start]:
            raise Exception("Please pick a valid start time: " + self.data[:, self.start])
        if stop not in self.data[:, self.stop]:
            raise Exception("Please pick a valid stop time: " + self.data[:, self.stop])
        start_index = np.where(self.data[:, self.start] == start)[0][0] + 1
        stop_index = np.where(self.data[:, self.stop] == stop)[0][0] + 1
        return np.arange(start_index, stop_index + 1)
