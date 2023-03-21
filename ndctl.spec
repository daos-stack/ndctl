Name:		ndctl
Version:	76.1
Release:	1%{?dist}
Summary:	Manage "libnvdimm" subsystem devices (Non-volatile Memory)
License:	GPLv2
Group:		System Environment/Base
Url:		https://github.com/pmem/ndctl
Source0:	https://github.com/pmem/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

Requires:	ndctl-libs%{?_isa} = %{version}-%{release}
Requires:	daxctl-libs%{?_isa} = %{version}-%{release}
Requires:	cxl-libs%{?_isa} = %{version}-%{release}
BuildRequires:	autoconf
%if 0%{?rhel} < 9
BuildRequires:	asciidoc
%define asciidoctor -Dasciidoctor=disabled
%define libtracefs -Dlibtracefs=disabled
%else
BuildRequires:	rubygem-asciidoctor
BuildRequires:	libtraceevent-devel
BuildRequires:	libtracefs-devel
%define asciidoctor -Dasciidoctor=enabled
%define libtracefs -Dlibtracefs=enabled
%endif
BuildRequires:	xmlto
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	pkgconfig
BuildRequires:	pkgconfig(libkmod)
BuildRequires:	pkgconfig(libudev)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	pkgconfig(json-c)
BuildRequires:	pkgconfig(bash-completion)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	keyutils-libs-devel
BuildRequires:	systemd-rpm-macros
BuildRequires:	iniparser-devel
BuildRequires:	meson

%description
Utility library for managing the "libnvdimm" subsystem.  The "libnvdimm"
subsystem defines a kernel device model and control message interface for
platform NVDIMM resources like those defined by the ACPI 6+ NFIT (NVDIMM
Firmware Interface Table).

%if 0%{?flatpak}
%global _udevrulesdir %{_prefix}/lib/udev/rules.d
%endif

%package -n ndctl-devel
Summary:	Development files for libndctl
License:	LGPLv2
Group:		Development/Libraries
Requires:	ndctl-libs%{?_isa} = %{version}-%{release}

%description -n ndctl-devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package -n ndctl-libs
Summary:	Management library for "libnvdimm" subsystem devices (Non-volatile Memory)
License:	LGPLv2
Group:		System Environment/Libraries
Requires:	daxctl-libs%{?_isa} = %{version}-%{release}

%description -n ndctl-libs
Libraries for %{name}.

%package -n daxctl
Summary:	Manage Device-DAX instances
License:	GPLv2
Group:		System Environment/Base
Requires:	daxctl-libs%{?_isa} = %{version}-%{release}

%description -n daxctl
The daxctl utility provides enumeration and provisioning commands for
the Linux kernel Device-DAX facility. This facility enables DAX mappings
of performance / feature differentiated memory without need of a
filesystem.

%package -n daxctl-devel
Summary:	Development files for libdaxctl
License:	LGPLv2
Group:		Development/Libraries
Requires:	daxctl-libs%{?_isa} = %{version}-%{release}

%description -n daxctl-devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}, a library for enumerating
"Device DAX" devices.  Device DAX is a facility for establishing DAX
mappings of performance / feature-differentiated memory.

%package -n daxctl-libs
Summary:	Management library for "Device DAX" devices
License:	LGPLv2
Group:		System Environment/Libraries

%description -n daxctl-libs
Device DAX is a facility for establishing DAX mappings of performance /
feature-differentiated memory. daxctl-libs provides an enumeration /
control API for these devices.

%package -n cxl-cli
Summary:	Manage CXL devices
License:	GPLv2
Requires:	cxl-libs%{?_isa} = %{version}-%{release}

%description -n cxl-cli
The cxl utility provides enumeration and provisioning commands for
the Linux kernel CXL devices.

%package -n cxl-devel
Summary:	Development files for libcxl
License:	LGPLv2
Requires:	cxl-libs%{?_isa} = %{version}-%{release}

%description -n cxl-devel
This package contains libraries and header files for developing applications
that use libcxl, a library for enumerating and communicating with CXL devices.

%package -n cxl-libs
Summary:	Management library for CXL devices
License:	LGPLv2

%description -n cxl-libs
libcxl is a library for enumerating and communicating with CXL devices.


%prep
%setup -q ndctl-%{version}

%build
%meson %{?asciidoctor} %{?libtracefs} -Dversion-tag=%{version}
%meson_build
%install
%meson_install
%check
%meson_test
%ldconfig_scriptlets -n ndctl-libs

%ldconfig_scriptlets -n daxctl-libs

%define bashcompdir %(pkg-config --variable=completionsdir bash-completion)

%pre
if [ -f %{_sysconfdir}/ndctl/monitor.conf ] ; then
  if ! [ -f %{_sysconfdir}/ndctl.conf.d/monitor.conf ] ; then
    cp -a %{_sysconfdir}/ndctl/monitor.conf /var/run/ndctl-monitor.conf-migration
  fi
fi

%post
if [ -f /var/run/ndctl-monitor.conf-migration ] ; then
  config_found=false
  while read line ; do
    [ -n "$line" ] || continue
    case "$line" in
      \#*) continue ;;
    esac
    config_found=true
    break
  done < /var/run/ndctl-monitor.conf-migration
  if $config_found ; then
    echo "[monitor]" > %{_sysconfdir}/ndctl.conf.d/monitor.conf
    cat /var/run/ndctl-monitor.conf-migration >> %{_sysconfdir}/ndctl.conf.d/monitor.conf
  fi
  rm /var/run/ndctl-monitor.conf-migration
fi

%files
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/ndctl
%{_mandir}/man1/ndctl*
%{bashcompdir}/ndctl
%{_unitdir}/ndctl-monitor.service

%dir %{_sysconfdir}/ndctl
%dir %{_sysconfdir}/ndctl/keys
%{_sysconfdir}/ndctl/keys/keys.readme

%{_sysconfdir}/modprobe.d/nvdimm-security.conf

%dir %{_sysconfdir}/ndctl.conf.d
%config(noreplace) %{_sysconfdir}/ndctl.conf.d/monitor.conf
%config(noreplace) %{_sysconfdir}/ndctl.conf.d/ndctl.conf

%files -n ndctl-devel
%license LICENSES/preferred/LGPL-2.1
%{_includedir}/ndctl/
%{_libdir}/libndctl.so
%{_libdir}/pkgconfig/libndctl.pc

%files -n ndctl-libs
%doc README.md
%license LICENSES/preferred/LGPL-2.1 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_libdir}/libndctl.so.*

%files -n daxctl
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/daxctl
%{_mandir}/man1/daxctl*
%{_datadir}/daxctl
%{bashcompdir}/daxctl
%{_unitdir}/daxdev-reconfigure@.service
%config %{_udevrulesdir}/90-daxctl-device.rules
%dir %{_sysconfdir}/daxctl.conf.d/
%config(noreplace) %{_sysconfdir}/daxctl.conf.d/daxctl.example.conf

%files -n daxctl-devel
%license LICENSES/preferred/LGPL-2.1
%{_includedir}/daxctl/
%{_libdir}/libdaxctl.so
%{_libdir}/pkgconfig/libdaxctl.pc

%files -n daxctl-libs
%doc README.md
%license LICENSES/preferred/LGPL-2.1 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_libdir}/libdaxctl.so.*

%files -n cxl-cli
%license LICENSES/preferred/GPL-2.0 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_bindir}/cxl
%{_mandir}/man1/cxl*
%{bashcompdir}/cxl
%{_unitdir}/cxl-monitor.service

%files -n cxl-devel
%license LICENSES/preferred/LGPL-2.1
%{_includedir}/cxl/
%{_libdir}/libcxl.so
%{_libdir}/pkgconfig/libcxl.pc
%{_mandir}/man3/cxl*
%{_mandir}/man3/libcxl.3*

%files -n cxl-libs
%doc README.md
%license LICENSES/preferred/LGPL-2.1 LICENSES/other/MIT LICENSES/other/CC0-1.0
%{_libdir}/libcxl.so.*


%changelog
* Mon Mar 20 2023 Tom Nabarro <tom.nabarro@intel.com> - 76.1-1
- Bump version to v76.1

* Tue Jun 14 2022 Jeff Moyer <jmoyer@redhat.com> - 71.1-4.el8
- Pull in fixes from upstream v72 and v73 (Jeff Moyer)
  - Fix enable-namespace all reporting errors incorrectly
  - Add support for inject-smart on papr scm
- Related: bz#2090190 bz#1986185 bz#2040074

* Mon Nov 29 2021 Bryan Gurney <bgurney@redhat.com> - 71.1-3.el8
- Rebuild with latest json-c version
- Related: bz#2021816

* Thu Feb 11 2021 Jeff Moyer <jmoyer@redhat.com> - 71.1-2.el8
- Get rid of confusing message when deleting all namespaces
- Related: bz#1782182

* Fri Feb  5 2021 Jeff Moyer <jmoyer@redhat.com> - 71.1-1.el8
- Update to v71.1 to pull in ppc support.
- Related: bz#1782182

* Fri Nov  1 2019 Jeff Moyer <jmoyer@redhat.com> - 67-2.el8
- Fix up botched change to nvdimm-security.conf (Jeff Moyer)
- Related: bz#1724531

* Mon Oct 28 2019 Jeff Moyer <jmoyer@redhat.com> - 67-1.el8
- Rebase to v67.  This brings in the following features:
  - support for the 'security frozen' sysfs attribute
  - support for using pmem as system ram
  - various cleanup and bug fixes
- Fix load-keys failure in initramfs (Jeff Moyer)
- Resolves: bz#1724531 bz#1730673 bz#1741164 bz#1741165 bz#1749888 bz#1749889

* Mon Jun  3 2019 Jeff Moyer <jmoyer@redhat.com> - 65-1.el8
- Rebase to v65.
- Resolves: bz#1665407 bz#1634349

* Tue Oct 09 2018 Jeff Moyer <jmoyer@redhat.com - 62-2.el8
- Remove faulty udev rule
- Resolves: bz#1637624

* Thu Aug 23 2018 Jeff Moyer <jmoyer@redhat.com> - 62-1
- rebase to v62
- Resolves: bz#1567756 bz#1497651 bz#1610650 bz#1511774 bz#1570548

* Mon Apr 23 2018 Dan Williams <dan.j.williams@intel.com> - 60.1-1
- release v60.1

* Thu Apr 19 2018 Dan Williams <dan.j.williams@intel.com> - 60-1
- release v60

* Tue Mar 27 2018 Dan Williams <dan.j.williams@intel.com> - 59.3-1
- release v59.3

* Tue Mar 06 2018 Björn Esser <besser82@fedoraproject.org> - 59.2-2
- Rebuilt for libjson-c.so.4 (json-c v0.13.1)

* Fri Feb 09 2018 Dan Williams <dan.j.williams@intel.com> - 59.2-1
- release v59.2

* Fri Feb 09 2018 Dan Williams <dan.j.williams@intel.com> - 59.1-1
- release v59.1

* Fri Feb 09 2018 Dan Williams <dan.j.williams@intel.com> - 59-1
- release v59

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 58.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Dec 10 2017 Björn Esser <besser82@fedoraproject.org> - 58.4-2
- Rebuilt for libjson-c.so.3

* Thu Nov 16 2017 Dan Williams <dan.j.williams@intel.com> - 58.4-1
- release v58.4

* Thu Sep 21 2017 Dan Williams <dan.j.williams@intel.com> - 58.2-1
- release v58.2

* Fri Sep 08 2017 Dan Williams <dan.j.williams@intel.com> - 58.1-2
- gate libpmem dependency on x86_64

* Fri Sep 08 2017 Dan Williams <dan.j.williams@intel.com> - 58.1-1
- add libpmem dependency
- release v58.1

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 57.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 57.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 30 2017 Dan Williams <dan.j.williams@intel.com> - 57.1-1
- Release v57.1

* Sat May 27 2017 Dan Williams <dan.j.williams@intel.com> - 57-1
- Release v57

* Fri Feb 10 2017 Dan Williams <dan.j.williams@intel.com> - 56-1
- Release v56

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 55-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Oct 21 2016 Dan Williams <dan.j.williams@intel.com> - 55-1
- release v55

* Fri Aug 05 2016 Dan Williams <dan.j.williams@intel.com> - 54-1
- add explicit lib version dependencies

* Sat May 28 2016 Dan Williams <dan.j.williams@intel.com> - 53.1-1
- Fix up tag format vs source url confusion

* Fri May 27 2016 Dan Williams <dan.j.williams@intel.com> - 53-1
- add daxctl-libs + daxctl-devel packages
- add bash completion

* Mon Apr 04 2016 Dan Williams <dan.j.williams@intel.com> - 52-1
- Initial rpm submission to Fedora
