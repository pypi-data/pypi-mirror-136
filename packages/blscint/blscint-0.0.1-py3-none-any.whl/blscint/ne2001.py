import os
import subprocess

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy import constants as const

import matplotlib.pyplot as plt
import tqdm

def to_galactic(ra, dec=None):
    """
    Convert RA/Dec to galactic coordinates (l, b).
    
    Parameters
    ----------
    ra : str, float, or astropy.Quantity
        Right ascension as a string or float in degrees, or a full string 
        that includes both RA and Dec
    dec : str, float, or astropy.Quantity, optional
        Declination as a string or float in degrees
        
    Returns
    -------
    l, b : float
        Galactic coordinates
    """
    if dec is None:
        assert isinstance(ra, str)
        c = SkyCoord(ra, unit=(u.hourangle, u.deg))
    else:
        if isinstance(ra, str) and isinstance(dec, str):
            c = SkyCoord(ra, dec, unit=(u.hourangle, u.deg))
        elif type(ra) in [int, float] and type(dec) in [int, float]:
            c = SkyCoord(ra, dec, unit=(u.deg, u.deg))
        else:
            c = SkyCoord(ra, dec)
    gal = c.galactic
    return gal.l.value, gal.b.value

def query_ne2001(l, b, d, field=None):
    """
    Query NE2001 model for various parameters, as described in 
    Cordes & Lazio 2002.
    
    Note that this returns an astropy Quantity; use the `.value` property
    to access the underlying value only.
    """
    current_path = os.path.abspath(os.path.dirname(__file__))
    exec_path = os.path.join(current_path, 'NE2001/bin.NE2001/run_NE2001.pl')
    
    cwd = os.getcwd()
    os.chdir(os.path.join(current_path, 'NE2001/bin.NE2001/'))
    
    if field is None:
        field = 'ALL'
    output = subprocess.run(['./run_NE2001.pl',
                             str(l),
                             str(b), 
                             str(d), 
                             '-1', 
                             field],
                            stdout=subprocess.PIPE).stdout.decode('utf-8')
    os.chdir(cwd)
    
    if field == 'ALL':
        print(output)
        return
             
    # Get unit
    unit = (output.split()[3].replace('pc-', 'pc.')
                             .replace('^{', '(')
                             .replace('}', ')'))
    unit = u.Unit(unit)
    val = float(output.split()[2])
    return val * unit

def plot_profile(l, b, d=(1, 20), steps=100, field='SCINTIME'):
    """
    Plot profile.
    """
    d = np.linspace(d[0], d[1], steps)
        
    p = np.empty(steps)
    for i in tqdm.tqdm(range(steps)):
        val = query_ne2001(l, b, d[i], field=field)
        p[i] = val.value
        unit = val.unit
        
    plt.plot(d, p)
    plt.xlabel('Distance (kpc)')
    plt.ylabel(f'{field} ({unit})')
    
def plot_map(l=(-2, 2), b=(-2, 2), d=8, l_steps=5, b_steps=5, field='SCINTIME'):
    """
    Plot 2D map of calculated field.
    """
    l = np.linspace(l[0], l[1], l_steps)
    dl = l[1] - l[0]
    b = np.linspace(b[0], b[1], b_steps)
    db = b[1] - b[0]
    
    f_map = np.empty((b_steps, l_steps))
    with tqdm.tqdm(total=l_steps * b_steps) as pbar:
        pbar.set_description('Pointings')
        for i in range(l_steps):
            for j in range(b_steps):
                val = query_ne2001(l[i], b[j], d, field=field)
                f_map[b_steps - 1 - j, i] = val.value
                unit = val.unit
                pbar.update(1)
            
    plt.imshow(f_map, interpolation='none', 
               extent=[l[0]-dl/2, l[-1]+dl/2, b[0]-db/2, b[-1]+db/2])
    c = plt.colorbar()
    plt.title(f'{field} ({unit})')
    plt.xlabel('l')
    plt.ylabel('b')

def get_standard_tscint(l, b, d):
    """
    Use NE2001 to estimate scintillation time at 1 GHz and 1 km/s transverse velocity.
    
    Parameters
    ----------
    l : float
        Galactic longitude
    b : float
        Galactic latitude
    d : float
        Distance in kpc
        
    Returns
    -------
    t_d : float
        Scintillation timescale in s
    """
    return query_ne2001(l, b, d, field='SCINTIME')

def scale_tscint(t_d, f=1, v=100, regime='moderate'):
    """
    Scale scintillation time by frequency and effective transverse velocity of 
    the diffraction pattern with respect to the observer. Changes exponential 
    scaling based on scattering regime, which is 'moderate' by default, or 
    'very_strong' (as in Cordes & Lazio 1991, Section 4.3).
    
    Parameters
    ----------
    t_d : float
        Scintillation time (s) at 1 GHz and 100 km/s
    f : float
        Frequency in GHz
    v : float
        Transverse velocity in km/s
    regime : str
        String determining frequency scaling, can be 'moderate' or 'very_strong'
        
    Returns
    -------
    t_d : float
        Scintillation timescale in s
    """
    if regime == 'very_strong':
        f_exp = 1
    else:
        f_exp = 1.2
    return t_d * (f / 1)**(f_exp) * (v / 100)**(-1)

def get_tscint(l, b, d, f=1, v=100, regime='moderate'):
    """
    Use NE2001 to estimate scintillation time at a specified frequency and 
    effective transverse velocity of the diffraction pattern with respect to
    the observer. Changes exponential scaling based on scattering regime, which
    is 'moderate' by default, or 'very_strong' (as in Cordes & Lazio 1991, Section
    4.3).
    
    Parameters
    ----------
    l : float
        Galactic longitude
    b : float
        Galactic latitude
    d : float
        Distance in kpc
    f : float
        Frequency in GHz
    v : float
        Transverse velocity in km/s
    regime : str
        String determining frequency scaling, can be 'moderate' or 'very_strong'
        
    Returns
    -------
    t_d : float
        Scintillation timescale in s
    """
    t_st = get_standard_tscint(l, b, d)
    return scale_tscint(t_st, f, v, regime)
    

def get_fresnel(f, D, normalize=True):
    """
    Get Fresnel scale. If normalize=True, use definition with 1/2pi in the sqrt.
    
    Parameters
    ----------
    f : float
        Frequency in GHz
    D : float
        Distance in kpc
    normalize : bool
        Whether to scale by sqrt(1/2pi)
    """
    
    wl = const.c / (f * u.GHz)
    l_f = np.sqrt(wl * (D * u.kpc)).to(u.cm)
    if normalize:
        l_f = np.sqrt(l_f / (2 * np.pi))
    return l_f