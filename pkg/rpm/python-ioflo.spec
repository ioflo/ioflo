%if 0%{?fedora} > 12 || 0%{?rhel} > 6
%global with_python3 1
%else

%if 0%{?rhel} == 5
%global with_python26 1
%endif

%if (0%{?rhel} < 7 || 0%{?fedora} < 13)
%global pybasever 2.6
%endif

%{!?__python2: %global __python2 /usr/bin/python%{?pybasever}}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%endif

%global srcname ioflo

Name:           python-%{srcname}
Version:        0.9.39
Release:        1%{?dist}
Summary:        Flow-based programing interface

Group:          Development/Libraries
License:        MIT
URL:            http://ioflo.com
Source0:        http://pypi.python.org/packages/source/i/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{srcname}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%if 0%{?with_python26}
BuildRequires:  python26-devel
BuildRequires:  python26-distribute
BuildRequires:  python26-importlib
Requires:       python26-importlib
%else

%if "%{?pybasever}" == "2.6"
BuildRequires:  python-importlib
Requires:       python-importlib
%endif

BuildRequires:  python-devel
BuildRequires:  python-setuptools
%endif

%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%endif

# We don't want to provide private python extension libs
%{?filter_setup:
%filter_provides_in %{python2_sitearch}/.*\.so$
%if 0%{?with_python3}
%filter_provides_in %{python3_sitearch}/.*\.so$
%endif
%filter_setup
}

%description
Ioflo is a flow-based programming automated reasoning engine and automation
operation system, written in Python.


%if 0%{?with_python3}
%package -n python3-%{srcname}
Summary:  Flow-based programing interface
Group:    Development/Libraries

%description -n python3-%{srcname}
Ioflo is a flow-based programming automated reasoning engine and automation
operation system, written in Python.
%endif


%prep
%setup -q -n %{srcname}-%{version}

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif

%build
%{__python2} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif

%install
rm -rf %{buildroot}
%{__python2} setup.py install --skip-build --root %{buildroot}

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root %{buildroot}
popd
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python2_sitelib}/*
%{_bindir}/%{srcname}

%if 0%{?with_python3}
%files -n python3-%{srcname}
%defattr(-,root,root,-)
%{python3_sitelib}/*
%{_bindir}/%{srcname}
%endif

%changelog
* Thu Jul 24 2014 Erik Johnson <erik@saltstack.com> - 0.9.39-1
- Updated to 0.9.39

* Wed Jul 23 2014 Erik Johnson <erik@saltstack.com> - 0.9.38-1
- Updated to 0.9.38

* Fri Jun 20 2014 Erik Johnson <erik@saltstack.com> - 0.9.35-1
- Initial build
