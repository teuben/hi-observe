#

LAB.fits:
	wget ftp://cdsarc.u-strasbg.fr/pub/cats/VIII/76/lab.fit.gz
	gunzip lab.fit.gz
	mv lab.fit LAB.fits

BL.fits:
	@echo No easy recipe, manual labor.

# just an example we ran on the GreenBank 40ft when we arrived Jan 5, 2018.
test1: LAB.fits
	./hi-observe.py LAB.fits 83.886 -2.67928
	mv hi-observe.png test1.png

test2: BL.fits
	./hi-observe.py BL.fits 83.886 -2.67928
	mv hi-observe.png test2.png
