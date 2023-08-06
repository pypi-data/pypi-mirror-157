# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -q
SPHINXBUILD   = sphinx-build

INDIR	      = .
HTMLDIR	      = build/html
PAGESDIR      = ../pages/PyLit

# Internal variables.
ALLSPHINXOPTS   = -d build/doctrees $(SPHINXOPTS) $(INDIR)

.PHONY: examples help clean html web pickle htmlhelp latex changes linkcheck pages

logo/pylit-bold-framed.png: logo/pylit-bold-framed.svg
	inkscape --export-png=logo/pylit-bold-framed.png logo/pylit-bold-framed.svg

examples/pylit.py.txt: ../pylit.py
	pylit ../pylit.py examples/pylit.py.txt

examples/pylit_test.py.txt: ../test/pylit_test.py
	pylit --comment-string='## ' ../test/pylit_test.py examples/pylit_test.py.txt

examples/conf.py.txt: conf.py
	pylit conf.py examples/conf.py.txt

examples: examples/pylit.py.txt examples/pylit_test.py.txt examples/conf.py.txt

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  pickle    to make pickle files"
	@echo "  json      to make JSON files"
	@echo "  htmlhelp  to make HTML files and a HTML help project"
	@echo "  latex     to make LaTeX files"
	@echo "  changes   to make an overview over all changed/added/deprecated items"
	@echo "  linkcheck to check all external links for integrity"
	@echo "  pages     to move the HTML files to ../pages/PyLit/"

clean:
	-rm -rf build/*

html:   examples logo/pylit-bold-framed.png
	echo $(INDIR)
	mkdir -p $(HTMLDIR) build/doctrees
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(HTMLDIR)
	@echo
	@echo "Copying some source files"
	cp $(INDIR)/download/pylit $(HTMLDIR)/download/
	cp $(INDIR)/examples/*.txt $(HTMLDIR)/examples/
	cp $(INDIR)/examples/*.py  $(HTMLDIR)/examples/
	cp $(INDIR)/examples/*.sty $(HTMLDIR)/examples/
	# cp $(INDIR)/examples/*.css $(HTMLDIR)/examples/
	cp $(INDIR)/tutorial/*.py  $(HTMLDIR)/tutorial/
	cp $(INDIR)/tutorial/*.py.txt $(HTMLDIR)/tutorial/

	@echo
	@echo "Build finished. The HTML pages are in $(HTMLDIR)."

pickle:
	mkdir -p build/pickle build/doctrees
	$(SPHINXBUILD) -b pickle $(ALLSPHINXOPTS) build/pickle
	@echo
	@echo "Build finished; now you can process the pickle files."

web: pickle

json:
	mkdir -p build/json build/doctrees
	$(SPHINXBUILD) -b json $(ALLSPHINXOPTS) build/json
	@echo
	@echo "Build finished; now you can process the JSON files."

htmlhelp:
	mkdir -p build/htmlhelp build/doctrees
	$(SPHINXBUILD) -b htmlhelp $(ALLSPHINXOPTS) build/htmlhelp
	@echo
	@echo "Build finished; now you can run HTML Help Workshop with the" \
	      ".hhp project file in build/htmlhelp."

latex:
	mkdir -p build/latex build/doctrees
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) build/latex
	@echo
	@echo "Build finished; the LaTeX files are in build/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

changes:
	mkdir -p build/changes build/doctrees
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) build/changes
	@echo
	@echo "The overview file is in build/changes."

linkcheck:
	mkdir -p build/linkcheck build/doctrees
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) build/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in build/linkcheck/output.txt."

pages: html
	cp $(HTMLDIR)/*.html $(HTMLDIR)/*.js $(PAGESDIR)
	cp -r $(HTMLDIR)/_static $(HTMLDIR)/download \
	$(HTMLDIR)/examples $(HTMLDIR)/tutorial $(PAGESDIR)
