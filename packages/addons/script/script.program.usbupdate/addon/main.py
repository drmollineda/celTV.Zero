# -*- coding: utf-8 -*-

import os
import xbmcgui


def main():
    d = xbmcgui.Dialog()
    filepath = d.browseSingle(1, 'Seleccione el fichero para actualizar', 'files', '.tar|.tar.gz', defaultt='')

    if not filepath:
        return

    p = xbmcgui.DialogProgress()
    p.create('Actualizar', 'Copiando fichero')

    chunk_size = 1 << 19

    total = os.stat(filepath).st_size
    reads = 0

    with open(filepath, 'rb') as src:
        with open('/storage/.update/blob.tar', 'wb') as dst:
            chunk = src.read(chunk_size)

            while chunk and not p.iscanceled():
                dst.write(chunk)
                reads += len(chunk)
                
                p.update((reads * 100) / total, 'Actualizar', 'Copiando fichero')
                chunk = src.read(chunk_size)
                
    if p.iscanceled():
        os.system('rm -r /storage/.update')
    else:
        d.ok('Actualizar', 'Reiniciaremos el dispositivo para actualizar')
        os.system('reboot now')


if __name__ == '__main__':
    main()
