.PHONY: all include clean

HTMLDIR = html
DATADIR = data
SCRIPTDIR = script
INCLUDEDIR = include

TOURNAMENTS += msi-2017
TOURNAMENTS += msi-2018
TOURNAMENTS += worlds-2017

TARGETS = $(addprefix $(HTMLDIR)/,$(addsuffix .html,$(TOURNAMENTS)))

all: include $(TARGETS)

include:
	cp -r $(INCLUDEDIR)/* $(HTMLDIR)

$(TARGETS): $(HTMLDIR)/%.html: $(DATADIR)/%.yaml $(SCRIPTDIR)/%.py
	python $(SCRIPTDIR)/$*.py < $(DATADIR)/$*.yaml > $@

clean:
	$(RM) -r $(HTMLDIR)/*
