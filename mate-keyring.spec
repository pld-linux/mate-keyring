#
# Conditional build:
%bcond_with	gtk3		# use GTK+ 3.x instead of 2.x
%bcond_with	p11_tests	# PKCS#11 tests
#
Summary:	Keep passwords and other user's secrets
Summary(pl.UTF-8):	Przechowywanie haseł i innych tajnych danych użytkowników
Name:		mate-keyring
Version:	1.6.1
Release:	2
License:	LGPL v2+ (library), GPL v2+ (programs)
Group:		X11/Applications
Source0:	http://pub.mate-desktop.org/releases/1.6/%{name}-%{version}.tar.xz
# Source0-md5:	3691d4d42ce7db525e6374b1e6505677
Patch0:		%{name}-doc.patch
Patch1:		%{name}-names.patch
URL:		http://mate-desktop.org/
BuildRequires:	autoconf >= 2.53
BuildRequires:	automake >= 1:1.9
BuildRequires:	dbus-devel >= 1.0
BuildRequires:	docbook-dtd412-xml
BuildRequires:	gettext-tools >= 0.10.40
BuildRequires:	glib2-devel >= 1:2.26.0
%{!?with_gtk3:BuildRequires:	gtk+2-devel >= 2:2.20.0}
%{?with_gtk3:BuildRequires:	gtk+3-devel >= 3.0.0}
BuildRequires:	gtk-doc >= 1.9
BuildRequires:	intltool >= 0.35.0
BuildRequires:	libcap-devel >= 2
BuildRequires:	libgcrypt-devel >= 1.2.2
# actually not used, only checks and includes exist
BuildRequires:	libtasn1-devel >= 0.3.4
BuildRequires:	libtool >= 1:1.4.3
%{?with_p11_tests:BuildRequires:	p11-tests-devel >= 0.1}
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.592
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
Requires(post,postun):	glib2 >= 1:2.26.0
Requires:	dbus >= 1.0
Requires:	filesystem >= 4.0-28
Requires:	libgcrypt >= 1.2.2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libexecdir	%{_libdir}/%{name}

%description
mate-keyring is a program that keeps password and other secrets for
users. It is run as a daemon in the session, similar to ssh-agent, and
other applications can locate it by an environment variable or DBus.

%description -l pl.UTF-8
mate-keyring to program do przechowywania haseł i innych tajnych
danych użytkowników. Działa jako demon w sesji, podobnie do
ssh-agenta, a inne aplikacje mogą znaleźć go poprzez zmienną
środowiskową lub DBus.

%package libs
Summary:	MATE keyring libraries
Summary(pl.UTF-8):	Biblioteki MATE keyring
License:	LGPL v2+
Group:		X11/Libraries
Requires:	glib2 >= 1:2.26.0
%{!?with_gtk3:Requires:	gtk+2 >= 2:2.20.0}
%{?with_gtk3:Requires:	gtk+3 >= 3.0.0}
Requires:	libtasn1 >= 0.3.4

%description libs
MATE keyring library.

%description libs -l pl.UTF-8
Biblioteka MATE keyring.

%package devel
Summary:	Header files for MATE keyring libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek MATE keyring
License:	LGPL v2+
Group:		X11/Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	glib2-devel >= 1:2.26.0
%{!?with_gtk3:Requires:	gtk+2-devel >= 2:2.20.0}
%{?with_gtk3:Requires:	gtk+3-devel >= 3.0.0}
Requires:	libtasn1-devel >= 0.3.4

%description devel
Header files for MATE keyring libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek MATE keyring.

%package apidocs
Summary:	MATE keyring API documentation
Summary(pl.UTF-8):	Dokumentacja API MATE keyring
License:	LGPL v2+
Group:		Documentation
Requires:	gtk-doc-common

%description apidocs
MATE keyring API documentation.

%description apidocs -l pl.UTF-8
Dokumentacja API MATE keyring.

%package -n pam-pam_mate_keyring
Summary:	A PAM module for unlocking keyrings at login time
Summary(pl.UTF-8):	Moduł PAM do odblokowywania zbiorów kluczy w czasie logowania
License:	LGPL v2+
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Obsoletes:	mate-keyring-pam

%description -n pam-pam_mate_keyring
A PAM module that can automatically unlock the "login" keyring when
the user logs in and start the keyring daemon.

%description -n pam-pam_mate_keyring -l pl.UTF-8
Moduł PAM, który może automatycznie odblokowywać zbiór kluczy "login"
w czasie logowania użytkownika i uruchamiania demona keyring.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%build
%{__gtkdocize}
%{__glib_gettextize}
%{__intltoolize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-silent-rules \
	--enable-gtk-doc \
	%{!?with_p11_tests:--disable-p11-tests} \
	%{?with_gtk3:--with-gtk=3.0} \
	--with-html-dir=%{_gtkdocdir} \
	--with-pam-dir=/%{_lib}/security \
	--with-root-certs=%{_sysconfdir}/certs
%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install install-pam \
	DESTDIR=$RPM_BUILD_ROOT

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/lib*.la
# dlopened modules
%{__rm} $RPM_BUILD_ROOT/%{_lib}/security/pam_mate_keyring.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/mate-keyring/{devel,standalone}/*.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/pkcs11/mate-keyring-pkcs11.la

# mate < 1.5 did not exist in pld, avoid dependency on mate-conf
%{__rm} $RPM_BUILD_ROOT%{_datadir}/MateConf/gsettings/org.mate.crypto.*.convert

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%posttrans
%glib_compile_schemas

%postun
if [ "$1" = "0" ]; then
	%glib_compile_schemas
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog NEWS README
%attr(755,root,root) %{_bindir}/mate-keyring
%attr(755,root,root) %{_bindir}/mate-keyring-daemon
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libexecdir}/mate-keyring-prompt
%dir %{_libdir}/%{name}/devel
%attr(755,root,root) %{_libdir}/%{name}/devel/gkm-mate2-store-standalone.so
%attr(755,root,root) %{_libdir}/%{name}/devel/gkm-roots-store-standalone.so
%attr(755,root,root) %{_libdir}/%{name}/devel/gkm-ssh-store-standalone.so
%attr(755,root,root) %{_libdir}/%{name}/devel/gkm-xdg-store-standalone.so
%dir %{_libdir}/%{name}/standalone
%attr(755,root,root) %{_libdir}/%{name}/standalone/gkm-secret-store-standalone.so
%attr(755,root,root) %{_libdir}/pkcs11/mate-keyring-pkcs11.so
%{_sysconfdir}/xdg/autostart/mate-keyring-gpg.desktop
%{_sysconfdir}/xdg/autostart/mate-keyring-pkcs11.desktop
%{_sysconfdir}/xdg/autostart/mate-keyring-secrets.desktop
%{_sysconfdir}/xdg/autostart/mate-keyring-ssh.desktop
%{_datadir}/dbus-1/services/org.mate-freedesktop.secrets.service
%{_datadir}/dbus-1/services/org.mate.keyring.service
%{_datadir}/glib-2.0/schemas/org.mate.crypto.*.gschema.xml
%{_datadir}/mate-keyring
%{_datadir}/mategcr
%{_mandir}/man1/mate-keyring.1*
%{_mandir}/man1/mate-keyring-daemon.1*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmategck.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libmategck.so.0
%attr(755,root,root) %{_libdir}/libmategcr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libmategcr.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmategck.so
%attr(755,root,root) %{_libdir}/libmategcr.so
%{_includedir}/mate-gck
%{_includedir}/mategcr
%{_pkgconfigdir}/mate-gck-0.pc
%{_pkgconfigdir}/mate-gcr-0.pc

%files apidocs
%defattr(644,root,root,755)
%{_gtkdocdir}/mate-gck
%{_gtkdocdir}/mate-gcr-0

%files -n pam-pam_mate_keyring
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_mate_keyring.so
