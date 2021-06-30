import subprocess
import re

from threading import Thread, Lock

import xbmc
from xbmcgui import WindowXMLDialog, Dialog

from contextlib import contextmanager
from api import Api
from time import sleep

class AppState(object):
    def __init__(self):
        self.selected_scan = -1


match = re.compile('\\d+\\.\\d+%')


class SignalMonitor(Thread):
    def __init__(self, receiver, api=Api()):
        super(SignalMonitor, self).__init__()
        self.receiver = receiver
        self.api = api

    def run(self):
        while True:
            data = self.api.status.query(action='inputs')()['entries'][0]

            signal = float(data['signal']) / 65535 * 100
            qualty = float(data['snr']) / 65535 * 100

            if not self.receiver.send_stats(signal, qualty):
                break

            sleep(1)


class ScanProgressWindow(WindowXMLDialog):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
       super(ScanProgressWindow, self).__init__(xmlFilename, scriptPath, *args, **kwargs)
       self.signal_monitor = SignalMonitor(self)
       self.scanner = kwargs['scanner']
       self.scanner.set_progress_listener(self)
       self.started = False

    def onInit(self):
        self.intensity_meter = self.getControl(108)
        self.snquality_meter = self.getControl(109)

        self.progress_label = self.getControl(112)
        self.progress_bar = self.getControl(113)

        self.start_button = self.getControl(110)

        self.signal_monitor.start()

    def onClick(self, control_id):
        if control_id is 110:
            if self.started:
                self.no_cancel()
                self.scanner.stop()
            else:
                self.started = True
                self.scanner.start()
                self.start_button.setLabel('Cancelar')

    def send(self, progress, info):
        self.progress_bar.setPercent(int(progress))
        self.progress_label.setLabel(info)

    def no_cancel(self):
        self.start_button.setLabel('Espere...')
        self.start_button.setEnabled(False)

    def send_stats(self, signal_intensity, signal_quality):
        if self.scanner.active():
            self.intensity_meter.setPercent(int(signal_intensity))
            self.snquality_meter.setPercent(int(signal_quality))
            return True
        else:
            return False


class ScanSelectWindow(WindowXMLDialog):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(ScanSelectWindow, self).__init__(xmlFilename, scriptPath, *args, **kwargs)
        self.app = kwargs['app']
        self.descriptions = {
            102: 'Escanear el rango completo de canales en busca de servicios de TV Digital y Radio',
            103: 'Escanear un rango de canales en busca de servicios de TV Digital y Radio',
            104: 'Escanear el canal elegido en busca de servicios de TV Digital y Radio'
        }

        self.finisher = False

    def update(self, signal, qualty):
        self.signalBar.setPercent(int(signal))
        self.qualtyBar.setPercent(int(qualty))

    def onFocus(self, control_id):
        try:
            self.getControl(5).setLabel(self.descriptions[control_id])
        except KeyError:
            pass

    def onClick(self, control_id):
        if control_id in range(102, 105):
            self.app.selected_scan = control_id - 102
            self.close()


def __input_loop(dialog, base_value=''):
    do_loop = True

    while do_loop:
        try:
            value = int(dialog.numeric(0, 'Canal (7 - 51)', str(base_value)))
        except ValueError:
            value = -1

        if value is -1 or value in range(7, 52):
            do_loop = False
        else:
            dialog.ok('Error', 'Los canales deben estar en el rango de 7 a 51')
    else:
        return value


def select_span():
    dialog = Dialog()

    a = __input_loop(dialog)

    if a is -1:
        return (-1, -1)

    b = __input_loop(dialog)

    start = a if a < b else b
    final = a if a > b else b

    return (start, final)


def select_pick():
    dialog = Dialog()
    return __input_loop(dialog)


@contextmanager
def busy():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
