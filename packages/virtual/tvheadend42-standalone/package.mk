################################################################################
#      This file is part of LibreELEC - https://libreelec.tv
#      Copyright (C) 2016-present Team LibreELEC
#
#  LibreELEC is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  LibreELEC is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with LibreELEC.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

PKG_NAME="tvheadend42-standalone"
PKG_VERSION="1.0.0"
PKG_ARCH="any"
PKG_LICENSE="GPL"
PKG_SITE=""
PKG_URL=""
PKG_DEPENDS_TARGET="toolchain tvheadend42"
PKG_SHORTDESC="Tvheadend: a TV streaming server for Linux"
PKG_LONGDESC="Tvheadend ($PKG_VERSION_NUMBER): is a TV streaming server for Linux supporting DVB-S/S2, DVB-C, DVB-T/T2, IPTV, SAT>IP, ATSC and ISDB-T"
PKG_TOOLCHAIN="manual"

make_target() {
  :
}

makeinstall_target() {
  mkdir -p $INSTALL/usr/share/tvheadend/bin
  cp -P $(get_build_dir tvheadend42)/build.linux/tvheadend $INSTALL/usr/share/tvheadend/bin
  cp -P $(get_build_dir tvheadend42)/capmt_ca.so $INSTALL/usr/share/tvheadend/bin

  cp -rfP $PKG_DIR/source/* $INSTALL/usr/share/tvheadend/
  chmod +x $INSTALL/usr/share/tvheadend/bin/*
}

post_install() {
  enable_service tvheadend42.service
}
