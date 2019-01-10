#

LAB.fits:
	wget ftp://cdsarc.u-strasbg.fr/pub/cats/VIII/76/lab.fit.gz
	gunzip lab.fit.gz
	mv lab.fit LAB.fits
