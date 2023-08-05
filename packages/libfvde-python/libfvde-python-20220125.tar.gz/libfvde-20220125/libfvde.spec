Name: libfvde
Version: 20220125
Release: 1
Summary: Library to access the FileVault Drive Encryption (FVDE) format
Group: System Environment/Libraries
License: LGPLv3+
Source: %{name}-%{version}.tar.gz
URL: https://github.com/libyal/libfvde
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:         openssl          zlib
BuildRequires: gcc         openssl-devel          zlib-devel

%description -n libfvde
Library to access the FileVault Drive Encryption (FVDE) format

%package -n libfvde-static
Summary: Library to access the FileVault Drive Encryption (FVDE) format
Group: Development/Libraries
Requires: libfvde = %{version}-%{release}

%description -n libfvde-static
Static library version of libfvde.

%package -n libfvde-devel
Summary: Header files and libraries for developing applications for libfvde
Group: Development/Libraries
Requires: libfvde = %{version}-%{release}

%description -n libfvde-devel
Header files and libraries for developing applications for libfvde.

%package -n libfvde-python2
Obsoletes: libfvde-python < %{version}
Provides: libfvde-python = %{version}
Summary: Python 2 bindings for libfvde
Group: System Environment/Libraries
Requires: libfvde = %{version}-%{release} python2
BuildRequires: python2-devel

%description -n libfvde-python2
Python 2 bindings for libfvde

%package -n libfvde-python3
Summary: Python 3 bindings for libfvde
Group: System Environment/Libraries
Requires: libfvde = %{version}-%{release} python3
BuildRequires: python3-devel

%description -n libfvde-python3
Python 3 bindings for libfvde

%package -n libfvde-tools
Summary: Several tools for reading FileVault Drive Encryption volumes
Group: Applications/System
Requires: libfvde = %{version}-%{release} fuse-libs
BuildRequires: fuse-devel

%description -n libfvde-tools
Several tools for reading FileVault Drive Encryption volumes

%prep
%setup -q

%build
%configure --prefix=/usr --libdir=%{_libdir} --mandir=%{_mandir} --enable-python2 --enable-python3
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
%make_install

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -n libfvde
%defattr(644,root,root,755)
%license COPYING COPYING.LESSER
%doc AUTHORS README
%attr(755,root,root) %{_libdir}/*.so.*

%files -n libfvde-static
%defattr(644,root,root,755)
%license COPYING COPYING.LESSER
%doc AUTHORS README
%attr(755,root,root) %{_libdir}/*.a

%files -n libfvde-devel
%defattr(644,root,root,755)
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/*.la
%{_libdir}/*.so
%{_libdir}/pkgconfig/libfvde.pc
%{_includedir}/*
%{_mandir}/man3/*

%files -n libfvde-python2
%defattr(644,root,root,755)
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python2*/site-packages/*.a
%{_libdir}/python2*/site-packages/*.la
%{_libdir}/python2*/site-packages/*.so

%files -n libfvde-python3
%defattr(644,root,root,755)
%license COPYING COPYING.LESSER
%doc AUTHORS README
%{_libdir}/python3*/site-packages/*.a
%{_libdir}/python3*/site-packages/*.la
%{_libdir}/python3*/site-packages/*.so

%files -n libfvde-tools
%defattr(644,root,root,755)
%license COPYING COPYING.LESSER
%doc AUTHORS README
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*

%changelog
* Tue Jan 25 2022 Joachim Metz <joachim.metz@gmail.com> 20220125-1
- Auto-generated

