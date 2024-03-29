Summary: Utilities for the IBM Power Linux RAID adapters
Name: iprutils
Version: 2.4.4
Release: 1
License: CPL
Group: System Environment/Base
Vendor: IBM
URL: http://sourceforge.net/projects/iprdd/
Source0: iprutils-%{version}-src.tgz
BuildRoot: %{_tmppath}/%{name}-root

%description
Provides a suite of utilities to manage and configure SCSI devices
supported by the ipr SCSI storage device driver.

%prep
%setup -q -n %{name}

%build
make

%install
if [ -d %{_unitdir} ]; then
	make INSTALL_MOD_PATH=$RPM_BUILD_ROOT install
	install -d $RPM_BUILD_ROOT/%{_unitdir}
	install -m 644 systemd/iprinit.service $RPM_BUILD_ROOT/%{_unitdir}/iprinit.service
	install -m 644 systemd/iprdump.service $RPM_BUILD_ROOT/%{_unitdir}/iprdump.service
	install -m 644 systemd/iprupdate.service $RPM_BUILD_ROOT/%{_unitdir}/iprupdate.service
else
	make INSTALL_MOD_PATH=$RPM_BUILD_ROOT install
	install -d $RPM_BUILD_ROOT/%{_sysconfdir}/init.d
	install -m 755 init.d/iprinit $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/iprinit
	install -m 755 init.d/iprdump $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/iprdump
	install -m 755 init.d/iprupdate $RPM_BUILD_ROOT/%{_sysconfdir}/init.d/iprupdate
fi

install -d $RPM_BUILD_ROOT/%{_sysconfdir}/ha.d
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/ha.d/resource.d
install -m 755 init.d/iprha $RPM_BUILD_ROOT/%{_sysconfdir}/ha.d/resource.d/iprha

%ifarch ppc ppc64
%post
# if the system is using systemd
if [ -d %{_unitdir} ]; then
	if [ $1 = 2 ]; then
		echo "Restarting iprutils services"
		/usr/bin/systemctl restart iprinit.service > /dev/null 2>&1
		/usr/bin/systemctl restart iprupdate.service > /dev/null 2>&1
		/usr/bin/systemctl restart iprdump.service > /dev/null 2>&1
	else
		/usr/bin/systemctl daemon-reload > /dev/null 2>&1
		/usr/bin/systemctl enable iprinit.service > /dev/null 2>&1
		/usr/bin/systemctl enable iprdump.service > /dev/null 2>&1
		/usr/bin/systemctl enable iprupdate.service > /dev/null 2>&1
	fi

# if the system is not using systemd
else
	if [ $1 = 2 ]; then
		echo "Restarting iprutils services"
		%{_sysconfdir}/init.d/iprdump restart  > /dev/null 2>&1
		%{_sysconfdir}/init.d/iprupdate restart  > /dev/null 2>&1
		%{_sysconfdir}/init.d/iprinit restart  > /dev/null 2>&1
	elif [ -f /sbin/chkconfig ]; then
		/sbin/chkconfig --add iprinit > /dev/null 2>&1
		/sbin/chkconfig --add iprdump > /dev/null 2>&1
		/sbin/chkconfig --add iprupdate > /dev/null 2>&1
		/sbin/chkconfig iprinit on > /dev/null 2>&1
		/sbin/chkconfig iprdump on > /dev/null 2>&1
		/sbin/chkconfig iprupdate on > /dev/null 2>&1
	else
		/usr/lib/lsb/install_initd %{_sysconfdir}/init.d/iprinit
		/usr/lib/lsb/install_initd %{_sysconfdir}/init.d/iprdump
		/usr/lib/lsb/install_initd %{_sysconfdir}/init.d/iprupdate
	fi
fi
%endif

%ifarch ppc ppc64
%preun
# disable services if the system is using systemd
if [ -d %{_unitdir} ]; then
        if [ $1 = 0 ]; then
                echo "Restarting iprutils services"
                /usr/bin/systemctl stop iprinit.service > /dev/null 2>&1
                /usr/bin/systemctl stop iprupdate.service > /dev/null 2>&1
                /usr/bin/systemctl stop iprdump.service > /dev/null 2>&1
	else
                /usr/bin/systemctl disable iprinit.service > /dev/null 2>&1
                /usr/bin/systemctl disable iprdump.service > /dev/null 2>&1
                /usr/bin/systemctl disable iprupdate.service > /dev/null 2>&1
        fi

# disable services if the system is *not* using systemd
elif [ $1 = 0 ]; then
	%{_sysconfdir}/init.d/iprdump stop  > /dev/null 2>&1
	%{_sysconfdir}/init.d/iprupdate stop  > /dev/null 2>&1
	%{_sysconfdir}/init.d/iprinit stop  > /dev/null 2>&1

	if [ -f /sbin/chkconfig ]; then
		/sbin/chkconfig --del iprinit > /dev/null 2>&1
		/sbin/chkconfig --del iprdump > /dev/null 2>&1
		/sbin/chkconfig --del iprupdate > /dev/null 2>&1
	else
		/usr/lib/lsb/remove_initd %{_sysconfdir}/init.d/iprdump
		/usr/lib/lsb/remove_initd %{_sysconfdir}/init.d/iprupdate
		/usr/lib/lsb/remove_initd %{_sysconfdir}/init.d/iprinit
	fi
fi
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%if %{?_unitdir:1}%{!?_unitdir:0}
	%{_unitdir}/*
%else
	%{_sysconfdir}/init.d/*
%endif
%doc README LICENSE
/sbin/*
%{_mandir}/man*/*
%{_sysconfdir}/ha.d/resource.d/iprha

%changelog
* Tue Sep 8 2014 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.4.4
- Release 2.4.4
- Add support to catch cache hit
- Change the filesnameof firmware to be case insentive.
* Tue Sep 2 2014 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.4.3
- Release 2.4.3
- On PowerNV, some of IOAs showed the wrong physical location
- Read Intensive SDs are not showed up in iprconifg
- Capacity is not reported for JBOD disk greater than 2TB
- Add code for supporting DVD/Tape hotplug
- allow systemd dameons to be activated laster during boot
- add DVD/Tape support in dispaly hardware staut menu
* Tue Jun 10 2014 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.4.2
- Release 2.4.2
- Creation of systemd files for the ipr daemons and proper changes on the spec
  file
- Adds three new CLI APIs: query-array/device/location
- Doesn't show "Redusant Paths" in dual config<LE>
- Couldn't create iprudmp file
- allow iprconfig to load sg module
- Segmentation fault when rebuild an array
- Fix blan space on array member strings
* Tue Apr 08 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.4.1
- Release 2.4.1
- Avoid bashisms
- remove libpci dependency
- Failed to write attribute: delte when hot removing disks
- segment fault when trying to show details of missing devices
* Fri Feb 07 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.4.0
- Release 2.4.0
- Eliminate libsysfs dependency
* Fri Feb 07 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.3.18
- Release 2.3.18
- array start enhancement patch
- compliation fails on ununtu
* Fri Feb 01 2014 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.3.17
- Release 2.3.17
- creating an array fails for T2 disks.
- Several fixes for LE system.
- Enable actie/active by default
* Tue Nov 05 2013 Wen Xiong<wenxionglinux.vnet.ibm.com> 2.3.16
- Release 2.3.16
- Fixes a bug for 4K bytes/sector disks in iprutils
- Fixes a bug for disk hot swap in VSES on P8
- Release 2.3.15
- Add support for 4K bytes/sector disks in iprutils
- Release 2.3.14
- Fixes stale information after hot plug a disk into an array
- Segmentation fault when removing a disk with hot spare disk
- Fxied sysfs error when updating microcode
- Fixes the platform location issue for Tres drawer
- Fix hop count defines
- Release 2.3.13
- Fixes Platform Location for 32bit adapter.
- Adds support for optical devices.
- Fixes platform location for disks.
- Changes %post and %preun sections of spec file.
- Fixes release date on the spec file.
* Fri Sep 05 2012 Wen Xiong <wenxiong@linux.vnet.ibm.com> 2.3.12
- Release 2.3.12
- Addes supporting suspend/resume utility for BlueHawk.
- Fixes raid array delete error.
* Tue Jun 12 2012 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.11
- Release 2.3.11
- Fixes deleting an array logs I/O errors.
- Fixes buffer overflow in disk details.
- Fixes wrong status on an array for the secondary controller.
- Fixes add_string_to_body() for non-interactive interface.
- Fixes IOA asymmetric access mode change.
- Gets location code when SES page 4 is unavailable.
- Fixes physical location error if disk is vses disk.
* Mon Apr 02 2012 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.10
- Release 2.3.10
- Displays Hardware Location Code for disk/expander.
- Changes concurrent maintenance GUI to 3 ways toggle.
- Changes README for concurrent maintenance command line.
- Adds structures and functions for query resource paths aliases.
- Fixes a bug in suspend/resume device bus.
- Supports concurrent maintenance for 64bit adapter.
- Supports not physical remove disk.
- Fixes header problem when query-remove/add-device.
- Sometimes receive diag failed at first time after update adapter firmware.
- If the disk in a RAID, iprutils itself has to delete sysfs name for secondary
  adapter.
- Old drawers don't support query page 4 for physical location.
- Adds display sas path detail for 64bit adapter.
- Fixes GUI version of raid consistency check.
- Adds new chip details entries.
- Fixes SES microcode update failures.
- Fixes SES microcode image version on CLI.
- Adds a flag to raid create command for known zeroed drives.
* Fri Dec 16 2011 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.9
- Release 2.3.9
- Fixes disks and arrays status.
- Uses C4 inquiry page for DRAM size.
- Sets allow_restart to zero before raid delete.
- Fixes raid consistency check for 64 bit adapters.
- Fixes compile warning.
- Updates queue depth values.
* Thu Nov 24 2011 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.8
- Release 2.3.8
- Adds support for FPGA updates.
- Bumps up number of command status records.
- Only uses primary adapter for initialize and format disk task.
- Fixes check for hotspare devices.
- Removes unnecessary call to find_dev().
* Thu Aug 18 2011 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.7
- Release 2.3.7
- Adds support for vset device asymmetric config.
- Fixes display details for array devices.
- Increases buffer size for new adapter config data.
- Fixes query command status functionality.
* Thu Jul 14 2011 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.6
- Release 2.3.6
- Fixes segmentation fault when qac is not available.
- Fixes serial number comparison.
* Thu Jun 16 2011 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.5
- Release 2.3.5
- Fixes suspend and resume device bus commands.
* Wed Apr 27 2011 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.4
- Release 2.3.4
- Fixes data types for C4 page definition.
- Fixes setting qac cdb[3] and rename ipr_is_array_record.
- Fixes array migration funcionality.
- Increases maximum dump size.
* Mon Mar 07 2011 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.3.3
- Release 2.3.3
- Adds initial support for sis64 asymmetric access changes.
- Fixes segmentation faults when trying to display certain information.
- Fixes some file permissions and a compilation warning.
* Thu Nov 18 2010 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.2
- Release 2.3.2
- Fixes code incompatibility with libsysfs version 1.
- Changes get_scsi_max_xfer_len return value.
* Fri Nov 12 2010 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.1
- Release 2.3.1
- Fixes display of empty slots.
- Fixes IOA description indentation.
- Adds Resource Path display for SIS64 devices.
- Adds support for the new live dump functionality.
- Fixes mode sense page24 for little endian architectures.
- Fixes battery info for little endian architectures.
* Fri Aug 12 2010 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.3.0
- Release 2.3.0
- Fixes type of pointers provided to scandir.
- Fixes buffer overflow when the SCSI Host ID is equal or greater than 1000.
- Fixes function names on comments in iprlib.c.
- Fixes memory leak when ioctl() returns EINVAL.
- Adds support to identify sis64 capability.
- Adds support for new sysfs attributes.
- Adds support for type 3 QAC command.
- Adds support for type 3 records.
* Mon May 10 2010 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.2.21
- Release 2.2.21
- Fixes firmware image files left open after getting firmware level.
- Changes IOA DRAM size display from hex to decimal base.
- Handles SG_IO ioctl error with older distros which caused disk microcode
  download to fail with JBOD's.
* Tue Apr 07 2010 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.2.20
- Release 2.2.20
- Adds resource address parsing based on encoding format flag.
* Fri Mar 19 2010 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.2.19
- Release 2.2.19
- Fixes platform location display on blades.
* Fri Oct 30 2009 Kleber Sacilotto de Souza <klebers@linux.vnet.ibm.com> 2.2.18
- Release 2.2.18
- Changes the default write buffer mode for writing to SES devices.
- Fixes the CLI show-details command for SES devices.
- Comments out the get_write_buffer_dev() routine to suppress compilation
  warnings as it is not being used at the moment.
- Fixes the Platform Location Information display for hotplug adapters and
  displays the information for non-hotplug adapters.
- Fixes the indentation problem when IOA host number is equal to or greater
  than 10.
* Wed Sep 16 2009 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.17
- Release 2.2.17
- Fixes a NULL pointer dereference which caused the daemons to silently fail.
* Fri Aug 14 2009 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.16
- Release 2.2.16
- Fixes a bug where CLI raid create is broken.
- Fixes several potential memory leak problems.
- Adds man page entries for the disable cache query and command.
* Tue Jun 30 2009 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.15
- Release 2.2.15
- Fixes a bug where cache reclaim can time out too soon.
- Fixes some problems with the disable caching support.
* Tue Apr 07 2009 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.14
- Release 2.2.14
- Add support for disabling IOA caching.
- Remove #include of <linux/byteorder/swab.h> as it is not used.
- Allow giving a relative path for a microcode image file when doing an upgrade
  from the command line.
- Add support for SSD drives.
* Mon Nov 17 2008 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.13
- Release 2.2.13
- Additional fixes for the active-active functionality.
- Fixes for iprdump to recognize a /sys/devices path.
* Thu Oct 23 2008 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.12
- Release 2.2.12
- Additional GUI support and fixes for the active-active functionality.
- Fixes for CLI RAID create and delete.
* Fri Sep 26 2008 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.11
- Release 2.2.11
- Add support for the active-active functionality.
* Wed Aug 20 2008 Wayne Boyer <wayneb@linux.vnet.ibm.com>
- Fixed a compilation failure on small endian systems.
* Wed Aug 13 2008 Wayne Boyer <wayneb@linux.vnet.ibm.com> 2.2.10
- Release 2.2.10
- Add support for the array migration functionality.
* Wed May 14 2008 Tseng-Hui Lin <tsenglin@us.ibm.com>
- Under heavy traffic, download microcode to a disk through /dev/sgX
  may get -ENOMEM SG_IO ioctl. Change to use /dev/sdX. Fall back
  to /dev/sgX if: (1) /dev/sdX does not exist or (2) max_sectors_kb
  is not set large enough for microcode download.
* Thu Apr 09 2008 Tseng-Hui Lin <tsenglin@us.ibm.com> 2.2.9
- Release 2.2.9
- Do not save preferred primary attribute to fix an infinite failover
  problem in HA two system RAID configuration.
* Thu Sep 20 2007 Brian King <brking@us.ibm.com> 2.2.8
- Release 2.2.8
* Mon Aug 27 2007 Brian King <brking@us.ibm.com>
- Add support for setting dual adapter HA mode.
* Thu Jun 21 2007 Brian King <brking@us.ibm.com> 2.2.7
- Fixes for init.d scripts to fix problems installing them on
  some systems.
* Wed Jun 13 2007 Brian King <brking@us.ibm.com>
- rpm spec file updates
* Tue May 1 2007 Brian King <brking@us.ibm.com> 2.2.6
- Fix iprinit dual initiator failover device rescanning code.
* Wed Apr 25 2007 Brian King <brking@us.ibm.com>
- Add iprha init.d script to enable/disable primary adapter mode
  for dual initiator configs.
* Fri Apr 13 2007 Brian King <brking@us.ibm.com>
- Add adapter config option in iprconfig for setting primary/secondary
  adapter in dual adapter environment.
* Mon Mar 19 2007 Brian King <brking@us.ibm.com>
- Add iprconfig option to display SAS dual pathing information.
* Mon Mar 12 2007 Brian King <brking@us.ibm.com>
- Increase time waiting for new devices to show up in
  iprconfig when doing concurrent add.
* Fri Feb 9 2007 Brian King <brking@us.ibm.com>
- Add filename date to microcode download screen. (Ryan Hong)
- Fix to prevent unnecessarily writing sysfs attributes. (Ryan Hong)
* Tue Feb 6 2007 Brian King <brking@us.ibm.com>
- Return standard error code according to send_dev_init() return code.
* Mon Feb 5 2007 Brian King <brking@us.ibm.com>
- Fix incorrect memory free in analyze log menus.
* Wed Jan 10 2007 Brian King <brking@us.ibm.com>
- Fix send diagnostics buffer transfer length to be only what was
  received in the receive diagnostics. Fixes disk hotplug on
  some SAS disk enclosures.
* Thu Jan 4 2007 Brian King <brking@us.ibm.com>
- Sourceforge patch 1627673: iprutils fix to buffer overflow
- Add checking to iprconfig command "set-qdepth" input queue
  depth value. If the given value is larger than 255, fail the command.
- Fix a bug in which the iprconfig command "raid-create"
  may create an illegal queue depth value to the ipr
  config file.
* Thu Jan 4 2007 Brian King <brking@us.ibm.com>
- Sourceforge patch 1627672: iprutils fix to buffer overflow
- Fix a bug in which the iprconfig command "raid-create"
  may create an illegal queue depth value to the ipr
  config file.
* Wed Nov 29 2006 Brian King <brking@us.ibm.com>
- Fixes for SES microcode download on SAS.
* Mon Nov 20 2006 Brian King <brking@us.ibm.com>
- Change to handle UA responses in the JBOD iprinit sequence.
* Thu Nov 16 2006 Brian King <brking@us.ibm.com>
- Fix segfault in iprconfig if /var/log does not exist.
- Allow IOA microcode download to a secondary IOA.
- Fix to prevent errors during SAS SES microcode download.
* Tue Oct 10 2006 Brian King <brking@us.ibm.com>
- Add a couple utility functions for SAS
	ipr_query_sas_expander_info
	ipr_query_res_redundancy_info
* Wed Sep 27 2006 Brian King <brking@us.ibm.com> 2.2.3
- Fix SAS disk hotplug dual path bug.
* Tue Sep 12 2006 Brian King <brking@us.ibm.com>
- Change default QERR setting for SAS to 0.
* Tue Sep 12 2006 Brian King <brking@us.ibm.com> 2.2.2
- Fix iprconfig set-format-timeout.
* Mon Sep 11 2006 Brian King <brking@us.ibm.com> 2.2.1
* Fri Sep 8 2006 Brian King <brking@us.ibm.com>
- Reduce default JBOD queue depth to 3.
- Fix iprconfig -c set-bus-speed.
* Wed Aug 23 2006 Brian King <brking@us.ibm.com>
- Fix a race condition with hotplug events which could
  cause the ipr daemons to run before newly added devices
  are completed added to the system.
* Wed Aug 9 2006 Brian King <brking@us.ibm.com>
- Fix a segfault in iprdbg when using the macro function
* Tue Jul 25 2006 Brian King <brking@us.ibm.com> 2.2.0
- Fix for command line SES microcode update.
* Mon May 8 2006 Brian King <brking@us.ibm.com>
- Use IOA's default format timeout for AF DASD instead
  of using a hard coded default.
- Remove RAID support for some older drives that should never
  have been supported.
* Mon May 1 2006 Brian King <brking@us.ibm.com>
- Add support to iprinit for it to handle disks going
  from JBOD <-> AF format across an adapter reset. When this
  is detected, iprinit will now attempt to delete the disk
  and then rescan that slot.
- Fixed an ncurses screen drawing bug which resulted in the
  screen getting paged down if the cursor was on the last item
  on the screen and 't' was pressed to toggle the display.
- Added disk concurrent maintenance support for handling
  dual pathed SAS disks.
* Fri Mar 17 2006 Brian King <brking@us.ibm.com>
- Improve iprdbg's logging
* Thu Mar 16 2006 Brian King <brking@us.ibm.com>
- Print better status for devices when IOA is offline/dead.
* Tue Mar 14 2006 Brian King <brking@us.ibm.com>
- Fix to allow for compiling with libsysfs 2.0.0
* Tue Mar 14 2006 Brian King <brking@us.ibm.com> 2.1.4
- Concurrent maintenance fix for certain iSeries
  enclosures which would result in non existent
  drive slots being displayed in iprconfig.
* Wed Mar 8 2006 Brian King <brking@us.ibm.com>
- Remove some redundant code in disk hotplug path
* Thu Mar 2 2006 Brian King <brking@us.ibm.com>
- Fixup status of RAID 10 arrays to print a better status
  under multiple failure scenarios.
* Thu Feb 24 2006 Brian King <brking@us.ibm.com> 2.1.3
- Prevent duplicate mode sense commands from being issued.
- More uevent handling improvements.
- Automatically create hotplug directory if it doesn't
  already exist so adapter microcode update works.
* Thu Feb 9 2006 Brian King <brking@us.ibm.com>
- Improve robustness of uevents failure handling. Fall
  back to polling method if needed. 
* Fri Feb 3 2006 Brian King <brking@us.ibm.com>
- Auxiliary cache adapter fixes.
* Fri Jan 27 2006 Brian King <brking@us.ibm.com>
- Fix iprconfig -c update-ucode to properly report an
  error if the wrong microcode level is specified.
* Mon Jan 23 2006 Brian King <brking@us.ibm.com>
- Fixed a compiler issue.
* Fri Jan 20 2006 Brian King <brking@us.ibm.com>
- Fixed a bug in iprconfig query-raid-create that prevented
  JBOD candidates from being displayed if there were no
  AF candidates as well.
* Thu Jan 5 2006 Brian King <brking@us.ibm.com> 2.1.2
- Make iprupdate return success/failure indication
  when invoked with --force.
* Tue Jan 3 2006 Brian King <brking@us.ibm.com>
- Concurrent maintenance fix for 7031-D24/T24.
* Tue Dec 20 2005 Brian King <brking@us.ibm.com> 2.1.1
- Fix compile error in iprconfig
* Thu Dec 18 2005 Brian King <brking@us.ibm.com> 2.1.0
- Updates for aux cache IOAs
- Updates for SAS adapters
- Misc fixes for new iprconfig command line options
* Wed Dec 7 2005 Brian King <brking@us.ibm.com>
- Add command line options to iprconfig to perform virtually
  every iprconfig function available in the ncurses interface.
* Tue Nov 15 2005 Brian King <brking@us.ibm.com> 2.0.15.6
- Fix concurrent maintenance with disk drawers reporting
  multiple SES devices on the same SCSI bus.
* Fri Oct 7 2005 Anton Blanchard <anton@samba.org>
- Fix string length calculation in ipr_get_hotplug_dir
* Wed Aug 17 2005 Brian King <brking@us.ibm.com> 2.0.15.4
- Fix a couple of uninitialized variable compile errors
* Wed Jul 27 2005 Brian King <brking@us.ibm.com> 2.0.15.3
- Fix: iprconfig: IOA microcode update would leave AF DASD
  (disks that are in disk arrays) in a state where they were
  no longer tagged queueing. Fix iprconfig to run iprinit on the
  adapter after a microcode download to ensure all attached devices
  are properly setup after a microcode download.
- Fix iprinit: If an IOA was reset for some reason at runtime,
  this would cause AF DASD devices to get tagged queueing turned
  off and it would never get turned back on. Change iprinit to
  detect this and turn tagged queueing back on if this happens.
- Changing the queue depth for a disk array was broken. Fix iprinit
  to properly restore the queue depth from the ipr configuration file.
- Fix iprconfig to handle disk format failures better
- Fix potential iprutils segfaults when iterating over disk arrays
* Wed Jun 1 2005 Brian King <brking@us.ibm.com> 2.0.15.1
- Fix iprconfig Analyze Log options
* Wed May 18 2005 Brian King <brking@us.ibm.com> 2.0.15
- Clarify format options
- Setup mode page 0 for IBM drives to ensure command aging is
  enabled. This ensures commands are not starved on some drives.
- Fix so that iprdump properly names dump files once 100 dumps
  have been made.
- Make iprconfig handle failures of scsi disk formats better
- Fix iprconfig Set root kernel message log directory menu
- Properly display RAID level on all iprconfig screens
- Don't disable init.d daemons on an rpm -U
* Tue Apr 12 2005 Brian King <brking@us.ibm.com> 2.0.14.2
- Fixed bug preventing disk microcode update from working.
* Mon Apr 4 2005 Brian King <brking@us.ibm.com>
- Add ability to force RAID consistency check
* Mon Mar 25 2005 Brian King <brking@us.ibm.com> 2.0.14.1
- Removed mention of primary/secondary adapters in some error
  screens since multi-initiator RAID is not supported and the
  messages will just cause confusion.
* Mon Mar 24 2005 Brian King <brking@us.ibm.com>
- iprconfig: During disk hotplug, wait for sd devices to show
  up. Fixes errors getting logged by iprconfig during hotplug.
* Mon Mar 23 2005 Brian King <brking@us.ibm.com>
- iprconfig: Fix cancel path on concurrent add/remove of disks
- Don't display current bus width and speed for SAS disks
* Mon Mar 21 2005 Brian King <brking@us.ibm.com>
- Fix scoping bug caught by gcc 4.0.
* Fri Mar 18 2005 Brian King <brking@us.ibm.com>
- Stop iprupdate from continually logging errors for adapters with
  backlevel adapter firmware.
* Mon Mar 7 2005 Brian King <brking@us.ibm.com> 2.0.14
- Add support for non-interactive array creation and deletion through
  iprconfig.
- Use kobject_uevent notifications instead of polling if the kernel
  supports it.
- Fix iprconfig to set the actual queue depth for advanced function disks
- Allow user to force tagged queuing on to drives that do not support
  QERR=1.
- Fix handling of medium format corrupt drives for drives
- iprconfig: Download microcode. Fix blank screen when displaying
  lots of microcode images.
- Fix iprinit to wait for scsi generic devices to show up in case we are
  racing with hotplug. Fixes the following error:
      0:255:0:0: Mode Sense failed. rc=1, SK: 5 ASC: 24 ASCQ: 0
- Add "known to be zeroed" tracking to iprconfig to drastically reduce the
  time required to create a RAID array when starting with 512 formatted disks
- Add ability to query multi-adapter status for dual initiator RAID configs
- Add ability to set "preferred primary" adapter when running dual initiator RAID configs
- Add iprconfig screen to display dual adapter status for dual initiator RAID configs
- Prevent RAID configuration from occurring on "secondary" adapter in dual initiator RAID configs
- Use /dev/sd for SG_IO instead of /dev/sg when possible
- Set QERR=3 rather than 1 for multi-initiator configurations
- Set TST=1 for multi-initiator configurations
- Allow Format device for JBOD function to work for JBOD adapters
- Fix handling of dead adapters in all of iprutils.
- Fix iprconfig RAID start bug for systems with multiple RAID adapters.
- Fix iprconfig RAID include bug for systems with multiple RAID adapters.
- Fix failing array add device due to race condition with iprinit.
* Tue Oct 5 2004 Brian King <brking@us.ibm.com> 2.0.13
- Improve iprupdate error logs to indicate where to download microcode from.
- Set default tcq queue depth for AS400 disks to 16.
- Don't log errors in iprdump if CONFIG_IPR_DUMP not enabled in the kernel
- Fix sysfs parsing to handle new sdev target kernel change
- Rescan JBOD devices following recovery format to make the device usable if
  it was originally in an unsupported sector size.
- Display correct adapter serial number in iprconfig.
- Support for microcode download to new adapters.
- Support for iSeries disk microcode update using microcode images from
  the pSeries microcode website.
* Fri Jun 11 2004 Brian King <brking@us.ibm.com> 2.0.12
- Fix bug preventing ucode download to iSeries disks from working
* Thu Jun 10 2004 Brian King <brking@us.ibm.com> 2.0.11
- Fix segmentation fault in _sg_ioctl that was causing a silent
  failure of microcode update to disks. The microcode update would
  fail, but no error would be logged. The seg fault was in a child
  process, so the parent process kept running.
* Thu May 23 2004 Brian King <brking@us.ibm.com> 2.0.10
- Don't let iprdbg sg ioctls be retried.
- Add --force flag to iprconfig to allow user to workaround buggy
  drive firmware.
- Don't initialize read/write protected disks
- Fix some reclaim cache bugs
- Don't setup Mode Page 0x0A if test unit ready fails
* Thu May 2 2004 Brian King <brking@us.ibm.com> 2.0.9
- Add --debug option to all utilities
- Make utilities behave better when ipr is not loaded
- Fix dependencies in init.d scripts
- Only enable init.d scripts on ppc
- Don't log an error if ipr is not loaded
* Mon Apr 28 2004 Brian King <brking@us.ibm.com> 2.0.8
- Fix to properly enable init.d scripts when the rpm is installed
- Fix memory leak in code download path
- Increase size of page 0 inquiry buffer so that extended vpd is displayed
- Decrease write buffer timeout to 2 minutes
* Wed Apr 16 2004 Brian King <brking@us.ibm.com> 2.0.7
- Load sg module in init.d scripts if not loaded
- Load sg module in iprconfig if not loaded
* Wed Apr 14 2004 Brian King <brking@us.ibm.com> 2.0.6
- Battery maintenance fixes.
- Fix to properly display failed status for pulled physical disks.
* Tue Apr 6 2004 Brian King <brking@us.ibm.com> 2.0.5
- Battery maintenance fixes.
- Fix init.d scripts to work properly with yast runlevel editor.
- Fix device details screen in iprconfig for Failed array members
- Allow formatting devices even if qerr cannot be disabled 
* Tue Mar 29 2004 Brian King <brking@us.ibm.com> 2.0.4
- Fixed some sysfs calls that changed their calling interfaces
* Tue Mar 17 2004 Brian King <brking@us.ibm.com> 2.0.2-3
- Fixed 
