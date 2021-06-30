import xbmcaddon
import xbmc

from xbmcgui import WindowXMLDialog, Dialog

from lib.scan import ChannelScanner
from lib.ui import AppState, ScanSelectWindow, ScanProgressWindow, busy, select_span, select_pick

from time import sleep
from json import dumps, loads


def build_rpc_cmd(_cmd, **params):
    return dumps({ 'jsonrpc': '2.0', 'method': _cmd, 'params': params, 'id': 1 })


def refresh_channel_numbers():
    cmd_off = build_rpc_cmd('Settings.SetSettingValue', setting='pvrmanager.usebackendchannelnumbers', value=False)
    cmd__on = build_rpc_cmd('Settings.SetSettingValue', setting='pvrmanager.usebackendchannelnumbers', value=True)

    xbmc.executeJSONRPC(cmd_off)
    sleep(1)
    xbmc.executeJSONRPC(cmd__on)


def full_scan():
    return ChannelScanner(7, 51)


def span_scan():
    span_start, span_end = select_span()

    return ChannelScanner(span_start, span_end) if span_start > 0 else None


def pick_scan():
    channel = select_pick()
    return ChannelScanner(channel, channel) if channel > 0 else None


if __name__ == '__main__':
    app = AppState()

    cwd = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8')
    window = ScanSelectWindow('scan-select.xml', cwd, 'default', '720p', app=app)
    window.doModal()
    del window

    player = xbmc.Player()

    if player.isPlaying():
        player.stop()

    variants = [full_scan, span_scan, pick_scan, lambda: None]
    scanner = variants[app.selected_scan]()

    success = False

    if scanner is not None:
        scan_window = ScanProgressWindow('scan-progress.xml', cwd, 'default', '720p', scanner=scanner)
        scan_window.doModal()
        del scan_window

        success = scanner.succeeded
        scanner.stop()

    if success:
        refresh_channel_numbers()
        xbmc.executebuiltin('ActivateWindow(10700)')
