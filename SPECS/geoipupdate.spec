%global _hardened_build 1

Name:		geoipupdate
Version:	2.5.0
Release:	2%{?dist}
Summary:	Update GeoIP2 and GeoIP Legacy binary databases from MaxMind
License:	GPLv2
URL:		http://dev.maxmind.com/geoip/geoipupdate/
Source0:	http://github.com/maxmind/geoipupdate/releases/download/v%{version}/geoipupdate-%{version}.tar.gz
Source1:	geoipupdate.cron
Source2:	geoipupdate6.cron
BuildRequires:	coreutils
BuildRequires:	gcc
BuildRequires:	libcurl-devel
BuildRequires:	make
BuildRequires:	zlib-devel
# Perl modules used by IPv6 cron script
BuildRequires:	perl-generators
BuildRequires:	perl(File::Copy)
BuildRequires:	perl(File::Spec)
BuildRequires:	perl(LWP::Simple)
BuildRequires:	perl(PerlIO::gzip)
BuildRequires:	perl(strict)

%description
The GeoIP Update program performs automatic updates of GeoIP2 and GeoIP
Legacy binary databases.

%package cron
Summary:	Cron job to do weekly updates of GeoIP databases
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}
Requires:	crontabs
Obsoletes:	GeoIP-update < 1.6.0
Provides:	GeoIP-update = 1.6.0

%description cron
Cron job for weekly updates to GeoIP Legacy database from MaxMind.

%package cron6
Summary:	Cron job to do weekly updates of GeoIP IPv6 databases
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}
Requires:	crontabs
Requires:	wget
Obsoletes:	GeoIP-update6 < 1.6.0
Provides:	GeoIP-update6 = 1.6.0

%description cron6
Cron job for weekly updates to GeoIP IPv6 Legacy database from MaxMind.

%prep
%setup -q

%build
%configure --disable-static --disable-dependency-tracking
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

# We'll package the documentation ourselves
rm -rf %{buildroot}%{_datadir}/doc/geoipupdate

# Fix up the config file to have geoipupdate fetch the free legacy databases by default
sed -i -e 's/^\(ProductIds\) .*$/\1 506 517 533/' \
	%{buildroot}%{_sysconfdir}/GeoIP.conf

install -D -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/cron.weekly/geoipupdate
install -D -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/cron.weekly/geoipupdate6

# Make the download directory for the IPv6 data cron job and some ghost files
mkdir -p %{buildroot}%{_datadir}/GeoIP/download/
: > %{buildroot}%{_datadir}/GeoIP/download/GeoIPv6.dat.gz
: > %{buildroot}%{_datadir}/GeoIP/download/GeoLiteCityv6.dat.gz
: > %{buildroot}%{_datadir}/GeoIP/download/GeoIPASNumv6.dat.gz

%files
%if 0%{?_licensedir:1}
%license LICENSE
%else
%doc LICENSE
%endif
%doc conf/GeoIP.conf.default README.md ChangeLog.md
%config(noreplace) %{_sysconfdir}/GeoIP.conf
%{_bindir}/geoipupdate
%{_mandir}/man1/geoipupdate.1*
%{_mandir}/man5/GeoIP.conf.5*

%files cron
%config(noreplace) %{_sysconfdir}/cron.weekly/geoipupdate

%files cron6
%config(noreplace) %{_sysconfdir}/cron.weekly/geoipupdate6
%dir %{_datadir}/GeoIP/
%dir %{_datadir}/GeoIP/download/
%ghost %{_datadir}/GeoIP/download/GeoIPv6.dat.gz
%ghost %{_datadir}/GeoIP/download/GeoLiteCityv6.dat.gz
%ghost %{_datadir}/GeoIP/download/GeoIPASNumv6.dat.gz

%changelog
* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Oct 31 2017 Paul Howarth <paul@city-fan.org> - 2.5.0-1
- Update to 2.5.0
  - Replace use of strnlen() due to lack of universal availability (GH#71)
  - Document the 'LockFile' option in the 'GeoIP.conf' man page (GH#64)
  - Remove unused base64 library (GH#68)
  - Add the new configuration option 'PreserveFileTimes'; if set, the
    downloaded files will get the same modification times as their original on
    the server (default is '0') (GH#63)
  - Use the correct types when calling 'curl_easy_setopt()'; this fixes
    warnings generated by libcurl's 'typecheck-gcc.h' (GH#61)
  - In 'GeoIP.conf', the 'UserId' option was renamed to 'AccountID' and the
    'ProductIds' option was renamed to 'EditionIDs'; the old options will
    continue to work, but upgrading to the new names is recommended for
    forward compatibility

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri May 26 2017 Paul Howarth <paul@city-fan.org> - 2.4.0-1
- Update to 2.4.0
  - geoipupdate now checks that the database directory is writable: if it is
    not, it reports the problem and aborts
  - geoipupdate now acquires a lock when starting up to ensure only one
    instance may run at a time: a new option, 'LockFile', exists to set the
    file to use as a lock ('.geoipupdate.lock' in the database directory by
    default)
  - geoipupdate now prints out additional information from the server when a
    download request results in something other than HTTP status 2xx; this
    provides more information when the API does not respond with a database
    file
  - ${datarootdir}/GeoIP is now created on 'make install' (GH#29)
  - Previously, a variable named 'ERROR' was used, which caused issues building
    on Windows (GH#36)
- Drop EL-5 support
  - Drop BuildRoot: and Group: tags
  - Drop explicit buildroot cleaning in %%install section
  - Drop explicit %%clean section
  - noarch subpackages always available now
  - libcurl-devel always available now

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan  5 2017 Paul Howarth <paul@city-fan.org> - 2.3.1-1
- Update to 2.3.1
  - geoipupdate now uses TCP keep-alive when compiled with cURL 7.25 or
    greater
  - Previously, on an invalid gzip file, geoipupdate would output binary data
    to stderr; it now displays an appropriate error message
  - Install README, ChangeLog, GeoIP.conf.default etc. into docdir (GH#33)
  - $(sysconfdir) is now created if it doesn't exist (GH#33)
  - The sample config file is now usable (GH#33)

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 22 2016 Paul Howarth <paul@city-fan.org> - 2.2.2-1
- Update to 2.2.2
  - geoipupdate now calls fsync on the database directory after a rename to
    make it durable in the event of a crash
- Update autotools patch

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Apr 13 2015 Paul Howarth <paul@city-fan.org> - 2.2.1-2
- Split patch for upstream issue #26 into separate patches for upstream changes
  and effect of running autotools

* Wed Mar  4 2015 Philip A. Prindeville <philipp@fedoraproject.org> - 2.2.1-1
- Update to 2.2.1
  - geoipupdate now verifies the MD5 of the new database before deploying it;
    if the database MD5 does not match the expected MD5, geoipupdate will exit
    with an error
  - The copy of 'base64.c' and 'base64.h' was switched to a version under
    GPLv2+ to prevent a license conflict
  - The 'LICENSE' file was added to the distribution
  - Several issues in the documentation were fixed
- Use interim fix for upstream issue #26 until it's accepted:
  https://github.com/maxmind/geoipupdate/issues/26
- Add buildroot and clean, BR: curl-devel rather than libcurl-devel for
  EL-5 compatibility

* Tue Feb 10 2015 Paul Howarth <paul@city-fan.org> - 2.1.0-4
- New geoipupdate6 cron script written in Perl that doesn't download the data
  if it hasn't changed

* Fri Feb  6 2015 Paul Howarth <paul@city-fan.org> - 2.1.0-3
- Add cron6 subpackage, equivalent to old GeoIP-update6 package
- Revise obsoletes/provides

* Sun Feb  1 2015 Philip A. Prindeville <philipp@fedoraproject.org> - 2.1.0-2
- Remove architecture-specific dependency in noarch subpackage

* Mon Jan 26 2015 Philip A. Prindeville <philipp@fedoraproject.org> - 2.1.0-1
- Initial review package (generated by rpmdev-newspec)

