from pybamm import Parameter


def separator_LGM50_heat_capacity_ORegan2021(T):
    """
    Wet separator specific heat capacity as a function of the temperature from [1].

    References
    ----------
    .. [1] Kieran O’Regan, Ferran Brosa Planella, W. Dhammika Widanage, and Emma
    Kendrick. "Thermal-electrochemical parametrisation of a lithium-ion battery:
    mapping Li concentration and temperature dependencies." Journal of the
    Electrochemical Society, submitted (2021).

    Parameters
    ----------
    T: :class:`pybamm.Symbol`
       Dimensional temperature

    Returns
    -------
    :class:`pybamm.Symbol`
       Specific heat capacity
    """

    # value for the dry porous separator (i.e. separator + air, and we neglect the air
    # contribution to density)
    cp_dry = 1.494e-3 * T ** 3 - 1.444 * T ** 2 + 475.5 * T - 5.13e4
    rho_dry = 946
    theta_dry = rho_dry * cp_dry

    # value for the bulk electrolyte
    rho_e = 1280
    cp_e = 229
    eps_e = Parameter("Separator porosity")
    theta_e = rho_e * cp_e

    # value for the wet separator
    theta_wet = theta_dry + theta_e * eps_e
    rho_wet = rho_dry + rho_e * eps_e
    cp_wet = theta_wet / rho_wet

    return cp_wet
