# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2016-2018 Team LibreELEC (https://libreelec.tv)
# Copyright (C) 2018-present David R. Mollineda (drmollineda@gmail.com)

PKG_NAME="script.program.databroadcast"
PKG_VERSION="1.0.0"
PKG_ARCH="any"
PKG_LICENSE="GPL"
PKG_SECTION="script.program"
PKG_SHORTDESC="script.program.databroadcast"
PKG_LONGDESC="Frontend for Data Broadcast Service"
PKG_DEPENDS_TARGET="toolchain ffmpegx"
PKG_TOOLCHAIN="manual"

PKG_IS_ADDON="embedded"
PKG_ADDON_NAME="TV - Servicios"
PKG_ADDON_TYPE="xbmc.python.script"

make_target() {
	:
}

makeinstall_target() {
	mkdir -p $INSTALL/usr/share/kodi/addons/${PKG_NAME}
	cp -rP $PKG_DIR/addon/* $INSTALL/usr/share/kodi/addons/${PKG_NAME}

	mkdir -p $INSTALL/usr/share/kodi/addons/${PKG_NAME}/bin
	cp -L $(get_build_dir ffmpegx)/.INSTALL_PKG/usr/local/bin/* $INSTALL/usr/share/kodi/addons/${PKG_NAME}/bin
}
