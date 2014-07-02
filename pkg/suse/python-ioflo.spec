#
# spec file for package python-ioflo
#
# Copyright (c) 2012 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name:           python-ioflo
Version:        0.9.38
Release:        0
License:        MIT
Summary:        Python IoFlo
Url:            https://github.com/ioflo/ioflo
Group:          Development/Languages/Python
Source0:        https://pypi.python.org/packages/source/i/ioflo/ioflo-%{version}.tar.gz
BuildRoot:      %{_tmppath}/ioflo-%{version}-build

BuildRequires:  python-setuptools
BuildRequires:  fdupes


%if 0%{?suse_version} && 0%{?suse_version} <= 1110
%{!?python_sitelib: %global python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
BuildRequires:  python-importlib
Requires:       python-importlib
%else
BuildArch:      noarch
%endif


%description
IoFlo is a magically powerful open interoperable software framework that enables non experts can intelligently automate 
their own programmable world. IoFlo has its roots in the research and development of autonomous underwater vehicles, 
autonomic ships, and automated buildings. These are cool applications that can be scarily complex. That complexity 
was the prime motivation for IoFlo and its ancestors, to make programming autonomous/autonomic systems easy 
even for people without PhDs.

%prep
%setup -q -n ioflo-%{version}

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot} --optimize=1
%fdupes %{buildroot}%{_prefix}

%files
%defattr(-,root,root)
%{python_sitelib}/*
%{_bindir}/ioflo

%changelog