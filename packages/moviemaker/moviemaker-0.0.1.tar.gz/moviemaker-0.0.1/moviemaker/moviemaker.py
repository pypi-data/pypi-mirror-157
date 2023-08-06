"""
The Moviemaker module.

Plesae have a look at the README file for a description of what this module is doing.

Created on Mon Jun  6 14:55:38 2022

@author: Antonio Bulgheroni
"""

import ctypes
import logging
import sys
import time
from pathlib import Path

import moviepy.video.compositing.concatenate
import moviepy.video.io.ImageSequenceClip
import moviepy.video.io.VideoFileClip
import moviepy.video.VideoClip
from PIL import Image, UnidentifiedImageError
from proglog import TqdmProgressBarLogger
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow

from moviemaker.moviemaker_ui import Ui_MainWindow

Signal = QtCore.pyqtSignal
Slot = QtCore.pyqtSlot


log = logging.getLogger(__name__)

LEVELS = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
          logging.CRITICAL)


class Signaller(QtCore.QObject):
    """
    A sub-class of QObject to contain a signal.

    Only QObejct derived instances are allowed to have a signal, so if you want to have a no
    QtObject to emit a signal, you have to add a Signaller like this to its attributes.

    This specific signaller contains only one Qt Signal emitting a formatted string a logging.LogRecord
    and it is used to establish a communication between a the logging module and a PlainText object in a
    QtWindow.

    """

    signal = Signal(str, logging.LogRecord)


class ProglogSignaller(QtCore.QObject):
    """
    A sub-class of QObject to contain a signal.

    Only QObejct derived instances are allowed to have a signal, so if you want to have a no QtObject
    to emit a signal, you have to add a Signaller like this to its attributes.

    This specific signaller contains two Qt Signals:
        - signal_max --> maximum value of a progress bar
        - signal_progress --> current index of a progress bar

    This specific signaller is used to establish a connection between a ProglogSignaller
    and a QProgressBar.

    """

    signal_max = Signal(int)
    signal_progress = Signal(int)


class QtHandler(logging.Handler):
    """
    A sub-class of the logging.Handler.

    It incorporates a Signaller to be able to emit a Qt Signal.

    """

    def __init__(self, slotfunc, *args, **kwargs):
        """
        Build an instance of QtHandler.

        Parameters
        ----------
        slotfunc : CALLABLE
            The slot function which the Signaller.signal is connected.
        *args : positional arguments
            All other positional arguments to be passed to the parent constructor.
        **kwargs : keyword arguments
            All keywork arguments to be passed to the parent constructor.

        Returns
        -------
        None.

        """
        super().__init__(*args, **kwargs)
        self.signaller = Signaller()
        self.signaller.signal.connect(slotfunc)

    def emit(self, record):
        """Emit the signaller signal containing the formatted string and the logging.Record."""
        s = self.format(record)
        self.signaller.signal.emit(s, record)


class MyBarLogger(TqdmProgressBarLogger):
    """
    A sub-class of the TqdmProgressBarLogger.

    It overloads the bars_callback method and has the ProglogSignaller with the
    two signals to control QProgressBar

    """

    def __init__(self, slotfunc_max, slotfunc_progress, *args, **kawrgs):
        """
        Build an instance of MyBarLogger.

        Parameters
        ----------
        slotfunc_max : CALLABLE
            Slot function to connect the maximum of the Proglog maximum index to
            the QProgressBar maximum value.
        slotfunc_progress : CALLABLE
            Slot function to connect the current index of the Proglog bar with the
            QProgressBar value.
        *args : positional arguments
            other positional argumets to be passed to the parent constructor.
        **kawrgs : keyword arguments
            other keyword arguments to be passed to the parent constructor.

        Returns
        -------
        None.

        """
        super().__init__(*args, **kawrgs)
        self.signaller = ProglogSignaller()
        self.signaller.signal_max.connect(slotfunc_max)
        self.signaller.signal_progress.connect(slotfunc_progress)

    def emit_max(self, maxi):
        """Emit the signal with the maximum index of the proglog progress bar."""
        self.signaller.signal_max.emit(maxi)

    def emit_progress(self, prog):
        """Emit the signal with the current index of the proglog progress bar."""
        self.signaller.signal_progress.emit(prog)

    def bars_callback(self, bar, attr, value, old_value):
        """
        Overload ot the bars_callback.

        This method is called everytime any value of a bar is changed.

        We will only care about the bar named 't'.
        We will call emit_max when the attribute is total.
        We will call emit_progress when the attribute is index

        Parameters
        ----------
        bar : STRING
            The name of the bar the.
        attr : STRING
            The name of the attribute being changed.
        value : NUMERIC
            The new value of the attribute.
        old_value : NUMERIC
            The previos value of the attribute.

        Returns
        -------
        None.

        """
        if bar == 't':
            if attr == 'index':
                self.emit_progress(value)
            elif attr == 'total':
                self.emit_max(value)
            else:
                print('{} is {}'.format(attr, value))


def ctname():
    """
    Return the current QThread name.

    Returns
    -------
    STRING
        The name of the current QThread.

    """
    return QtCore.QThread.currentThread().objectName()


class Worker(QtCore.QObject):
    """
    A Worker class derived from QObject.

    This class will be performing the real job.
    It will be moved to a separate Thread in order to leave the GUI responsibe

    """

    # signal to confirm that the worker did its job
    work_done = Signal(bool, name='work_done')
    # signal to indicate the whole amount of work to do
    how_much_work = Signal(int, name='how_much_work')
    # signal to show how much work has been already done.
    work_progress = Signal(int, name='work_progress')

    def __init__(self, parent=None):
        """
        Build an instance of a generic worker.

        It sets its parent and call the super constructor

        Parameters
        ----------
        parent : Object, optional
            The parent object.

        Returns
        -------
        None.

        """
        self.parent = parent
        super().__init__(parent=parent)

    def get_imagelist(self, input_path, file_filter, display=False, as_path=True):
        """
        Return the image list.

        Scan the input_path applying the file_filer and returns all matching files
        in a list.

        Parameters
        ----------
        input_path : Path or string representing the input folder
            DESCRIPTION.
        file_filter : STRING
            A wildcard (*,?) file type filter
        display : BOOL, optional
            If true, the returned list will be sent to the logger.
            The default is False.
        as_path : BOOL, optional
            If True the returned list will be containing Path objects instead of strings.
            The default is True.

        Returns
        -------
        image_list : list of Path objects or strings
            The list of matching files found in input_path

        """
        if as_path:
            image_list = sorted(list(Path(input_path).glob(file_filter)))
            # image_list = sorted( [img for img in Path(input_path).glob(file_filter)])
        else:
            image_list = sorted([str(img)
                                for img in Path(input_path).glob(file_filter)])
        if display:
            log.info('Found a total of %s images in the input folder matchign the filter',
                     len(image_list), extra=self.extra)
            for img in image_list:
                log.info(img.name, extra=self.extra)
        return image_list


class ConverterWorker(Worker):
    """
    The specialized ConverterWorker.

    It takes care of converting input images in a more suitable format.
    """

    def __init__(self, parent=None):
        """
        Build an instance of a ConverterWorker.

        Parameters
        ----------
        parent : Object, optional
            The parent object. The default is None.

        Returns
        -------
        None.

        """
        self.converter_input_folder = ''
        self.converter_output_folder = ''
        self.converter_filter = ''
        self.converter_output_format = ''
        self.extra = ''
        self.converter_image_list = []
        super().__init__(parent=parent)

    def update_parameters(self, input_path, file_filter, output_path, output_format):
        """
        Assign the conversion parameters to the instance members.

        In normal use, the GUI Thread will call this method transfering the GUI input values

        Parameters
        ----------
        input_path : Path or STRING
            The input folder for the conversion.
        file_filter : STRING
            A wildcard pattern to select the images to be converted.
        output_path : PATH or STRING
            The output folder for the conversion.
        output_format : STRING
            The output format.

        Returns
        -------
        None.

        """
        self.converter_input_folder = Path(input_path)
        self.converter_output_folder = Path(output_path)
        self.converter_filter = file_filter
        self.converter_output_format = output_format

    @Slot()
    def start(self):
        """
        Start the worker.

        This is a Qt Slot

        Returns
        -------
        None.

        """
        start_time = time.time()
        self.extra = {'qThreadName': ctname()}
        log.debug('Started work %s', self.objectName(), extra=self.extra)
        log.debug('Input path: %s', str(
            self.converter_input_folder), extra=self.extra)
        log.debug('File filter: %s', self.converter_filter, extra=self.extra)
        log.debug('Output path: %s', str(
            self.converter_output_folder), extra=self.extra)
        log.debug('Output format: %s',
                  self.converter_output_format, extra=self.extra)

        # make the dest folder
        self.converter_output_folder.mkdir(exist_ok=True)

        # get the list of images
        self.converter_image_list = self.get_imagelist(Path(self.converter_input_folder),
                                                       self.converter_filter)

        # reset progress bar and set its max
        self.how_much_work.emit(len(self.converter_image_list))
        self.work_progress.emit(0)
        i = 1

        # start the real work
        for img in self.converter_image_list:

            # stop the loop here if asked to sktop
            if QtCore.QThread.currentThread().isInterruptionRequested():
                log.info('Received interruption request', extra=self.extra)
                break
            outputfilename = Path(str(img.stem) + '.'
                                  + self.converter_output_format)
            try:
                log.info('Converting %s in %s', img.name,
                         self.converter_output_format,
                         extra=self.extra)
                im = Image.open(img)
                im = im.convert('RGB')
                im.save(self.converter_output_folder
                        / outputfilename, self.converter_output_format)
            except FileNotFoundError as e:
                log.error('File %s not found. Skipping it',
                          str(img.name), extra=self.extra)
                log.exception(e, extra=self.extra)
            except UnidentifiedImageError as e:
                log.error('The image %s can\'t be opened and identified. Skipping it', str(img.name),
                          extra=self.extra)
                log.exception(e, extra=self.extra)
            except (ValueError, TypeError) as e:
                log.exception(e, extra=self.extra)
            self.work_progress.emit(i)
            i += 1
        self.work_done.emit(True)
        delta_time = time.time() - start_time
        log.info('Conversion of %s images finished in %.3f seconds',
                 len(self.converter_image_list), delta_time, extra=self.extra)


class SequenceWorker(Worker):
    """
    The specialized SequenceWorker.

    It takes care of transforming a sequence of images in a video clip
    """

    def __init__(self, parent=None):
        """
        Build an instance of the SequenceWorker.

        Parameters
        ----------
        parent : Object, optional
            The parent object. The default is None.

        Returns
        -------
        None.

        """
        self.sequence_input_folder = ''
        self.sequence_file_filter = ''
        self.sequence_output_file = ''
        self.sequence_fps = 4
        self.extra = ''
        self.sequence_proglog_bar = ''
        super().__init__(parent=parent)

    def update_parameters(self, input_path, file_filter, output_file, fps):
        """
        Assign the sequence parameters.

        In normal use, the GUI Thread will call this method transfering the GUI input values

        Parameters
        ----------
        input_path : Path-like object or STRING
            The input folder where the images are located.
        file_filter : STRING
            A wild-card filter to select a subset of the input images.
        output_file :  Path-like object or STRING
            The name of the output file. It must be a .mp4 file
            No validation on the extension is performed here since it is already
            done by the GUI
        fps : FLOAT
            Number of frame per seconds.

        Returns
        -------
        None.

        """
        self.sequence_input_folder = Path(input_path)
        self.sequence_file_filter = file_filter
        self.sequence_output_file = Path(output_file)
        self.sequence_fps = fps

    @Slot()
    def start(self):
        """
        Start the worker.

        Here is where the sequence to video conversion is really performed.
        A ImageSequenceClip is created with the image list and a VideoClip is then saved.

        The GUI is updating the ProgressBar thanks to the MyBarLogger interface between Qt
        and ProgLog.

        This is a Qt Slot.

        Returns
        -------
        None.

        """
        start_time = time.time()
        self.extra = {'qThreadName': ctname()}

        self.how_much_work.emit(1)
        self.work_progress.emit(0)

        # moviepy requires a proglog progress bar handler.
        self.sequence_proglog_bar = MyBarLogger(
            self.how_much_work.emit, self.work_progress.emit, bars=('t',))

        # make sure that the directory of the outputfile exists
        self.sequence_output_file.parent.mkdir(exist_ok=True)
        log.info('Generating image sequence', extra=self.extra)
        log.info('It may take several minutes', extra=self.extra)
        image_list = self.get_imagelist(
            self.sequence_input_folder, self.sequence_file_filter, display=False, as_path=False)
        try:
            clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(
                image_list, fps=self.sequence_fps)
            self.work_progress.emit(1)
            log.info('Generating output file %s',
                     self.sequence_output_file.name, extra=self.extra)
            log.info('It may take several minutes', extra=self.extra)
            clip.write_videofile(filename=str(
                self.sequence_output_file), logger=self.sequence_proglog_bar)
            log.info('Writing output file %s on disk', self.sequence_output_file.name,
                     extra=self.extra)
        except (ValueError, KeyError, Exception) as e:
            log.exception(e, extra=self.extra)
        self.work_done.emit(True)
        delta_time = time.time() - start_time
        log.info('Generation of video clip finished %.3f seconds', delta_time,
                 extra=self.extra)


class JoinWorker(Worker):
    """
    The specialized join worker.

    It is responsible for concatenating two video clips.

    No fancy stuff here, no clipping, no transitions, just append one video to the next.
    """

    def __init__(self, parent=None):
        """
        Build an instance of JoinWorker.

        Parameters
        ----------
        parent : Object, optional
            The parent object. The default is None.

        Returns
        -------
        None.

        """
        self.parent = parent
        self.input_file1 = ''
        self.input_file2 = ''
        self.output_file = ''
        self.extra = ''
        self.join_proglog_bar = ''
        super().__init__(parent=parent)

    def update_parameters(self, input_file1, input_file2, output_file):
        """
        Assign the conversion parameters to the instance members.

        In normal use, the GUI Thread will call this method transfering the GUI input values

        Parameters
        ----------
        input_file1 : Path-like or STRING
            Path to the first video.
        input_file2 : Path-like or STRING
            Path to the second video.
        output_file : Path-like or STRING
            Output file full path.

        Returns
        -------
        None.

        """
        self.input_file1 = Path(input_file1)
        self.input_file2 = Path(input_file2)
        self.output_file = Path(output_file)

    @Slot()
    def start(self):
        """
        Start the worker.

        Here is where the sequence to video conversion is really performed.
        Both input files are open as VideoFileClip. The concatenate clip is created and saved.

        The GUI is updating the ProgressBar thanks to the MyBarLogger interface between Qt
        and ProgLog.

        This is a Qt Slot.

        Returns
        -------
        None.

        """
        start_time = time.time()
        self.extra = {'qThreadName': ctname()}

        # moviepy requires a proglog progress bar handler.
        self.join_proglog_bar = MyBarLogger(
            self.how_much_work.emit, self.work_progress.emit, bars=('t',))

        self.how_much_work.emit(3)
        self.work_progress.emit(0)
        try:
            log.info('Loading video %s',
                     self.input_file1.name, extra=self.extra)
            clip1 = moviepy.video.io.VideoFileClip.VideoFileClip(
                str(self.input_file1))
            self.work_progress.emit(1)

            log.info('Loading video %s',
                     self.input_file2.name, extra=self.extra)
            clip2 = moviepy.video.io.VideoFileClip.VideoFileClip(
                str(self.input_file2))
            self.work_progress.emit(2)
            log.info('Concatenating the input videos', extra=self.extra)
            outclip = moviepy.video.compositing.concatenate.concatenate_videoclips([
                                                                                   clip1, clip2])
            self.work_progress.emit(3)

            self.work_progress.emit(0)
            log.info('Writing the output file %s',
                     self.output_file.name, extra=self.extra)
            outclip.write_videofile(
                str(self.output_file), logger=self.join_proglog_bar)
        except (ValueError, OSError) as e:
            log.exception(e, extra=self.extra)
        self.work_done.emit(True)
        delta_time = time.time() - start_time
        log.info('Joining of video clips finished %.3f seconds',
                 delta_time, extra=self.extra)


class MovieMakerWindow(QMainWindow, Ui_MainWindow):
    """
    MovieMaker main window.

    This is a subclass of QMainWindow and of the specific Ui_MainWindow generated
    via the QtDesigner.

    """

    # Used to have different colors for each logging level.
    COLORS = {
        logging.DEBUG: 'black',
        logging.INFO: 'blue',
        logging.WARNING: 'orange',
        logging.ERROR: 'red',
        logging.CRITICAL: 'purple'
    }

    def __init__(self, app):
        """
        Build a MovieMakerWindow instance.

        Parameters
        ----------
        app : QApplication
            The application reference.

        Returns
        -------
        None.

        """
        super().__init__()
        self.app = app
        self.setupUi(self)

        # create a logging handler with a slot function pointing to update_status
        self.handler = QtHandler(self.update_status)
        self.extra = {'qThreadName': ctname()}

        # create a formatter and assign it to the handler
        fs = '[%(asctime)s] %(qThreadName)-12s %(levelname)s: %(message)s'
        formatter = logging.Formatter(fs, datefmt='%Y%m%d-%H:%M:%S')
        self.handler.setFormatter(formatter)
        log.addHandler(self.handler)

        # initialize workers and threads dictionaries
        self.workers = {}
        self.worker_threads = {}

        # start the threads and their workers
        self.start_thread()

        # connect all signals and slots
        self.connectSignalsSlot()

    def show(self):
        """
        Show the main windown.

        Overload of the parent show method adding a message in the log window
        """
        log.info('Welcome to the Moviemaker GUI.', extra=self.extra)
        super().show()

    def start_thread(self):
        """
        Start all the needed threads.

        The program is using a separate thread for each of the three workers plus
        another one executing the GUI.

        A reference of all workers and threads are stored in the self.workers
        and self.worker_threads dictionaries.

        Returns
        -------
        None.

        """
        worker_list = {
            'Converter': {
                'WorkerClassType': 'ConverterWorker',
                'WorkerObjectName': 'Converter',
                'WorkerThreadName': 'ConverterThread'
            },
            'Sequence': {
                'WorkerClassType': 'SequenceWorker',
                'WorkerObjectName': 'Sequence',
                'WorkerThreadName': 'SequenceThread'
            },
            'Join': {
                'WorkerClassType': 'JoinWorker',
                'WorkerObjectName': 'Join',
                'WorkerThreadName': 'JoinThread'
            }
        }

        for key, worker in worker_list.items():
            new_worker = globals()[worker['WorkerClassType']]()
            new_worker.parent = self
            new_worker_thread = QtCore.QThread()
            new_worker.setObjectName(worker['WorkerObjectName'])
            new_worker_thread.setObjectName(worker['WorkerThreadName'])
            new_worker.moveToThread(new_worker_thread)
            new_worker_thread.start()
            new_worker.work_done.connect(self.enable_inputs)
            new_worker.how_much_work.connect(self.progressBar.setMaximum)
            new_worker.work_progress.connect(self.progressBar.setValue)
            self.workers[key] = new_worker
            self.worker_threads[worker['WorkerThreadName']] = new_worker_thread

    def kill_thread(self):
        """
        Kill all threads.

        Returns
        -------
        None.

        """
        for key, thread in self.worker_threads.items():
            if thread.isRunning():
                thread.quit()
                thread.wait()
            else:
                log.debug('Thread %s was dead already', key, extra=self.extra)

    def force_quit(self):
        """
        Force threads to stop.

        Returns
        -------
        None.
        """
        for thread in self.worker_threads.values():
            if thread.isRunning():
                thread.quit()
                thread.wait()

    @Slot(str, logging.LogRecord)
    def update_status(self, status, record):
        """
        Update the status window.

        This is the Qt Slot connected to the QtHandler Signaller.

        Parameters
        ----------
        status : STRING
            The formatted string to be appended to the message window.
        record : logging.LogRecord
            The LogRecord as transmitted by the logging module.

        Returns
        -------
        None.

        """
        color = self.COLORS.get(record.levelno, 'black')
        s = '<pre><font color="%s">%s</font></pre>' % (color, status)
        self.messagewindow.appendHtml(s)

    def connectSignalsSlot(self):
        """Connect all other signals to slots."""
        # The three start buttons.
        self.converter_start_button.clicked.connect(
            self.workers['Converter'].start)
        self.converter_start_button.clicked.connect(
            lambda: self.enable_inputs(False))
        self.sequence_start_button.clicked.connect(
            self.workers['Sequence'].start)
        self.sequence_start_button.clicked.connect(
            lambda: self.enable_inputs(False))
        self.join_start_button.clicked.connect(self.workers['Join'].start)
        self.join_start_button.clicked.connect(
            lambda: self.enable_inputs(False))

        # Connect the about to quit action to the force_quit to kill all threads
        self.app.aboutToQuit.connect(self.force_quit)

    def converter_open_input_folder(self):
        """Open a file dialog for the converter input folder."""
        directory = self.converter_input_path_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getExistingDirectory(
            self, 'Input images folder', directory=directory)
        if returnpath:
            self.converter_input_path_text.setText(returnpath)
            self.converter_validate_start()

    def converter_open_output_folder(self):
        """Open a file dialog for the converter output folder."""
        directory = self.converter_output_path_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getExistingDirectory(
            self, 'Output folder', directory=directory)
        if returnpath:
            self.converter_output_path_text.setText(returnpath)
            self.converter_validate_start()

    def converter_test_filter(self):
        """Print the list of files machng the filter condition."""
        self.sequence_get_imagelist(Path(self.converter_input_path_text.text()),
                                    self.converter_file_filter_text.text(),
                                    display=True)

    @Slot()
    def converter_validate_start(self):
        """
        Perform a validation check on the input fieds for the converter tab.

        The start button becomes enabled only if all fields (input and output path and file filter)
        are valid. No check is perform on the format since it is taken from a closed list.
        When the start button is enabled, all parameters are transferred to the ConverterWorker
        making it ready for the start.

        The check button is active if input folder and filter are set.

        Note
        ----

        This method is a Qt Slot and it is connected with the editing finished signal of the
        corresponding input filed.

        Returns
        -------
        None.

        """
        ok_to_start = True
        ok_to_test = True
        if not self.converter_input_path_text.text():
            ok_to_start = ok_to_start and False
            ok_to_test = ok_to_test and False
        if not self.converter_file_filter_text.text():
            ok_to_start = ok_to_start and False
            ok_to_test = ok_to_test and False
        if not self.converter_output_path_text.text():
            ok_to_start = ok_to_start and False
        self.converter_start_button.setEnabled(ok_to_start)
        self.converter_test_filter_button.setEnabled(ok_to_test)
        if ok_to_start:
            self.sequence_image_path_text.setText(
                self.converter_input_path_text.text())
            self.sequence_image_filter_text.setText(
                '*.{}'.format(self.converter_output_format_combobox.currentText().lower()))
            log.debug('Updating converter parameters', extra=self.extra)
            self.workers['Converter'].update_parameters(Path(self.converter_input_path_text.text()),
                                                        self.converter_file_filter_text.text(),
                                                        Path(
                                                            self.converter_output_path_text.text()),
                                                        self.converter_output_format_combobox.currentText())
        log.debug('Ready to start the image conversion', extra=self.extra)

    def sequence_test_filter(self):
        """Print the list of files machng the filter condition."""
        self.sequence_get_imagelist(Path(self.sequence_image_path_text.text()),
                                    self.sequence_image_filter_text.text(),
                                    display=True)

    def sequence_open_input_folder(self):
        """Open a file dialog for the sequence output folder."""
        directory = self.sequence_image_path_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getExistingDirectory(
            self, 'Image list folder', directory=directory)
        if returnpath:
            self.sequence_image_path_text.setText(returnpath)
            self.sequence_validate_start()

    def sequence_open_output_file(self):
        """Open a file dialog for the sequence output folder."""
        directory = self.sequence_output_filename_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getSaveFileName(self, 'Output filename for the sequence video',
                                                 filter='Videos (*.mp4)',
                                                 directory=directory)
        if returnpath:
            self.sequence_output_filename_text.setText(returnpath[0])
            self.sequence_validate_start()

    @Slot()
    def sequence_validate_start(self):
        """
        Perform a validation check on the input fieds for the sequence tab.

        The start button becomes enabled only in all fields (input and output path and file filter)
        are valid. No check is perform on the FPS since it is done directly by  the GUI.
        When the start button is enabled, all parameters are transferred to the SequenceWorker
        making it ready for the start.

        The check button is active if input folder and filter are set.

        Note
        ----

        This method is a Qt Slot and it is connected with the editing finished signal of the
        corresponding input filed.

        Returns
        -------
        None.

        """
        ok_to_start = True
        ok_to_test = True
        if not self.sequence_image_path_text.text():
            ok_to_start = ok_to_start and False
            ok_to_test = ok_to_test and False
        if not self.sequence_image_filter_text.text():
            ok_to_start = ok_to_start and False
            ok_to_test = ok_to_test and False
        if not self.sequence_output_filename_text.text():
            ok_to_start = ok_to_start and False
        if self.sequence_output_filename_text.text() and not self.sequence_output_filename_text.text().endswith('.mp4'):
            ok_to_start = ok_to_start and False
            log.warning('Please select a mp4 output file', extra=self.extra)
        self.sequence_start_button.setEnabled(ok_to_start)
        self.sequence_test_filter_button.setEnabled(ok_to_test)

        if ok_to_start:
            log.debug('Updating sequence parameters', extra=self.extra)
            self.workers['Sequence'].update_parameters(Path(self.sequence_image_path_text.text()),
                                                       self.sequence_image_filter_text.text(),
                                                       Path(
                                                           self.sequence_output_filename_text.text()),
                                                       self.sequence_fpb_spin.value())

    def sequence_get_imagelist(self, folder, filefilter, display=False):
        """Print the list of files machng the filter condition."""
        image_list = sorted(list(folder.glob(filefilter)))
        if display:
            log.info('Found a total of %s images in the input folder matching the filter', len(image_list),
                     extra=self.extra)
            for img in image_list:
                log.info(img.name, extra=self.extra)
        return image_list

    def enable_inputs(self, status=True):
        """
        Turn all inputs ON or OFF.

        When a worker start its job, it is better to disable all inputs so that the user is not making any changes.
        This slot is called with status=False when the job starts and with status=True when the job is finished.

        Parameters
        ----------
        status : BOOL, optional
            Switch the inputs on if True or off is False. The default is True.

        Returns
        -------
        None.

        """
        self.tab_moviemaker.setEnabled(status)

    def join_validate_start(self):
        """
        Perform a validation check on the input fieds for the sequence tab.

        The start button becomes enabled only in all fields (input and output path and file filter)
        are valid. No check is perform on the FPS since it is done directly by  the GUI.
        When the start button is enabled, all parameters are transferred to the SequenceWorker
        making it ready for the start.

        The check button is active if input folder and filter are set.

        Note
        ----

        This method is a Qt Slot and it is connected with the editing finished signal of the
        corresponding input filed.

        Returns
        -------
        None.

        """
        ok_to_start = True
        if not self.join_video1_path_text.text():
            ok_to_start = ok_to_start and False
        if not self.join_video2_path_text.text():
            ok_to_start = ok_to_start and False
        if not self.join_outputvideo_path_text.text():
            ok_to_start = ok_to_start and False
        if self.join_outputvideo_path_text.text() and not self.join_outputvideo_path_text.text().endswith('.mp4'):
            ok_to_start = ok_to_start and False
            log.warning('The output file must be an mp4 file',
                        extra=self.extra)
        self.join_start_button.setEnabled(ok_to_start)

        if ok_to_start:
            log.debug('Updating joining parameters', extra=self.extra)
            self.workers['Join'].update_parameters(Path(self.join_video1_path_text.text()),
                                                   Path(
                                                       self.join_video2_path_text.text()),
                                                   Path(self.join_outputvideo_path_text.text()))

    def join_open_video1(self):
        """
        Open a file dialog for the selection of the first video clip file.

        The selection is limited to *.mp4 files because it is the only format accepted so far.

        """
        directory = self.join_video1_path_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getOpenFileName(
            self, 'Select first video to join', filter='Video (*.mp4)', directory=directory)

        if returnpath:
            self.join_video1_path_text.setText(returnpath[0])
            self.join_validate_start()

    def join_open_video2(self):
        """
        Open a file dialog for the selection of the second video clip file.

        The selection is limited to *.mp4 files because it is the only format accepted so far.

        """
        directory = self.join_video2_path_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getOpenFileName(
            self, 'Select second video to join', filter='Video (*.mp4)', directory=directory)
        if returnpath:
            self.join_video2_path_text.setText(returnpath[0])
            self.join_validate_start()

    def join_open_output_video(self):
        """
        Open a file dialog for the selection of the output video clip file.

        The selection is limited to *.mp4 files because it is the only format accepted so far.

        """
        directory = self.join_outputvideo_path_text.text()
        if not directory:
            directory = '.'
        returnpath = QFileDialog.getSaveFileName(
            self, 'Select the output file name', filter='Video (*.mp4)', directory=directory)
        if returnpath:
            self.join_outputvideo_path_text.setText(returnpath[0])
            self.join_validate_start()


def main():
    """
    Start the event loop of the QApplication.

    The main task is to create a QAppliocation and instanciate a
    MovieMakerWindow.

    Minor things:
        1. Adding an AppUserModelID in order to have a nice icon on the taskbar (windows)
        2. Setting a thread name
        3. Setting the log leve.

    Returns
    -------
    None.

    """
    # to set the icon on the window task bar
    myappid = u'ecjrc.moviemaker.gui.v1.0.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # give a name at the main thread
    QtCore.QThread.currentThread().setObjectName('MovieMaker')

    # set the log level
    logging.getLogger().setLevel(logging.INFO)

    # start the Qt App
    app = QApplication(sys.argv)
    win = MovieMakerWindow(app)

    # show the main window
    win.show()

    # execute the main window and eventually exit when done!
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
