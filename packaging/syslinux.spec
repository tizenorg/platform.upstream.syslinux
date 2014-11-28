# -*- rpm -*-
Summary: Kernel loader which uses a FAT, ext2/3 or iso9660 filesystem or a PXE network
Name: syslinux
Version: 6.03
Release: 0
License: GPL-2.0
Url: http://syslinux.zytor.com/
#X-Vc-Url: git://git.kernel.org/pub/scm/boot/syslinux/syslinux.git
Group: System/Other
Source0: ftp://ftp.kernel.org/pub/linux/utils/boot/syslinux/%{name}-%{version}.tar.gz
Source1001: packaging/syslinux.manifest
Source10: gnu-efi.tar.bz2

ExclusiveArch: %{ix86} x86_64
BuildRequires: nasm >= 0.98.39, perl
BuildRequires: python
BuildRequires: libuuid-devel
BuildRequires: git
Requires: mtools

%ifarch x86_64
BuildRequires: glibc-devel-32bit, gcc-32bit, libgcc_s1-32bit
%define my_cc gcc -Wno-sizeof-pointer-memaccess
%else
Autoreq: 0
Requires: libc.so.6
%define my_cc gcc -m32 -Wno-sizeof-pointer-memaccess
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
Group: System/Other
Requires: syslinux

%description devel
The SYSLINUX boot loader contains an API, called COM32, for writing
sophisticated add-on modules.  This package contains the libraries
necessary to compile such modules.

%package extlinux
Summary: The EXTLINUX bootloader, for booting the local system
Group: System/Other
Requires: syslinux

%description extlinux
The EXTLINUX bootloader, for booting the local system, as well as all
the SYSLINUX/PXELINUX modules in /boot.

%package tftpboot
Summary: SYSLINUX modules in /var/lib/tftpboot, available for network booting
Group: System/Other
Requires: syslinux

%description tftpboot
All the SYSLINUX/PXELINUX modules directly available for network
booting in the /var/lib/tftpboot directory.

%prep
%setup -q -a 10 -n %{name}-%{version}

%build
cp %{SOURCE1001} .
%define make %__make CC='%{my_cc}' OPTFLAGS="-DDEBUG=1 -O0" HEXDATE='0x00000000'


%make bios clean
%make bios spotless
%make bios all

%ifarch x86_64
echo "TODO: regenerate 32bit sources for {ext,*}linux installers"
ORIG_CFLAGS="${CFLAGS}"
CFLAGS="-m32"
export CFLAGS

%define my_cc gcc -m32 -Wno-sizeof-pointer-memaccess -march=i686 -mtune=i686 -funwind-tables
%define make %__make CC='%{my_cc}' OPTFLAGS="-DDEBUG=1 -O0" HEXDATE='0x00000000'

rm -rfv bios/extlinux bios/libinstaller bios/com32 bios/core bios/linux

%{my_cc} -v
nasm -v

%make bios all V=1 || echo "ignore: expected to fail, checking file:"
grep len ./bios/libinstaller/ldlinuxc32_bin.c

echo "TODO: rebuild x64 utilities with 32bit generated sources"
CFLAGS="${ORIG_CFLAGS}"
export CFLAGS
%define make %__make CC='gcc' HEXDATE='0x00000000'

rm -rfv \
  bios/*/ldlinuxc32_bin.o \
  bios/extlinux/*.o

%make bios all -k V=1
%endif


%install

%make \
	bios install-all \
	INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=%{_sbindir} \
	LIBDIR=%{_libdir} DATADIR=%{_datadir} \
	MANDIR=%{_mandir} INCDIR=%{_includedir} \
	TFTPBOOT=/var/lib/tftpboot EXTLINUXDIR=/boot/extlinux

%clean
rm -rf %{buildroot}

%files
%manifest syslinux.manifest
%defattr(-,root,root)
%{_bindir}/*
%dir %{_datadir}/syslinux
%{_datadir}/syslinux/*.com
%{_datadir}/syslinux/*.c32
%{_datadir}/syslinux/*.bin
%{_datadir}/syslinux/*.0
%{_datadir}/syslinux/memdisk
%{_datadir}/syslinux/dosutil
%license COPYING

%files devel
%manifest syslinux.manifest
%defattr(-,root,root)
%license COPYING doc/logo/LICENSE
%doc NEWS README doc/*
%doc sample
%doc %{_mandir}/man*/*
%{_datadir}/syslinux/com32
%{_datadir}/syslinux/diag

%files extlinux
%manifest syslinux.manifest
%defattr(-,root,root)
%license COPYING
%{_sbindir}/extlinux
/boot/extlinux

%files tftpboot
%manifest syslinux.manifest
%defattr(-,root,root)
%license COPYING
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
