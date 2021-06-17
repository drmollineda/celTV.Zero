# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import string
import json
import xml.etree.ElementTree as ET

import xbmcaddon
import xbmcgui
import xbmc

from lib.ui import TopWindow, LevelTwoWindow, LevelThreeWindow
from lib.parse import build_page_model_from_file, BASE_DIRS


def create_background_image(cur, background):
    path_to_original_background = os.path.join(BASE_DIRS, background)
    path_to_textured_background = os.path.join(BASE_DIRS, '%s.png' % background)

    try:
        sys.path.extend([os.path.join(cur, 'bin'), os.path.join(cur, 'lib')])
        xbmc.log(str(sys.path), xbmc.LOGWARNING)
        subprocess.call(['ffmpeg', '-i', path_to_original_background, path_to_textured_background])
    except Exception as e:
        print e

    return path_to_textured_background


if __name__ == '__main__':
    
    try:
        data_page = sys.argv[1]
    except:
        data_page = '0_index.xml'

    if not os.path.exists(os.path.join(BASE_DIRS, data_page)):
        xbmc.executebuiltin("Notification(Servicios, Sin datos)")
    else:
        model = build_page_model_from_file(data_page)

        cur = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8')
        
        layout_router = [(TopWindow, 'main-level-alternative.xml'), (LevelTwoWindow, 'list-level.xml'), (LevelThreeWindow, 'detail-level.xml')]
        layout_class, layout_file = layout_router[model['type']]

        model['dbc_background'] = create_background_image(cur, model['dbc_background'])

        layout = layout_class(layout_file, cur, 'default', '720p', model=model)

        layout.doModal()
        del layout
