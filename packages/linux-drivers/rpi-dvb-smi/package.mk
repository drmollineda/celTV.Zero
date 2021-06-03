# SPDX-License-Identifier: GPL-2.0
# Copyright (C) 2021-present David R. Mollineda <drmollineda@uclv.cu>

PKG_NAME="rpi-dvb-smi"
PKG_VERSION="master"
PKG_ARCH="arm"
PKG_LICENSE="GPL"
PKG_DEPENDS_TARGET="toolchain linux"
PKG_NEED_UNPACK="$LINUX_DEPENDS"
PKG_LONGDESC="Kernel modules for Raspberry Pi-based DTMB TV box"
PKG_IS_KERNEL_PKG="yes"

pre_make_target() {
        unset LDFLAGS
}

make_target() {
        make KDIR=$(kernel_path)
}

makeinstall_target() {
        mkdir -p $INSTALL/usr/lib/modules/$(get_module_dir)/$PKG_NAME
          cp *.ko $INSTALL/usr/lib/modules/$(get_module_dir)/$PGK_NAME
}
