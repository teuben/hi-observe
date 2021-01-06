#! /usr/bin/env python
#
#  HI-observe:  Load an RA-DEC-VEL FITS cube ,
#               extract the spectrum at a given pixel/ra+dec/glon+glat
#               plot the spectrum
#
#  5-jan-2019   PJT hacking, based on a trimmed cubespectrum3.py, for the GradMap weekend at the 40ft
#  8-jan-2018   PJT finished documenting, added the coordinate transformation functions
#                   make it work on BL.fits and LAB.fits, add Makefile for easy bootstrapping
#  5-jan-2020   PJT sum up signal
#  6-jan-2021   PJT convert to module for python notebook
#
#  Caveats:
#  - this code still ignores the equinox (B1950, J2000, current)


_version = "6-jan-2021  10.35"


#  import python modules we need. One per line.

import sys, os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy import coordinates as coord

#  define some convenience functions to transform coordinates between RA,DEC <---> GLON,GLAT

def radec_glonlat(rah,ram,ras,dec):
    """
    Simple conversion of 40ft RA(LST)/DEC to GLON/GLAT
    E.g. is LST = 12:10:30 and DEC=52 you would call
    this routine as   (glon,glat) = radec_glonlat(12,10,30,52)
    """
    r = rah*u.hour  + ram*u.minute + ras*u.second
    d = dec*u.deg
    c = SkyCoord(ra=r, dec=d, frame='icrs')
    g = c.galactic.to_string().split()
    return (float(g[0]),float(g[1]))

def glonlat_radec(glon,glat):
    """
    Convert GLON/GLAT to RA/DEC
    """
    lon = glon*u.deg
    lat = glat*u.deg
    c = SkyCoord(l=lon, b=lat, frame='galactic')
    g = c.icrs.to_string().split()
    return (float(g[0]),float(g[1]))

def lst(location='green bank telescope', date=None):
    """
    Return LST at greenbank, at the current time
    When a date is given, it will use that date,
    for example
        date =  '2021-01-06T03:00:00'
    
    Greenbank location:  gbloc = ('-80d', '38d')
    or more accurately:  -79.83131 38.43724 from google maps
    """
    myloc = coord.EarthLocation.of_site(location)
    if date == None:
        t = Time(datetime.utcnow(), scale='utc', location=myloc)
    else:
        t = Time(date, scale='utc', location=myloc)
    return t.sidereal_time('mean')


if True:
    print("*** hi_observe: version %s ***\n" % _version)
    # testing the conversion functions
    (glon,glat) = radec_glonlat(21,0,0,42)
    (ra,dec)    = glonlat_radec(glon,glat)
    print("test: radec_glonlat(20,58,15,42) should produce 83.886 -2.67928:   %g %g" % (glon,glat))
    print("test: glonlat_radec(glon,glat)   should produce 315 42:            %g %g" % (ra,dec))
    for f in ['BL.fits', 'LAB.fits']:
        if os.path.exists(f):
            print("test %-10s: found" % f)
        else:
            print("test %-10s: not found" % f)
            

def greenbank40ft(rah,ram,ras,dec, fitsfile='BL.fits', debug=False):
    """
    This function emulates observing with the Greenbank40ft, which
    is a transit instrument. For this the LST is the RAH:RAM:RAS

    Args:
       rah      (int) :  RA (or LST) hours
       ram      (int) :  RA (or LST) minutes
       ras      (int) :  RA (or LST) seconds
       dec      (int) :  Declination
       fitsfile (str) :  survey FITS file (common ones are BL.fits and LAB.fits)
       debug   (bool) :  turn debug on?

    Returns:
       (channels,flux)   :  two numpy arrays, the channels are in VLSR (km/s),
                            the flux is in whatever unit the survey was taken in
                            (usually K, sometimes Jy/beam)
     
    """

    c        = 299792.458         # speed of light in km/s
    restfreq = 1420.405751786     # HI restfreq in MHz
    vrange   = [-200, 50]         # plotting range

    
    have_pixel = False    
    (glon,glat) = radec_glonlat(rah,ram,ras,dec)
    if debug:
        print("GLON/GLAT: %g %g" % (glon,glat))
    pos=[glon,glat]
    

    # open the fits file (a FITS file has one or more Header-Data-Unit's, HDU's)
    hdu = fits.open(fitsfile)

    # get a reference to the primary header and data.
    h = hdu[0].header
    d = hdu[0].data.squeeze()
    if debug:
        print("Shape of cube: :",d.shape)
    if len(d.shape) != 3:                 # The data better be 3-dim numpy array now
        print("Your cube is not 3D")
        return None

    # get the important coordinate conversion factors that scale between pixels and WCS

    # axis 1 is GLON, in degrees
    cdelt1 = h['CDELT1']
    crval1 = h['CRVAL1']
    crpix1 = h['CRPIX1']

    # axis 2 is GLAT, in degrees
    cdelt2 = h['CDELT2']
    crval2 = h['CRVAL2']
    crpix2 = h['CRPIX2']

    # axis 3 is FELO, velocities in m/s (which we convert to km/s)
    cdelt3 = h['CDELT3']
    crval3 = h['CRVAL3']
    crpix3 = h['CRPIX3']

    # pos[] is now either a pixel or GLON/GLAT coordinate
    # depending on the "have_pixel" variable
    xpos = pos[0]
    ypos = pos[1]

    if have_pixel:
        # already have pixels, no conversion needed
        if debug:
            print("Pixel: %d %g" % (xpos,ypos))
        glon = (xpos-crpix1+1)*cdelt1 + crval1
        glat = (ypos-crpix2+1)*cdelt2 + crval2
        if debug:
            print("GLON/GLAT: %g %g" % (glon,glat))    
        (ra,dec) = glonlat_radec(glon,glat)
        if debug:
            print("RA/DEC: %g %g" % (ra,dec))
    else:
        # need to convert the xpos,ypos (in WCS) to pixel
        #    xpos_wcs = (xpos_pix - crpix + 1) * cdelt + crval
        #    xpos_pix = (xpos_wcs - crval)/cdelt + crpix - 1
        xposl = xpos
        yposb = ypos
        xpos = (xposl - crval1)/cdelt1 + crpix1 - 1 
        ypos = (yposb - crval2)/cdelt2 + crpix2 - 1
        if debug:
            print("Pixel: %g %g (converted from WCS %g %g)" % (xpos,ypos,xposl,yposb))
        xpos = int(xpos)
        ypos = int(ypos)
    

    #   now we grab get the spectrum using a numpy slice operation
    #   this will be the Y (intensity) coordinate in the plot
    if True:
        if debug:
            print("Using single pixel")
        flux     = d[:,ypos,xpos]
    else:
        #   if we are using some neighbours.... add them in (this algorithm is for near the Gal plane)
        b = 2
        w0 = 1.0
        w1 = np.exp(-1/(b*b))
        w2 = w1 * w1
        f00 = w2*d[:,ypos-1,xpos-1]
        f01 = w1*d[:,ypos-1,xpos  ]
        f02 = w2*d[:,ypos-1,xpos+1]
        f10 = w1*d[:,ypos  ,xpos-1]
        f11 = w0*d[:,ypos  ,xpos  ]
        f12 = w1*d[:,ypos  ,xpos+1]
        f20 = w2*d[:,ypos+1,xpos-1]
        f21 = w1*d[:,ypos+1,xpos  ]
        f22 = w2*d[:,ypos+1,xpos+1]
        if debug:
            print("Using 3x3 pixels with b=%g" % b)
        flux = (f00+f01+f02+f10+f11+f12+f20+f21+f22)/(w0+4*w1+4*w2)


    #   some helper arrays for the X (velocity) coordinate in the plot
    nchan    = d.shape[0]       
    zero     = np.zeros(nchan)
    channeln = np.arange(nchan)
    channelf = (channeln-crpix3+1)*cdelt3 + crval3   # WCS in m/s, notice channeln starts at 0
    channelv = channelf / 1000.0                     # convert assumed m/s to km/s
    if debug:
        print("MinMax in velocities:",channelv.min(), channelv.max())
        print("Total flux:",flux.sum()*(channelv[1]-channelv[0]))


    if False:

        #   and finally the figure can be plotted
        plt.figure()

        plt.plot(channelv,flux,'o-',markersize=2,label='HI-spectrum')
        plt.plot(channelv,zero,                  label='baseline')
        plt.xlim(vrange[0], vrange[1])
        plt.xlabel("Doppler Velocity (km/s)")
        plt.ylabel("Brightness")
        plt.title("%s  @ %g %g" % (cmdline,xpos,ypos))

        plt.legend()
        plt.savefig('hi-observe.png')
        plt.show()

    #   some statistics

    if debug:
        print("Mean and RMS of %d points: %g %g" % (len(flux),flux.mean(),flux.std()))


    return (channelv,flux)







if __name__ == '__main__':
    main(sys.argv[1:])









