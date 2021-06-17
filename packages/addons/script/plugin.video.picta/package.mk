# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2009-2016 Stephan Raue (stephan@openelec.tv)
# Copyright (C) 2019-2021 Team LibreELEC (https://libreelec.tv)
# Copyright (C) 2021-present David R. Mollineda (darmollineda@uclv.cu)

PKG_NAME="plugin.video.picta"
PKG_VERSION="master"
PKG_ARCH="any"
PKG_LICENSE="OSS"
PKG_SITE="https://github.com/crmartinez930130/plugin.video.picta"
PKG_URL="https://nube.uclv.cu/index.php/s/wmij3XXsgwFG5iX/download/plugin.video.picta-$PKG_VERSION.tar.gz"
PKG_SHORTDESC="plugin.video.picta"
PKG_LONGDESC="plugin.video.picta"
PKG_TOOLCHAIN="manual"

PKG_ADDON_NAME="Picta"
PKG_ADDON_TYPE="xbmc.python.pluginsource"
PKG_IS_ADDON="embedded"

unpack() {
	mkdir -p $PKG_BUILD/addon
	tar --strip-components=1 -xf $SOURCES/$PKG_NAME/$PKG_NAME-$PKG_VERSION.tar.gz -C $PKG_BUILD/addon
}

make_target() {
	:
}

makeinstall_target() {
	mkdir -p $INSTALL/usr/share/kodi/addons/${PKG_NAME}
	cp -rP $PKG_BUILD/addon/* $INSTALL/usr/share/kodi/addons/${PKG_NAME}
}
