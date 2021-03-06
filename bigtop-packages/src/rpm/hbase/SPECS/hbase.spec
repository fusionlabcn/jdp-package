# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
%define _unpackaged_files_terminate_build 0

# Set the following parameters
%define stack_name %{soft_stack_name}
%define stack_version %{soft_stack_version}

%define stack_home /opt/%{stack_name}/%{stack_version}
%define component_name hbase
%define component_install_dir %{stack_home}/%{component_name}

%define etc_dir %{stack_home}/etc/%{component_name}
%define config_dir %{etc_dir}/conf.dist

%define etc_hbase_conf %{stack_home}/%{_sysconfdir}/%{component_name}
%define etc_hbase_conf_dist %{config_dir}
%define hbase_home %{stack_home}/%{component_name}
%define bin_hbase %{hbase_home}/bin
%define lib_hbase %{hbase_home}/lib
%define conf_hbase %{hbase_home}/conf
%define logs_hbase %{hbase_home}/logs
%define pids_hbase %{hbase_home}/pids
%define webapps_hbase %{hbase_home}/hbase-webapps
%define man_dir %{hbase_home}/man
%define hbase_username hbase
%define hbase_services master regionserver thrift thrift2 rest
%define hadoop_home %{stack_home}/hadoop
%define zookeeper_home %{stack_home}/zookeeper

%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

# SLES is more strict anc check all symlinks point to valid path
# But we do point to a hadoop jar which is not there at build time
# (but would be at install time).
# Since our package build system does not handle dependencies,
# these symlink checks are deactivated
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%define doc_hbase %{stack_home}/%{component_name}/doc
%global initd_dir %{stack_home}/%{component_name}/%{_sysconfdir}/rc.d
%define alternatives_cmd update-alternatives

%else

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?mgaversion:1}0

# FIXME: brp-repack-jars uses unzip to expand jar files
# Unfortunately guice-2.0.jar pulled by ivy contains some files and directories without any read permission
# and make whole process to fail.
# So for now brp-repack-jars is being deactivated until this is fixed.
# See BIGTOP-294
%define __os_install_post \
    %{_rpmconfigdir}/brp-compress ; \
    %{_rpmconfigdir}/brp-strip-static-archive %{__strip} ; \
    %{_rpmconfigdir}/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}
%endif


%define doc_hbase %{stack_home}/%{component_name}/doc
%global initd_dir %{stack_home}/%{component_name}/%{_sysconfdir}/rc.d/init.d
%define alternatives_cmd alternatives

%endif


Name: %{component_name}%{soft_package_version}
Version: %{hbase_version}
Release: %{hbase_release}
Summary: HBase is the Hadoop database. Use it when you need random, realtime read/write access to your Big Data. This project's goal is the hosting of very large tables -- billions of rows X millions of columns -- atop clusters of commodity hardware. 
URL: http://hbase.apache.org/
Group: Development/Libraries
Buildroot: %{_topdir}/INSTALL/%{component_name}-%{version}
License: ASL 2.0
Source0: %{component_name}-%{hbase_base_version}.tar.gz
Source1: do-component-build
Source2: install_hbase.sh
Source3: hbase.svc
Source4: init.d.tmpl
Source5: hbase.default
Source6: hbase.nofiles.conf
Source7: regionserver-init.d.tpl
#BIGTOP_PATCH_FILES
BuildArch: noarch
Requires: coreutils, /usr/sbin/useradd, /sbin/chkconfig, /sbin/service
Requires: hadoop%{soft_package_version}, zookeeper%{soft_package_version} >= 3.4.0, anyscale-select >= %{stack_version}

%if  0%{?mgaversion}
Requires: bsh-utils
%else
Requires: sh-utils
%endif


%description 
HBase is an open-source, distributed, column-oriented store modeled after Google' Bigtable: A Distributed Storage System for Structured Data by Chang et al. Just as Bigtable leverages the distributed data storage provided by the Google File System, HBase provides Bigtable-like capabilities on top of Hadoop. HBase includes:

    * Convenient base classes for backing Hadoop MapReduce jobs with HBase tables
    * Query predicate push down via server side scan and get filters
    * Optimizations for real time queries
    * A high performance Thrift gateway
    * A REST-ful Web service gateway that supports XML, Protobuf, and binary data encoding options
    * Cascading source and sink modules
    * Extensible jruby-based (JIRB) shell
    * Support for exporting metrics via the Hadoop metrics subsystem to files or Ganglia; or via JMX

%package master
Summary: The Hadoop HBase master Server.
Group: System/Daemons
Requires: %{component_name}%{soft_package_version} = %{version}
Requires(pre): %{component_name}%{soft_package_version} = %{version}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif

%description master
HMaster is the "master server" for a HBase. There is only one HMaster for a single HBase deployment.

%package regionserver
Summary: The Hadoop HBase RegionServer server.
Group: System/Daemons
Requires: %{component_name}%{soft_package_version} = %{version}
Requires(pre):  %{component_name}%{soft_package_version} = %{version}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description regionserver 
HRegionServer makes a set of HRegions available to clients. It checks in with the HMaster. There are many HRegionServers in a single HBase deployment.

%package thrift
Summary: The Hadoop HBase Thrift Interface
Group: System/Daemons
Requires: %{component_name}%{soft_package_version} = %{version}
Requires(pre): %{component_name}%{soft_package_version} = %{version}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description thrift
ThriftServer - this class starts up a Thrift server which implements the Hbase API specified in the Hbase.thrift IDL file.
"Thrift is a software framework for scalable cross-language services development. It combines a powerful software stack with a code generation engine to build services that work efficiently and seamlessly between C++, Java, Python, PHP, and Ruby. Thrift was developed at Facebook, and we are now releasing it as open source." For additional information, see http://developers.facebook.com/thrift/. Facebook has announced their intent to migrate Thrift into Apache Incubator.

%package thrift2
Summary: The Hadoop HBase Thrift2 Interface
Group: System/Daemons
Requires: %{component_name}%{soft_package_version} = %{version}
Requires(pre): %{component_name}%{soft_package_version} = %{version}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description thrift2
Thrift2 Server to supersede original Thrift Server.
Still under development. https://issues.apache.org/jira/browse/HBASE-8818

%package doc
Summary: Hbase Documentation
Group: Documentation
BuildArch: noarch
Obsoletes: %{component_name}-docs

%description doc
Documentation for Hbase

%package rest
Summary: The Apache HBase REST gateway
Group: System/Daemons
Requires: %{component_name}%{soft_package_version} = %{version}
Requires(pre): %{component_name}%{soft_package_version} = %{version}

%if  %{?suse_version:1}0
# Required for init scripts
Requires: insserv
%endif

%if  0%{?mgaversion}
# Required for init scripts
Requires: initscripts
%endif

# CentOS 5 does not have any dist macro
# So I will suppose anything that is not Mageia or a SUSE will be a RHEL/CentOS/Fedora
%if %{!?suse_version:1}0 && %{!?mgaversion:1}0
# Required for init scripts
Requires: /lib/lsb/init-functions
%endif


%description rest
The Apache HBase REST gateway

%prep
%setup -n %{component_name}-%{hbase_base_version}-src

#BIGTOP_PATCH_COMMANDS

%build
env HBASE_VERSION=%{version} bash %{SOURCE1}

%install
%__rm -rf $RPM_BUILD_ROOT
bash %{SOURCE2} \
	--build-dir=build \
        --stack-home=%{stack_home} \
        --doc-dir=%{doc_hbase} \
        --conf-dir=%{etc_hbase_conf_dist} \
	--prefix=$RPM_BUILD_ROOT

%__install -d -m 0755 $RPM_BUILD_ROOT/%{initd_dir}/

%__install -d -m 0755 $RPM_BUILD_ROOT/%{stack_home}/etc/default/
%__install -m 0644 %{SOURCE5} $RPM_BUILD_ROOT/%{stack_home}/etc/default/%{component_name}

%__install -d -m 0755 $RPM_BUILD_ROOT/%{stack_home}/etc/security/limits.d
%__install -m 0644 %{SOURCE6} $RPM_BUILD_ROOT/%{stack_home}/etc/security/limits.d/%{component_name}.nofiles.conf

%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/log/%{component_name}
%__install -d  -m 0755  %{buildroot}/%{logs_hbase}
ln -s %{_localstatedir}/log/%{component_name} %{buildroot}/%{logs_hbase}/%{component_name}

%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/run/%{component_name}
%__install -d  -m 0755  %{buildroot}/%{pids_hbase}
ln -s %{_localstatedir}/run/%{component_name} %{buildroot}/%{pids_hbase}/%{component_name}

#%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/lib/%{component_name}

for service in %{hbase_services}
do
    init_file=$RPM_BUILD_ROOT/%{initd_dir}/%{component_name}-${service}
    if [[ "$service" = "regionserver" ]] ; then
        # Region servers start from a different template that allows
        # them to run multiple concurrent instances of the daemon
        %__cp %{SOURCE7} $init_file
        %__sed -i -e "s|@INIT_DEFAULT_START@|3 4 5|" $init_file
        %__sed -i -e "s|@INIT_DEFAULT_STOP@|0 1 2 6|" $init_file
        %__sed -i -e "s|@CHKCONFIG@|345 87 13|" $init_file
        %__sed -i -e "s|@HBASE_DAEMON@|${service}|" $init_file
    else
        %__sed -e "s|@HBASE_DAEMON@|${service}|" %{SOURCE3} > ${RPM_SOURCE_DIR}/hbase-${service}.node
        bash %{SOURCE4} ${RPM_SOURCE_DIR}/hbase-${service}.node rpm $init_file
    fi

    chmod 755 $init_file
done

#%__install -d -m 0755 $RPM_BUILD_ROOT/usr/bin

# Pull zookeeper and hadoop from their packages
rm -f $RPM_BUILD_ROOT/%{lib_hbase}/{hadoop,zookeeper,slf4j-log4j12-}*.jar
ln -f -s %{zookeeper_home}/zookeeper.jar $RPM_BUILD_ROOT/%{lib_hbase}

#ln -f -s %{hadoop_home}/client/hadoop-annotations.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-auth.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-common.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-hdfs.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-mapreduce-client-app.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-mapreduce-client-common.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-mapreduce-client-core.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-mapreduce-client-jobclient.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-mapreduce-client-shuffle.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-yarn-api.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-yarn-client.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-yarn-common.jar $RPM_BUILD_ROOT/%{lib_hbase}
#ln -f -s %{hadoop_home}/client/hadoop-yarn-server-common.jar $RPM_BUILD_ROOT/%{lib_hbase}

%pre
getent group hbase 2>/dev/null >/dev/null || /usr/sbin/groupadd -r hbase
getent passwd hbase 2>&1 > /dev/null || /usr/sbin/useradd -c "HBase" -s /sbin/nologin -g hbase -r -d /var/lib/hbase hbase 2> /dev/null || :

%post
%{alternatives_cmd} --install %{etc_hbase_conf} %{component_name}-conf %{etc_hbase_conf_dist} 30

%preun
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{component_name}-conf %{etc_hbase_conf_dist} || :
fi


#######################
#### FILES SECTION ####
#######################
%files 
%defattr(-,hbase,hbase)
%{logs_hbase}
%{pids_hbase}
%{man_dir}
%dir %{initd_dir}


%defattr(-,root,root)
%config(noreplace) %{stack_home}/%{_sysconfdir}/default/hbase
%config(noreplace) %{stack_home}/etc/security/limits.d/hbase.nofiles.conf
%{hbase_home}
%{webapps_hbase}
%config(noreplace) %{etc_hbase_conf_dist}
%exclude %{initd_dir}/hbase-*

%files doc
%defattr(-,root,root)
%doc %{doc_hbase}/


%define service_macro() \
%files %1 \
%attr(0755,root,root)/%{initd_dir}/%{component_name}-%1 \
%post %1 \
chkconfig --add %{component_name}-%1 \
\
%preun %1 \
if [ $1 = 0 ] ; then \
        service %{component_name}-%1 stop > /dev/null 2>&1 \
        chkconfig --del %{component_name}-%1 \
fi \
%postun %1 \
if [ $1 -ge 1 ]; then \
        service %{component_name}-%1 condrestart >/dev/null 2>&1 \
fi
%service_macro master
%service_macro thrift
%service_macro thrift2
%service_macro regionserver
%service_macro rest
