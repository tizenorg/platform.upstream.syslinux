# -*- rpm -*-
Summary: Kernel loader which uses a FAT, ext2/3 or iso9660 filesystem or a PXE network
Name: syslinux
Version: 4.04
Release: 1
License: GPLv2
Url: http://syslinux.zytor.com/
Group: System/Boot
Source0: ftp://ftp.kernel.org/pub/linux/utils/boot/syslinux/%{name}-%{version}.tar.gz
ExclusiveArch: %{ix86} x86_64
Buildroot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: nasm >= 0.98.39, perl
Source101: syslinux-rpmlintrc
Source1001: packaging/syslinux.manifest 
# >> gbp-patch-tags         # auto-added by gbp
Patch0:    0001-btrfs-Correctly-determine-the-installation-subvolume.patch
# << gbp-patch-tags         # auto-added by gbp

Autoreq: 0
%ifarch x86_64
Requires: mtools
%define my_cc gcc
%else
Requires: mtools, libc.so.6
%define my_cc gcc -m32
%endif

# NOTE: extlinux belongs in /sbin, not in /usr/sbin, since it is typically
# a system bootloader, and may be necessary for system recovery.
%define _sbindir /sbin

%description
SYSLINUX is a suite of bootloaders, currently supporting DOS FAT
filesystems, Linux ext2/ext3 filesystems (EXTLINUX), PXE network boots
(PXELINUX), or ISO 9660 CD-ROMs (ISOLINUX).  It also includes a tool,
MEMDISK, which loads legacy operating systems from these media.

%package devel
Summary: Development environment for SYSLINUX add-on modules
Group: Development/Libraries
Requires: syslinux

%description devel
The SYSLINUX boot loader contains an API, called COM32, for writing
sophisticated add-on modules.  This package contains the libraries
necessary to compile such modules.

%package extlinux
Summary: The EXTLINUX bootloader, for booting the local system
Group: System/Boot
Requires: syslinux

%description extlinux
The EXTLINUX bootloader, for booting the local system, as well as all
the SYSLINUX/PXELINUX modules in /boot.

%package tftpboot
Summary: SYSLINUX modules in /var/lib/tftpboot, available for network booting
Group: Applications/Internet
Requires: syslinux

%description tftpboot
All the SYSLINUX/PXELINUX modules directly available for network
booting in the /var/lib/tftpboot directory.

%prep
%setup -q -n syslinux-%{version}

# >> gbp-apply-patches    # auto-added by gbp
%patch0 -p1
# << gbp-apply-patches    # auto-added by gbp

%build
cp %{SOURCE1001} .
make CC='%{my_cc}' clean
make CC='%{my_cc}' installer
make CC='%{my_cc}' -C sample tidy

%install
rm -rf %{buildroot}
make CC='%{my_cc}' install-all \
	INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=%{_sbindir} \
	LIBDIR=%{_libdir} DATADIR=%{_datadir} \
	MANDIR=%{_mandir} INCDIR=%{_includedir} \
	TFTPBOOT=/var/lib/tftpboot EXTLINUXDIR=/boot/extlinux
make CC='%{my_cc}' -C sample tidy

%clean
rm -rf %{buildroot}

%files
%manifest syslinux.manifest
%defattr(-,root,root)
%{_bindir}/*
%dir %{_datadir}/syslinux
%{_datadir}/syslinux/*.com
%{_datadir}/syslinux/*.exe
%{_datadir}/syslinux/*.c32
%{_datadir}/syslinux/*.bin
%{_datadir}/syslinux/*.0
%{_datadir}/syslinux/memdisk
%{_datadir}/syslinux/dosutil

%files devel
%manifest syslinux.manifest
%defattr(-,root,root)
%doc COPYING NEWS README doc/*
%doc sample
%doc %{_mandir}/man*/*
%{_datadir}/syslinux/com32
%{_datadir}/syslinux/diag

%files extlinux
%manifest syslinux.manifest
%defattr(-,root,root)
%{_sbindir}/extlinux
/boot/extlinux

%files tftpboot
%manifest syslinux.manifest
%defattr(-,root,root)
/var/lib/tftpboot

%post extlinux
# If we have a /boot/extlinux.conf file, assume extlinux is our bootloader
# and update it.
if [ -f /boot/extlinux/extlinux.conf ]; then \
	ln -sf /boot/extlinux/extlinux.conf /etc/extlinux.conf; \
	extlinux --update /boot/extlinux ; \
elif [ -f /boot/extlinux.conf ]; then \
	mkdir -p /boot/extlinux && \
	mv /boot/extlinux.conf /boot/extlinux/extlinux.conf && \
	extlinux --update /boot/extlinux ; \
fi
