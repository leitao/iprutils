# (C) Copyright 2000, 2001
# International Business Machines Corporation and others.
# All Rights Reserved. This program and the accompanying
# materials are made available under the terms of the
# Common Public License v1.0 which accompanies this distribution.

INCLUDEDIR = -I.
CC = gcc

include version.mk

CFLAGS = -g -Wall $(IPR_DEFINES)
UTILS_VER = $(IPR_MAJOR_RELEASE).$(IPR_MINOR_RELEASE).$(IPR_FIX_LEVEL)
TAR = cd .. && tar -zcpf iprutils-$(UTILS_VER)-src.tgz --exclude CVS --exclude applied-patches --exclude series --exclude txt --exclude pc --exclude patches --exclude debug --exclude *~* iprutils

all: iprconfig iprupdate iprdump iprinit iprdbg docs 

iprconfig: iprconfig.c iprlib.o iprconfig.h
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprconfig iprconfig.c iprlib.o -lform -lpanel -lncurses -lmenu -lsysfs

iprupdate: iprupdate.c iprlib.o
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprupdate iprlib.o iprupdate.c -lsysfs

iprdump:iprdump.c iprlib.o
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprdump iprlib.o iprdump.c -lsysfs

iprinit:iprinit.c iprlib.o
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprinit iprlib.o iprinit.c -lsysfs

iprdbg:iprdbg.c iprlib.o
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprdbg iprlib.o iprdbg.c -lsysfs -lncurses

iprucode:iprucode.c iprlib.o
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprucode iprlib.o iprucode.c -lsysfs

iprlib.o: iprlib.c iprlib.h
	$(CC) $(CFLAGS) $(INCLUDEDIR) -o iprlib.o -c iprlib.c

%.8.gz : %.8
	gzip -f -c $< > $<.gz

%.nroff : %.8
	nroff -man $< > $@

%.ps : %.nroff
	a2ps -B --columns=1 -R -o $@ $<

%.pdf : %.ps
	ps2pdf $< $@

docs : $(patsubst %.8,%.8.gz,$(wildcard *.8))

pdfs : $(patsubst %.8,%.pdf,$(wildcard *.8))

utils: ./*.c ./*.h
	cd ..
	$(TAR)

clean:
	rm -f iprupdate iprconfig iprdump iprinit iprdbg *.o
	rm -f *.ps *.pdf *.nroff *.gz *.tgz *.rpm

install: all
	install -d $(INSTALL_MOD_PATH)/sbin
	install --mode=755 iprconfig $(INSTALL_MOD_PATH)/sbin/iprconfig
	install --mode=755 iprupdate $(INSTALL_MOD_PATH)/sbin/iprupdate
	install --mode=755 iprdump $(INSTALL_MOD_PATH)/sbin/iprdump
	install --mode=755 iprinit $(INSTALL_MOD_PATH)/sbin/iprinit
	install --mode=700 iprdbg $(INSTALL_MOD_PATH)/sbin/iprdbg
	install -d $(INSTALL_MOD_PATH)/usr/share/man/man8
	install iprconfig.8.gz $(INSTALL_MOD_PATH)/usr/share/man/man8/iprconfig.8.gz
	install iprupdate.8.gz $(INSTALL_MOD_PATH)/usr/share/man/man8/iprupdate.8.gz
	install iprdump.8.gz $(INSTALL_MOD_PATH)/usr/share/man/man8/iprdump.8.gz
	install iprinit.8.gz $(INSTALL_MOD_PATH)/usr/share/man/man8/iprinit.8.gz

rpm: *.c *.h *.8
	-make clean
	cd ..
	cp -f spec/iprutils.spec .
	$(TAR)
	mv ../iprutils-$(UTILS_VER)-src.tgz .
	rm -f iprutils.spec
	rpmbuild --nodeps -ts iprutils-$(UTILS_VER)-src.tgz
	cp /home/$(USER)/rpm/SRPMS/iprutils-$(UTILS_VER)-$(IPR_RELEASE).src.rpm .
