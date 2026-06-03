LATEXMK = latexmk
MAIN = main.tex

.PHONY: pdf clean

pdf:
	$(LATEXMK) -pdf -synctex=1 -interaction=nonstopmode -file-line-error $(MAIN)

clean:
	$(LATEXMK) -C $(MAIN)
