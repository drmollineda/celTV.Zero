# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2016-2018 Team LibreELEC (https://libreelec.tv)
# Copyright (C) 2018-present David R. Mollineda (drmollineda@gmail.com)

PKG_NAME="script.program.channelscanner"
PKG_VERSION="1.0.0"
PKG_ARCH="any"
PKG_LICENSE="GPL"
PKG_SECTION="script.program"
PKG_SHORTDESC="script.program.channelscanner"
PKG_LONGDESC="Frontend for TVHeadend Service Scanning"
PKG_TOOLCHAIN="manual"

PKG_IS_ADDON="embedded"
PKG_ADDON_NAME="TV - Escanear canales"
PKG_ADDON_TYPE="xbmc.python.script"

make_target() {
	:
}

makeinstall_target() {
	mkdir -p $INSTALL/usr/share/kodi/addons/${PKG_NAME}
	cp -rP $PKG_DIR/addon/* $INSTALL/usr/share/kodi/addons/${PKG_NAME}
}
