# HI observe

Given an RA-DEC-VEL fits cube, a spectrum will be extracted.

Inspired by https://teuben.github.io/nemo/man_html/hispectrum.1.html for the GradMap 2018 trip to Greenbank.

## Data

The original data described in https://teuben.github.io/nemo/man_html/hi.5.html seem to have been lost.

* "BL" survey : ftp://cdsarc.u-strasbg.fr/pub/cats/VIII/28 (GLON-GLAT slices in FELO)
* BL.fits : handcrafted from the BL survey
* LDS: http://cdsarc.u-strasbg.fr/cgi-bin/Cat?VIII/54 (VELO-GLAT slices in GLON)
* LAB: http://cdsarc.u-strasbg.fr/viz-bin/cat/VIII/76 (has a useful lab.fit GLON-GLAT-VELO cube)
* LAB.fits: see ftp://cdsarc.u-strasbg.fr/pub/cats/VIII/76/lab.fit.gz
* some ancient links:  http://www.sao.ru/cats/~satr/DOC/RADIO-ADC.html 

## Possible future improvements:

* Greenbank 40ft mode:  allow extracting at oblique angles in RA-VEL plane
* deal with cubes where VEL is FREQ


