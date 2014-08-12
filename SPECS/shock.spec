# Use rpmbuild --define="version  1.0"  -ba shock.spec 
# To command line override the Version number defined here. ### hint: we need a makefile
%{!?version: %global version 0.UNKNOWN}

# Don't try fancy stuff like debuginfo, which is useless on binary-only
# packages. Don't strip binary too
# Be sure buildpolicy set to do nothing
%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress


Summary: Shock is an object storage management system.
Name: shock
Version: %{version}
Release: 3
License: BSD
Group: Applications/Databases
%define SOURCE_URL github.com/MG-RAST/Shock/...
SOURCE1: shockd.conf
SOURCE2: shockd.initd
SOURCE3: shockd.sysconfig
URL: https://github.com/MG-RAST/Shock

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: golang >= 1.1
BuildRequires: git, mercurial, bzr 
Requires(pre): shadow-utils
Requires: mongodb-server >= 2.4

%description 
Shock is a platform to support computation, storage, and
distribution. Designed from the ground up to be fast, scalable, fault
tolerant, federated.

Shock is RESTful. Accessible from desktops, HPC systems, exotic
hardware, the cloud and your smartphone.

Shock is for scientific data. One of the challenges of large volume
scientific data is that without often complex metadata it is of little
to no value. Shock allows storage and querying of complex metadata.

Shock is a data management system. The long term goals of Shock
include the ability to annotate, anonymize, convert, filter, perform
quality control, and statically subsample at line speed bioinformatics
sequence data. Extensible plug-in architecture is in development.


%prep
#%setup -q


%build
cd $RPM_BUILD_DIR
export GOPATH=$RPM_BUILD_DIR
go get %{SOURCE_URL}



%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}

# Binaries to the usual locations
install -Dp -m755 bin/shock-server %{buildroot}%{_sbindir}/shock-server
install -Dp -m755 bin/shock-client %{buildroot}%{_bindir}/shock-client

# Init script (sysvinit style only right now)
install -Dp -m0755 %{SOURCE2} %{buildroot}%{_initddir}/shockd

# install sysconfig file
install -Dp -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/shockd 

# Shock config itself
install -Dp -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/shock/shockd.conf

# Create an empty data area
mkdir -p %{buildroot}/srv/%{name}/data

# Create log dir - it must be a dir - we're kinda spammy with the logs
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

# Copy the site "doc" tree to the %docs dir.
# This might be wrong- users could leave out %docs and leave us with nothing.
mkdir -p %{buildroot}%{_defaultdocdir}
# This is a terrible hack - prevent a dangling symlink in the docs
rm -f src/github.com/MG-RAST/Shock/shock-server/site/assets/misc/README.md
cp src/github.com/MG-RAST/Shock/README.md src/github.com/MG-RAST/Shock/shock-server/site/assets/misc/README.md


%clean
rm -rf %{buildroot}


%pre
getent group shock >/dev/null || groupadd -r shock
getent passwd shock >/dev/null || \
    useradd -r -g shock -d /opt/shock -s /sbin/nologin \
    -c "Shock Daemon User" shock
exit 0

%post
if [ $1 = 1 ] ; then 
   # initial installation
   /sbin/chkconfig --add shockd
fi

%preun
if [ $1 = 1 ] ; then
   # Package removal, not upgrade
   /sbin/service shockd > /dev/null 2>&1
   /sbin/chkconfig --del shockd
fi

%postun 
if [ "$1" -ge 1 ]; then
    /sbin/service shockd condrestart > /dev/null 2>&1
fi
exit 0


%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/shockd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/shockd
%{_initddir}/shockd
%{_sbindir}/shock-server
%{_bindir}/shock-client
%doc src/github.com/MG-RAST/Shock/shock-server/site
%doc src/github.com/MG-RAST/Shock/LICENSE
%attr(755, shock, shock)%dir /srv/shock
%attr(755, shock, shock)%{_localstatedir}/log/%{name}

%changelog
* Wed Jan 29 2014 root <root@france.igsb.anl.gov> - 0.8-3
- Remove binary tar ball and build from source
- Add version override from the command line
- Add proper build requires
- Include the "site" dir into the docs
- Fix dangling symlink in "site" dir
- Move everything out of /opt and into more FHS compliant locations.
  I know /srv isn't Fedora/EPEL compliant - thats next. 

* Fri Jan 23 2014 Hunter Matthews <hunter@mcs.anl.gov> 0.8-2
- Fixed typos in the post scripts and tried to make pkg "own" the /etc/shock dir

* Fri Jan 23 2014 Hunter Matthews <hunter@mcs.anl.gov> 0.8-1
- First Build
- This is a TERRIBLE tar ball only build - but it gets me an rpm which 
  is more than we've had.

## END OF LINE ##

