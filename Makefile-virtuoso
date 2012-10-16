#
# Makefile para ajudar na montagem de um ambiente local para o Virtuoso
# e para subida local de ontologias
#

VIRTUOSO_VERSION := 6.1.6
VIRTUOSO_HOME ?= /usr/local/virtuoso-opensource-$(VIRTUOSO_VERSION)
VIRTUOSO_DB := $(VIRTUOSO_HOME)/var/lib/virtuoso/db
VIRTUOSO_LOAD := $(VIRTUOSO_DB)/ontology
VIRTUOSO_PACKAGE := virtuoso-opensource-$(VIRTUOSO_VERSION).tar.gz
TEMP_DIR := tmp
VIRTUOSO_BUILD_DIR := $(TEMP_DIR)/virtuoso-opensource-$(VIRTUOSO_VERSION)

all: help

help:
	@echo -n $(blue)
	@echo 'USE: make <target>'
	@echo -n $(normal)
	@echo '-------'
	@echo 'Targets'
	@echo '-------'
	@echo '    setup-host-ubuntu....................... Install Virtuoso on Ubuntu'
	@echo '    setup .................................. Setup Virtuoso'
	@echo '    run | start ............................ Start Virtuoso local server'
	@echo '    stop ................................... Stop Virtuoso local server'
	@echo '    status ................................. Show Virtuoso\'s status'
	@echo '    load | base_virtuoso ................... Load ontologys'
	@echo '    clean .................................. Remove Virtuoso local'
	@echo '    cleanlogs .............................. Remove log\'s files'

$(TEMP_DIR)/$(VIRTUOSO_PACKAGE):
	mkdir -p $(TEMP_DIR)
	@echo Downloading the Virtuoso source $(VIRTUOSO_VERSION)
	wget -P $(TEMP_DIR) -c --content-disposition "http://sourceforge.net/projects/virtuoso/files/virtuoso/$(VIRTUOSO_VERSION)/$(VIRTUOSO_PACKAGE)/download"

$(TEMP_DIR)/.configured: $(TEMP_DIR)/$(VIRTUOSO_PACKAGE)
	@echo Opening the Virtuoso package
	tar xzf $(TEMP_DIR)/$(VIRTUOSO_PACKAGE) -C $(TEMP_DIR)
	(cd $(VIRTUOSO_BUILD_DIR); \
		./configure \
			--disable-bpel-vad \
			--disable-demo-vad \
			--disable-fct-vad  \
			--disable-ods-vad  \
			--disable-syncml-vad \
			--disable-tutorial-vad \
			--prefix=$(VIRTUOSO_HOME) \
	)
	touch $(TEMP_DIR)/.configured

unpack: $(TEMP_DIR)/.configured

$(TEMP_DIR)/.built: $(TEMP_DIR)/.configured
	@rm -f $(TEMP_DIR)/.built
	$(MAKE) -C $(VIRTUOSO_BUILD_DIR)
	@touch $(TEMP_DIR)/.built

build: $(TEMP_DIR)/.built

$(VIRTUOSO_HOME)/.installed: $(TEMP_DIR)/.built
	sudo $(MAKE) -C $(VIRTUOSO_BUILD_DIR) install
	sudo sed -i -e 's/^Load[0-9]/;&/' \
		$(VIRTUOSO_HOME)/var/lib/virtuoso/db/virtuoso.ini
	sudo sed -i -e 's/^DirsAllowed.*/&, ./ontology/' \
		$(VIRTUOSO_HOME)/var/lib/virtuoso/db/virtuoso.ini
	sudo mkdir -p $(VIRTUOSO_HOME)/var/lib/virtuoso/db/ontology
	sudo chmod a+rwx $(VIRTUOSO_HOME)/var/lib/virtuoso/db/ontology
	sudo touch $(VIRTUOSO_HOME)/.installed

	sudo cp $(VIRTUOSO_HOME)/var/lib/virtuoso/db/virtuoso.ini $(VIRTUOSO_HOME)/var/lib/virtuoso/db/virtuoso-test.ini
	sudo sed -i -e 's/8890/8891/g' \
		$(VIRTUOSO_HOME)/var/lib/virtuoso/db/virtuoso-test.ini

ifeq ($(origin VIRTUOSO_HOME), file)

install: $(VIRTUOSO_HOME)/.installed

else

$(VIRTUOSO_HOME)/bin/virtuoso-t:
	@echo "EXTERNAL_VIRTUOSO esa definido, mas não encontrei $(VIRTUOSO_HOME)/bin/virtuoso-t"
	@false

install: $(VIRTUOSO_HOME)/bin/virtuoso-t

endif

setup: install

run: setup
	@echo "$(blue)Stating Virtuoso"
	cd $(VIRTUOSO_DB); sudo $(VIRTUOSO_HOME)/bin/virtuoso-t >/dev/null 2>&1

run-test: setup
	@echo "$(blue)Stating Virtuoso"
	sudo $(VIRTUOSO_HOME)/bin/virtuoso-t +config $(VIRTUOSO_DB)/virtuoso-test.ini

test: run-test
	@python example_project/manage.py test --settings=example_project.settings_test
	make stop

start: run

start-test: run-test

stop:
	@echo "$(blue)Stoping Virtuoso"
	$(VIRTUOSO_HOME)/bin/isql -H localhost -U dba -P dba -K 2>/dev/null || true

status:
	@if $(VIRTUOSO_HOME)/bin/isql localhost <<<'status();' &>/dev/null ; then \
		echo "Started" ;\
	else \
		echo "Not started" ;\
	fi

load:
	cap LOADER_OPTS="$(LOADER_OPTS)" ambiente:local action:deploylocal

base_virtuoso: load

clean:
	@echo To remove a local Virtuoso's installatin, use \'make realclean\'

ifeq ($(origin VIRTUOSO_HOME), file)

realclean: stop
	@echo "$(blue)Removing $(TARGET_DIR) e $(VIRTUOSO_HOME)"
	@sleep 5
	sudo rm -rf $(VIRTUOSO_HOME)

else

realclean:
	@echo "$(blue)Your Virtuoso can't be removed, because it not have be installed with this Makefile"

endif
	
cleanlogs:
	rm $(VIRTUOSO_DB)/virtuoso.log

setup-host-ubuntu:
	sudo apt-get update
	sudo apt-get install \
		build-essential \
		autoconf \
		automake \
		libtool \
		make \
		flex \
		bison \
		gawk \
		gperf \
		m4 \
		libssl-dev \
		libxml2-dev

setup-host-mac:
	@for prog in xcodebuild flex bison gawk gperf m4; do \
		which $$prog >/dev/null 2>&1 || (echo "Você precisa ter $$prog instalado para compilar o Virtuoso"; exit 1) \
	done

