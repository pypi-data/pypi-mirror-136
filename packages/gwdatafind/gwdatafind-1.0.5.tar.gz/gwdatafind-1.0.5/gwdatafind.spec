%define srcname gwdatafind
%define version 1.0.5
%define release 1

Name:      python-%{srcname}
Version:   %{version}
Release:   %{release}%{?dist}
Summary:   The client library for the GWDataFind service
Group:     Development/Libraries
License:   GPLv3+
Url:       https://gwdatafind.readthedocs.io/
Source0:   %pypi_source
Packager:  Duncan Macleod <duncan.macleod@ligo.org>

BuildArch: noarch

# build dependencies
BuildRequires: python-srpm-macros
BuildRequires: python-rpm-macros
BuildRequires: python3-rpm-macros

# python3-gwdatafind
BuildRequires: python%{python3_pkgversion}-setuptools

# gwdatafind (requires all runtime requirements for python3-gwdatafind)
BuildRequires: python%{python3_pkgversion}-ligo-segments
BuildRequires: python%{python3_pkgversion}-pyOpenSSL
BuildRequires: help2man

# testing dependencies
BuildRequires: man-db
BuildRequires: python%{python3_pkgversion}-pytest >= 2.8.0

# -- src.rpm

%description
The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors. This is the source package for the
GWDataFind client API.

# -- gwdatafind

%package -n %{srcname}
Summary: %{summary}
Requires: python%{python3_pkgversion}-%{srcname} = %{version}-%{release}
Requires: python%{python3_pkgversion}-setuptools
Conflicts: glue < 1.61.0
Conflicts: python2-gwdatafind < 1.0.4-3
%description -n %{srcname}
The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors. This package provides the python interface
libraries.

# -- python3x-gwdatafind

%package -n python%{python3_pkgversion}-%{srcname}
Summary:  Python %{python3_version} library for the GWDataFind service
Requires: python%{python3_pkgversion}-pyOpenSSL
Requires: python%{python3_pkgversion}-ligo-segments
%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}
%description -n python%{python3_pkgversion}-%{srcname}
The DataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors. This package provides the
Python %{python3_version} interface libraries.

# -- build steps

%prep
%autosetup -n %{srcname}-%{version}

%build
%py3_build

%install
%py3_install
mkdir -vp %{buildroot}%{_mandir}/man1
env PYTHONPATH="%{buildroot}%{python3_sitelib}" \
help2man \
    --output %{buildroot}%{_mandir}/man1/gw_data_find.1 \
    --name "discover available GW data" \
    --no-discard-stderr \
    --no-info \
    --section 1 \
    --source %{srcname} \
    --version-string %{version} \
    %{buildroot}%{_bindir}/gw_data_find \
;

%check
# test python3
env PYTHONPATH="%{buildroot}%{python3_sitelib}" %{__python3} -m pytest --pyargs gwdatafind
env PYTHONPATH="%{buildroot}%{python3_sitelib}" %{__python3} -m gwdatafind --help
env PYTHONPATH="%{buildroot}%{python3_sitelib}" PATH="%{buildroot}%{_bindir}:${PATH}" gw_data_find --help
# test man pages
env MANPATH="%{buildroot}%{_mandir}" man -P cat gw_data_find

%clean
rm -rf $RPM_BUILD_ROOT

%files -n %{srcname}
%license LICENSE
%doc README.md
%{_bindir}/gw_data_find
%{_mandir}/man1/gw_data_find.1*

%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

# -- changelog

%changelog
* Fri Jan 28 2022 Duncan Macleod <duncan.macleod@ligo.org> 1.0.5-1
- update for 1.0.5
- rename SRPM to not match any binary RPMs
- drop Python 2 packages
- update summary text to not reference LDR
- separate bindir into separate package

* Fri Jul 12 2019 Duncan Macleod <duncan.macleod@ligo.org> 1.0.4-2
- fixed incorrect installation of /usr/bin/gw_data_find
- use python-srpm-macros to provide python3 versions

* Fri Jan 11 2019 Duncan Macleod <duncan.macleod@ligo.org> 1.0.4-1
- include command-line client, requires matching glue release

* Fri Jan 04 2019 Duncan Macleod <duncan.macleod@ligo.org> 1.0.3-1
- added python3 packages

* Tue Aug 14 2018 Duncan Macleod <duncan.macleod@ligo.org> 1.0.2-1
- bug-fix release

* Tue Aug 14 2018 Duncan Macleod <duncan.macleod@ligo.org> 1.0.1-1
- bug-fix release

* Mon Jul 30 2018 Duncan Macleod <duncan.macleod@ligo.org> 1.0.0-1
- first build
