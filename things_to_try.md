#  Greenbank 40ft Observing:    things to try out

These are some questions you can tackle using the
[Greenbank40ft notebook](https://github.com/teuben/hi-observe/blob/master/greenbank40ft.ipynb).


1. For the example spectrum in cell [4],
   can you zoom in a bit by looking at the signal near 0 (the baseline).

2. Compare the spectrum from the LAB and BL (the default) surveys at the same location in the sky.
   What's the most obvious difference?  How could you better compare them.

3. Plot a spectrum at the galactic center:  use the coordinate conversion plot (the last page in https://greenbankobservatory.org/wp-content/uploads/2018/02/40-manual.pdf) and find the RA (LST) and DEC of the galactic center.

4. Plot spectra at some selected points in (RA,DEC). Look at the (GLON,GLAT) coordinates and make a table of the peaks and velocities where the peaks occur, e.g. (I'm completely making numbers)

    
       # RA h/m/s DEC   GLON GLAT   PEAK  PEAK_LOCATIONS
         7 00 00  -10    210 -10    800  -200  10 170       # three peaks
         8 30 00  +10    180 +10    600  -100  0            # two locations
         ...


    Some hints:
    * pick a series of points along the galactic plane (GLAT at 0)
    * pick a series of points perpendicular from the plan (GLON the same)
    * can you find points where there is no HI ?

5. To get help on the "HI" functions, use the jupyter notebook method to get help

        HI.greenbank40ft?
   or
   
        help(HI.greenbank40ft)


6. (advanced) The white insert plot in the strip chart plot was done with the BL
survey, which twice as large a resolution from the Greenbank 40ft
stripchart data, so it will look more smooth. In fact, it shows two
peaks, where as the Greenbank data arguably shows three.  If you try
this location with the LAB survey (which is twice as detailed as
Greenbank), can you explain more features?  Hint: look at our old notes
https://github.com/teuben/hi-observe/blob/master/Greenbank40ft-scan.txt


#  Under the hood: Spectral Line Data Cubes

1. Use a FITS viewer (like ds9, QFitsView or CARTA) to view the LAB.fits and/or BL.fits survey.
Learn how to change the contrast so you see more. Learn how to slide through different channels
in the 3rd dimension.

2. (advanced) Both the LAB and BL are presented in a GLON-GLAT-VLSR cube, where each VLSR slice
is a GLON-GLAT image.  There are ways in the viewers to view another slice, for example
a VLSR-GLON or VLSR-GLAT plot. Hint: in **ds9**: Frame -> Cube -> Axes Order

3. (advanced) In ds9 you can blink between images. Hint: Frame -> New Frame, load an image
in that frame, then Frame -> Tile Frame, and compare visually, or blink between them.
