.PHONY: all include clean
.DELETE_ON_ERROR:

HTMLDIR = html
DATADIR = data
SCRIPTDIR = script
INCLUDEDIR = include

TOURNAMENTS += msi-2015 msi-2016 msi-2017 msi-2018
TOURNAMENTS += worlds-2017

TARGETS = $(addprefix $(HTMLDIR)/,$(addsuffix .html,$(TOURNAMENTS)))

all: include $(TARGETS)

include:
	cp -r $(INCLUDEDIR)/* $(HTMLDIR)

$(TARGETS): $(HTMLDIR)/%.html: $(DATADIR)/%.yaml $(SCRIPTDIR)/%.py
	python $(SCRIPTDIR)/$*.py < $(DATADIR)/$*.yaml > $@

clean:
	$(RM) -r $(HTMLDIR)/*
