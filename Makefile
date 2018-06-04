.PHONY: all static clean
.DELETE_ON_ERROR:

SHELL = bash
HTMLDIR = html
DATADIR = data
SCRIPTDIR = script
STATICDIR = static

TOURNAMENTS += worlds-2015 worlds-2016 worlds-2017
TOURNAMENTS += msi-2015 msi-2016 msi-2017 msi-2018
TOURNAMENTS += lms-2016 lms-2017

TARGETS = $(addprefix $(HTMLDIR)/,$(addsuffix .html,$(TOURNAMENTS)))

all: static $(TARGETS) $(HTMLDIR)/index.html

static $(TARGETS) $(HTMLDIR)/index.html: | $(HTMLDIR)

$(HTMLDIR):
	mkdir -p $(HTMLDIR)

static:
	cp -r $(STATICDIR)/* $(HTMLDIR)

$(TARGETS): $(HTMLDIR)/%.html: $(DATADIR)/%.yaml $(SCRIPTDIR)/%.py
	python $(SCRIPTDIR)/$*.py < $(DATADIR)/$*.yaml > $@

$(HTMLDIR)/index.html: $(DATADIR)/index.yaml $(SCRIPTDIR)/index.py | $(TARGETS)
	python $(SCRIPTDIR)/index.py $(HTMLDIR) < $(DATADIR)/index.yaml > $@

clean:
	$(RM) -r $(HTMLDIR)
