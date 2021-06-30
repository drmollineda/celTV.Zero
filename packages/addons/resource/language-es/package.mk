# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2016-2018 Team LibreELEC (https://libreelec.tv)
# Copyright (C) 2018-present David R. Mollineda (drmollineda@gmail.com)

PKG_NAME="language-es"
PKG_VERSION="1.0.0"
PKG_ARCH="any"
PKG_LICENSE="GPL"
PKG_SECTION="resource"
PKG_SHORTDESC="resource.language.es_es"
PKG_LONGDESC="Spanish language addon"
PKG_TOOLCHAIN="manual"

PKG_IS_ADDON="embedded"
PKG_ADDON_NAME="Spanish Locale Info"

make_target() {
	:
}

makeinstall_target() {
	mkdir -p $INSTALL/usr/share/kodi/addons/resource.language.es_es
	cp -rP $PKG_DIR/addon/* $INSTALL/usr/share/kodi/addons/resource.language.es_es
}
