ej=ejemplo1

EJEMPLO=../doc/source/$(ej).rst


$(EJEMPLO): $(ej).ipynb
	jupyter-nbconvert $< --to rst --output-dir=../doc/source

