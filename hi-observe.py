#! /usr/bin/env python
#
#  HI-observe:  Load an RA-DEC-VEL FITS cube ,
#               extract the spectrum at a given pixel/ra+dec/glon+glat
#               plot the spectrum
#
#  5-jan-2019   PJT hacking, based on a trimmed cubespectrum3.py, for the GradMap weekend at the 40ft
#  8-jan-2018   PJT finished documenting, added the coordinate transformation functions
#                   make it work on BL.fits and LAB.fits, add Makefile for easy bootstrapping
#
#  Caveats:
#  - this code still ignores the equinox (B1950, J2000, current)


#  import python modules we need. One per line.

import sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy import units as u
from astropy.coordinates import SkyCoord

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


if True:
    # testing the functions
    (glon,glat) = radec_glonlat(21,0,0,42)
    (ra,dec)    = glonlat_radec(glon,glat)
    print("test1: radec_glonlat(20,58,15,42) should produce 83.886 -2.67928:   %g %g" % (glon,glat))
    print("test2: glonlat_radec(glon,glat)   should produce 315 42:            %g %g" % (ra,dec))

#   some constants we might need (but actually not in the current code)

c        = 299792.458         # speed of light in km/s
restfreq = 1420.405751786     # HI restfreq in MHz


#   parse our simple positional command line interface,
#   and give some help if you didn't specify it correctly

na = len(sys.argv) - 1
cmdline = str(sys.argv[1:])
if na == 3:
    # if 3 arguments given, FILE GLON GLAT    or    FILE -XPOS -YPOS
    fitsfile = sys.argv[1]
    xpos = sys.argv[2]
    ypos = sys.argv[3]
    if xpos[0]=='-':
        have_pixel = True
        pos = [-int(sys.argv[2]),-int(sys.argv[3])]        
    else:
        have_pixel = False
        pos = [float(sys.argv[2]),float(sys.argv[3])]
        glon = pos[0]
        glat = pos[1]
        (ra,dec) = glonlat_radec(glon,glat)
        print("RA/DEC: %g %g" % (ra,dec))
elif na == 5:
    # if 5 arguments given, FILE RAH RAM RAS DEC (as integers)
    fitsfile = sys.argv[1]
    rah = int(sys.argv[2])
    ram = int(sys.argv[3])
    ras = int(sys.argv[4])
    dec = int(sys.argv[5])
    have_pixel = False    
    (glon,glat) = radec_glonlat(rah,ram,ras,dec)
    print("GLON/GLAT: %g %g" % (glon,glat))
    pos=[glon,glat]
else:
    # else give some reminders
    print("Usage: %s fitsfile glon glat"       % sys.argv[0])
    print("       %s fitsfile -xpos -ypos"     % sys.argv[0])
    print("       %s fitsfile rah ram ras dec" % sys.argv[0])
    sys.exit(1)


# open the fits file (a FITS file has one or more Header-Data-Unit's, HDU's)
hdu = fits.open(fitsfile)

# get a reference to the primary header and data.
h = hdu[0].header
d = hdu[0].data.squeeze()
print("Shape of cube: :",d.shape)
if len(d.shape) != 3:                 # The data better be 3-dim numpy array now
    print("Your cube is not 3D")
    sys.exit(1)

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
    print("Pixel: %d %g" % (xpos,ypos))
    glon = (xpos-crpix1+1)*cdelt1 + crval1
    glat = (ypos-crpix2+1)*cdelt2 + crval2
    print("GLON/GLAT: %g %g" % (glon,glat))    
    (ra,dec) = glonlat_radec(glon,glat)
    print("RA/DEC: %g %g" % (ra,dec))
else:
    # need to convert the xpos,ypos (in WCS) to pixel
    #    xpos_wcs = (xpos_pix - crpix + 1) * cdelt + crval
    #    xpos_pix = (xpos_wcs - crval)/cdelt + crpix - 1
    xposl = xpos
    yposb = ypos
    xpos = (xposl - crval1)/cdelt1 + crpix1 - 1 
    ypos = (yposb - crval2)/cdelt2 + crpix2 - 1
    print("Pixel: %g %g (converted from WCS %g %g)" % (xpos,ypos,xposl,yposb))
    xpos = int(xpos)
    ypos = int(ypos)
    

#   now we grab get the spectrum using a numpy slice operation
#   this will be the Y (intensity) coordinate in the plot
flux     = d[:,ypos,xpos]

#   some helper arrays for the X (velocity) coordinate in the plot
nchan    = d.shape[0]       
zero     = np.zeros(nchan)
channeln = np.arange(nchan)
channelf = (channeln-crpix3+1)*cdelt3 + crval3   # WCS in m/s, notice channeln starts at 0
channelv = channelf / 1000.0                     # convert assumed m/s to km/s
print("MinMax in velocities:",channelv.min(), channelv.max())

#   and finally the figure can be plotted
plt.figure()

plt.plot(channelv,flux,'o-',markersize=2,label='HI-spectrum')
plt.plot(channelv,zero,                  label='baseline')
plt.xlabel("Doppler Velocity (km/s)")
plt.ylabel("Brightness")
plt.title("%s  @ %g %g" % (cmdline,xpos,ypos))

plt.legend()
plt.savefig('hi-observe.png')
plt.show()

#   some statistics

print("Mean and RMS of %d points: %g %g" % (len(flux),flux.mean(),flux.std()))

















