"""Material objects are a simple structure that contain commonly used
properties for calculations. By default this includes Fused Silica and
Silicon at 123K.

.. todo::

    At some point add in wavelenth and temperature dependence to these
    Material objects.
"""

cdef class Material:
    """"""
    def __init__(self, alpha, nr, dndT, kappa, emiss, poisson, E, rho, C, T):
        self.values.alpha   = alpha
        self.values.nr      = nr
        self.values.dndT    = dndT
        self.values.kappa   = kappa
        self.values.emiss   = emiss
        self.values.poisson = poisson
        self.values.E       = E
        self.values.T       = T
        self.values.C       = C
        self.values.rho     = rho

    @property
    def alpha(self):
        """Thermo expansion coefficient"""
        return self.values.alpha

    @property
    def nr(self):
        """Refractive index"""
        return self.values.nr

    @property
    def dndT(self):
        """Thermo refractive coefficient [K^-1]"""
        return self.values.dndT

    @property
    def kappa(self):
        """Thermal conductivity [Wm^-1]"""
        return self.values.kappa

    @property
    def emiss(self):
        """Emissitivity"""
        return self.values.emiss

    @property
    def poisson(self):
        """Poisson ratio"""
        return self.values.poisson

    @property
    def E(self):
        """Youngs Modulus [kg m^-3]"""
        return self.values.E

    @property
    def rho(self):
        """Density [kg m^-3]"""
        return self.values.rho

    @property
    def C(self):
        """Specific Heat [J kg^-1]"""
        return self.values.C

    @property
    def T(self):
        """The temperature materials properties are defined at [K]"""
        return self.values.T


FusedSilica = Material(
    5.5e-7, # coefficient of linear expansion
    1.45,   # refractive Index
    8.6E-6, # dn/dt
    1.38,   # Thermal Conductivity
    0.91,   # Emissivity
    0.17,   # Poisson ratio
    7.2e10, # Youngs Modulus
    2202,   # density
    772,    # Specific heat
    297,    # reference temperature
)

# Taken from Voyager GWINC
Silicon123K_sum = Material(
    1e-10,  # coefficient of linear expansion
    3.4,   # refractive Index @ 2um
    1e-4,  # dn/dt
    700,    # Thermal Conductivity
    0.7,    # Emissivity, https://www.sciencedirect.com/science/article/pii/S0017931019361289
    0.27,   # Poisson ratio
    155.8e9,# Youngs Modulus
    2329,   # density
    300,    # Specific heat
    123,    # reference temperature
)

CaF2_300K_2um = Material(
    18.5e-6,  # coefficient of linear expansion
    1.4239,   # refractive Index @ 2um
    -10e-6,   # dn/dt
    9.71,     # Thermal Conductivity
    0.88,     # Emissivity
    0.26,     # Poisson ratio
    75.8e9,   # Youngs Modulus
    3180,     # density
    854,      # Specific heat
    300,      # reference temperature
)
