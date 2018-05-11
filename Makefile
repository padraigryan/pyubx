tests:
	make -C test

readme:
	grip  -b README.md &

help:
	./rtl_utils.py -h
