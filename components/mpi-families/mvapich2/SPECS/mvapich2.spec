#----------------------------------------------------------------------------bh-
# This RPM .spec file is part of the OpenHPC project.
#
# It may have been modified from the default version supplied by the underlying
# release package (if available) in order to apply patches, perform customized
# build/install configurations, and supply additional files to support
# desired integration conventions.
#
#----------------------------------------------------------------------------eh-

# MVAPICH2 MPI stack that is dependent on compiler toolchain

%include %{_sourcedir}/OHPC_macros

%ohpc_compiler

# Multiple permutations for this MPI stack are possible depending
# on the desired underlying resource manager and comm library support.

%{!?with_slurm: %global with_slurm 0}
%{!?with_pbs: %global with_pbs 0}
%{!?with_psm: %global with_psm 0}
%{!?with_psm2: %global with_psm2 0}
%{!?RMS_DELIM: %global RMS_DELIM %{nil}}
%{!?COMM_DELIM: %global COMM_DELIM %{nil}}

# Base package name/config
%define pname mvapich2

Summary:   OSU MVAPICH2 MPI implementation
Name:      %{pname}%{COMM_DELIM}-%{compiler_family}%{RMS_DELIM}%{PROJ_DELIM}
Version:   2.2
Release:   1%{?dist}
License:   BSD
Group:     %{PROJ_NAME}/mpi-families
URL:       http://mvapich.cse.ohio-state.edu/overview/mvapich2/
Source0:   http://mvapich.cse.ohio-state.edu/download/mvapich/mv2/%{pname}-%{version}.tar.gz
Source1:   OHPC_macros

# karl.w.schulz@intel.com (09/08/2015)
%global _default_patch_fuzz 2
Patch0:    winfree.patch
# karl.w.schulz@intel.com (04/13/2016)
Patch1:    minit.patch
Patch2:    mvapich2-get_cycles.patch

%if 0%{with_slurm}
BuildRequires: slurm-devel%{PROJ_DELIM} slurm%{PROJ_DELIM}
Provides:      %{pname}-%{compiler_family}%{PROJ_DELIM}
%endif

%if 0%{with_psm}
BuildRequires:  infinipath-psm infinipath-psm-devel
Provides: %{pname}-%{compiler_family}%{PROJ_DELIM}
%endif

%if 0%{with_psm2}
BuildRequires:  hfi1-psm hfi1-psm-devel
Provides: %{pname}-%{compiler_family}%{PROJ_DELIM}
Conflicts: %{pname}-%{compiler_family}%{PROJ_DELIM}
%endif

%if 0%{?sles_version} || 0%{?suse_version}
Buildrequires: ofed
%endif
%if 0%{?rhel_version} || 0%{?centos_version}
Buildrequires: rdma
%endif

Requires: prun%{PROJ_DELIM}

BuildRequires: bison
BuildRequires: libibmad-devel libibverbs-devel
BuildRequires: librdmacm-devel

# Default library install path
%define install_path %{OHPC_MPI_STACKS}/%{pname}-%{compiler_family}/%version

%description

MVAPICH2 is a high performance MPI-2 implementation (with initial
support for MPI-3) for InfiniBand, 10GigE/iWARP and RoCE.  MVAPICH2
provides underlying support for several interfaces (such as OFA-IB,
OFA-iWARP, OFA-RoCE, PSM, Shared Memory, and TCP) for portability
across multiple networks.

%prep

%setup -q -n %{pname}-%{version}
# disabled on 09/19/16
# %patch0 -p1
# disabled on 09/19/16, patch was upstreamed in v2.2
# %patch1 -p0
%patch2 -p1

%build
%ohpc_setup_compiler
%{?scl_enable}
./configure --prefix=%{install_path} \
	    --enable-cxx \
	    --enable-g=dbg \
            --with-device=ch3:mrail \
%if 0%{?with_pwm} || 0%{?with_psm2}
            --with-device=ch3:psm \
%endif
%if 0%{with_slurm}
            --with-pm=no --with-pmi=slurm \
%endif
	    --enable-fast=O3 || { cat config.log && exit 1; }

make
%{?scl_disable}
%install
%ohpc_setup_compiler
%{?scl_enable}
# 06/04/15 - karl.w.schulz@intel.com; run serial build for fortran deps
make DESTDIR=$RPM_BUILD_ROOT install

%{?scl_disable}

# Remove .la files detected by rpm
rm $RPM_BUILD_ROOT/%{install_path}/lib/*.la


# OpenHPC module file
%{__mkdir_p} %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}/%{pname}
%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}/%{pname}/%{version}
#%Module1.0#####################################################################

proc ModulesHelp { } {

puts stderr " "
puts stderr "This module loads the %{pname} library built with the %{compiler_family} toolchain."
puts stderr "\nVersion %{version}\n"

}
module-whatis "Name: %{pname} built with %{compiler_family} toolchain"
module-whatis "Version: %{version}"
module-whatis "Category: runtime library"
module-whatis "Description: %{summary}"
module-whatis "URL: %{url}"

set     version			    %{version}

prepend-path    PATH                %{install_path}/bin
prepend-path    MANPATH             %{install_path}/man
prepend-path	LD_LIBRARY_PATH	    %{install_path}/lib
prepend-path    MODULEPATH          %{OHPC_MODULEDEPS}/%{compiler_family}-%{pname}
prepend-path    MPI_DIR             %{install_path}
prepend-path    PKG_CONFIG_PATH     %{install_path}/lib/pkgconfig

family "MPI"
EOF

%{__cat} << EOF > %{buildroot}/%{OHPC_MODULEDEPS}/%{compiler_family}/%{pname}/.version.%{version}
#%Module1.0#####################################################################
##
## version file for %{pname}-%{version}
##
set     ModulesVersion      "%{version}"
EOF

%{__mkdir_p} ${RPM_BUILD_ROOT}/%{_docdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{OHPC_HOME}
%doc README.envvar
%doc COPYRIGHT
%doc CHANGELOG
%doc CHANGES
%doc README


%changelog
* Fri Feb 17 2017 Adrian Reber <areber@redhat.com> - 2.2-1
- Switching to %%ohpc_compiler macro

* Tue Aug  5 2014  <karl.w.schulz@intel.com>
- Initial build.
