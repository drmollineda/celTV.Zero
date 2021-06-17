# -*- coding: utf-8 -*-

import xbmc
import xbmcgui
import xbmcaddon

from datetime import date


WEEKDAY_NAMES = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo',]
NAME_X_MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
ID = xbmcaddon.Addon().getAddonInfo('id')


def build_date_string(date):
    return '%s %d/%d/%d' % (WEEKDAY_NAMES[date.weekday()].upper(), date.day, date.month, date.year)


def jump_to_content(content):
    xbmc.executebuiltin('RunScript(%s, %s)' % (ID, content))


class AppWindow(xbmcgui.WindowXML):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(AppWindow, self).__init__(xmlFilename, scriptPath, *args, **kwargs)
        self.model = kwargs['model']

    def onInit(self):
        self.setProperty('dbc_hint', self.model['dbc_hint'])
        self.setProperty('dbc_background', self.model['dbc_background'])
        self.setProperty('dbc_top_header', self.model['dbc_top_header'])

        self.setProperty('dbc_datetime', build_date_string(date.today()))


class TopWindow(AppWindow):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(TopWindow, self).__init__(xmlFilename, scriptPath, *args, **kwargs)

    def onInit(self):
        super(TopWindow, self).onInit()

        widget_list = self.getControl(100)
        widget_list.reset()
        
        item_list = []
        for item_dict in self.model['items']:
            item = xbmcgui.ListItem()

            for prop, value in item_dict.items():
                item.setProperty(prop, value)

            item_list.append(item)

        widget_list.addItems(item_list)
        self.setFocusId(100)

    def onClick(self, control_id):
        if control_id is 100:
            href = self.getControl(100).getSelectedItem().getProperty('href')
            jump_to_content(href)


class LevelTwoWindow(AppWindow):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(LevelTwoWindow, self).__init__(xmlFilename, scriptPath, *args, **kwargs)

    def onInit(self):
        super(LevelTwoWindow, self).onInit()

        widget_strip = self.getControl(100)
        item_list = []

        for index, info_class in enumerate(self.model['items']):
            item = xbmcgui.ListItem(label=info_class['title'])
            item.setProperty('mode', info_class['mode'])
            item.setProperty('index', str(index))

            item_list.append(item)

        widget_strip.addItems(item_list)

        widget_strip.selectItem(0)
        self.update_page()

    def update_page(self, selected_tab=None):
        if selected_tab is None:
            widget_strip = self.getControl(100)
            selected_tab = widget_strip.getSelectedItem()

        self.setProperty('selectedTab', selected_tab.getProperty('index'))
        source = self.model['items'][int(selected_tab.getProperty('index'))]

        if selected_tab.getProperty('mode') == 'list':
            item_list = []
            widget_list = self.getControl(111)
            widget_list.reset()

            for index, info in enumerate(source['values']):
                item = xbmcgui.ListItem(label=info['title'].lstrip())
                item.setProperty('href', info['href'])
                item.setProperty('index', str(index))

                item_list.append(item)

            widget_list.addItems(item_list)
            self.setFocusId(111)
        else:
            header_row = self.getControl(121)
            widget_list = self.getControl(122)
            widget_list.reset()

            header_row.setLabel(' | '.join(header.rjust(width) for header, width in zip(source['headers'], source['widths'])))
            item_list = []

            for info in source['values']:
                item = xbmcgui.ListItem(label='   '.join((value or '').rjust(width) for value, width in zip(info, source['widths'])))
                item_list.append(item)

            widget_list.addItems(item_list)
            self.setFocusId(122)

    def onAction(self, action_object):
        focused_control = self.getFocusId()

        if focused_control not in (111, 122):
            if self.getControl(111).isVisible():
                self.setFocusId(111)
            elif self.getControl(122).isVisible():
                self.setFocusId(122)

        widget_strip = self.getControl(100)
        selected = int(widget_strip.getSelectedItem().getProperty('index'))
        action_id = action_object.getId()

        if action_id not in (1, 2):
            return super(LevelTwoWindow, self).onAction(action_object)

        offset = -1 if action_id is 1 else 1
        next_select = selected + offset if selected + offset in range(0, len(self.model['items'])) else selected

        if next_select != selected:
            widget_strip.selectItem(next_select)
            self.update_page(widget_strip.getListItem(next_select))

    def onClick(self, control_id):
        if control_id is 111:
            item = self.getControl(control_id).getSelectedItem().getProperty('href')
            jump_to_content(item)


class LevelThreeWindow(AppWindow):
    def __init__(self, xmlFilename, scriptPath, *args, **kwargs):
        super(LevelThreeWindow, self).__init__(xmlFilename, scriptPath, *args, **kwargs)

    def onInit(self):
        super(LevelThreeWindow, self).onInit()

        try:
            self.setProperty('image', self.model['image'])
        except:
            pass

        self.setProperty('title', self.model['title'])
        self.setProperty('text', self.model['text'] if 'text' in self.model else '')

        if 'table' in self.model:
            self.setProperty('table', 'yes')

            source = self.model['table']
            xbmc.log('source = %s' % source, xbmc.LOGNOTICE)

            header_row = self.getControl(121)
            widget_list = self.getControl(122)
            widget_list.reset()

            header_row.setLabel(' | '.join(header.rjust(width) for header, width in zip(source['headers'], source['widths'])))
            item_list = []

            for info in source['values']:
                item = xbmcgui.ListItem(label='   '.join((value or '').rjust(width) for value, width in zip(info, source['widths'])))
                item_list.append(item)

            widget_list.addItems(item_list)

        for kind in ('text', 'image', 'table'):
            if kind in self.model and self.model[kind]:
                self.setProperty('selected', kind)
                break
