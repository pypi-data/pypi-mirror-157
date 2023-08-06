#
# Class for many particles with polynomial concentration profile
#
import pybamm

from .base_fickian import BaseFickian


class PolynomialProfile(BaseFickian):
    """
    Class for molar conservation in particles employing Fick's
    law, assuming a polynomial concentration profile in r, and allowing variation
    in the electrode domain. Model equations from [1]_.

    Parameters
    ----------
    param : parameter class
        The parameters to use for this submodel
    domain : str
        The domain of the model either 'Negative' or 'Positive'
    name : str
        The name of the polynomial approximation to be used. Can be "uniform
        profile", "quadratic profile" or "quartic profile".
    options: dict
        A dictionary of options to be passed to the model.
        See :class:`pybamm.BaseBatteryModel`

    References
    ----------
    .. [1] VR Subramanian, VD Diwakar and D Tapriyal. “Efficient Macro-Micro Scale
           Coupled Modeling of Batteries”. Journal of The Electrochemical Society,
           152(10):A2002-A2008, 2005

    **Extends:** :class:`pybamm.particle.BaseParticle`
    """

    def __init__(self, param, domain, name, options):
        super().__init__(param, domain, options)
        self.name = name

        pybamm.citations.register("Subramanian2005")

    def get_fundamental_variables(self):
        variables = {}
        if self.domain == "Negative":
            # For all orders we solve an equation for the average concentration
            c_s_rav = pybamm.standard_variables.c_s_n_rav
            if self.name == "uniform profile":
                # The concentration is uniform so the surface value is equal to
                # the average
                c_s_surf = c_s_rav
            elif self.name in ["quadratic profile", "quartic profile"]:
                # We solve an equation for the surface concentration, so it is
                # a variable in the model
                c_s_surf = pybamm.standard_variables.c_s_n_surf
                r = pybamm.standard_spatial_vars.r_n
            if self.name == "quartic profile":
                # For the fourth order polynomial approximation we also solve an
                # equation for the average concentration gradient. Note: in the original
                # paper this quantity is referred to as the flux, but here we make the
                # distinction between the flux defined as N = -D*dc/dr and the
                # concentration gradient q = dc/dr
                q_s_rav = pybamm.standard_variables.q_s_n_rav
                variables.update(
                    {"R-averaged negative particle concentration gradient": q_s_rav}
                )

        elif self.domain == "Positive":
            # For all orders we solve an equation for the average concentration
            c_s_rav = pybamm.standard_variables.c_s_p_rav
            if self.name == "uniform profile":
                # The concentration is uniform so the surface value is equal to
                # the average
                c_s_surf = c_s_rav
            elif self.name in ["quadratic profile", "quartic profile"]:
                # We solve an equation for the surface concentration, so it is
                # a variable in the model
                c_s_surf = pybamm.standard_variables.c_s_p_surf
                r = pybamm.standard_spatial_vars.r_p
            if self.name == "quartic profile":
                # For the fourth order polynomial approximation we also solve an
                # equation for the average concentration gradient. Note: in the original
                # paper this quantity is referred to as the flux, but here we make the
                # distinction between the flux defined as N = -D*dc/dr and the
                # concentration gradient q = dc/dr
                q_s_rav = pybamm.standard_variables.q_s_p_rav
                variables.update(
                    {"R-averaged positive particle concentration gradient": q_s_rav}
                )

        # Set concentration depending on polynomial order
        if self.name == "uniform profile":
            # The concentration is uniform
            c_s = pybamm.PrimaryBroadcast(c_s_rav, [self.domain.lower() + " particle"])
        elif self.name == "quadratic profile":
            # The concentration is given by c = A + B*r**2
            A = pybamm.PrimaryBroadcast(
                (1 / 2) * (5 * c_s_rav - 3 * c_s_surf),
                [self.domain.lower() + " particle"],
            )
            B = pybamm.PrimaryBroadcast(
                (5 / 2) * (c_s_surf - c_s_rav), [self.domain.lower() + " particle"]
            )
            c_s = A + B * r ** 2
        elif self.name == "quartic profile":
            # The concentration is given by c = A + B*r**2 + C*r**4
            A = pybamm.PrimaryBroadcast(
                39 * c_s_surf / 4 - 3 * q_s_rav - 35 * c_s_rav / 4,
                [self.domain.lower() + " particle"],
            )
            B = pybamm.PrimaryBroadcast(
                -35 * c_s_surf + 10 * q_s_rav + 35 * c_s_rav,
                [self.domain.lower() + " particle"],
            )
            C = pybamm.PrimaryBroadcast(
                105 * c_s_surf / 4 - 7 * q_s_rav - 105 * c_s_rav / 4,
                [self.domain.lower() + " particle"],
            )
            c_s = A + B * r ** 2 + C * r ** 4

        variables.update(
            self._get_standard_concentration_variables(
                c_s, c_s_rav=c_s_rav, c_s_surf=c_s_surf
            )
        )

        return variables

    def get_coupled_variables(self, variables):
        c_s = variables[self.domain + " particle concentration"]
        c_s_rav = variables[
            "R-averaged " + self.domain.lower() + " particle concentration"
        ]
        c_s_surf = variables[self.domain + " particle surface concentration"]
        T = pybamm.PrimaryBroadcast(
            variables[self.domain + " electrode temperature"],
            [self.domain.lower() + " particle"],
        )
        D_eff = self._get_effective_diffusivity(c_s, T)

        # Set flux depending on polynomial order
        if self.name == "uniform profile":
            # The flux is zero since there is no concentration gradient
            N_s = pybamm.FullBroadcastToEdges(
                0,
                [self.domain.lower() + " particle"],
                auxiliary_domains={
                    "secondary": self.domain.lower() + " electrode",
                    "tertiary": "current collector",
                },
            )
            N_s_xav = pybamm.FullBroadcastToEdges(
                0, self.domain.lower() + " particle", "current collector"
            )
        elif self.name == "quadratic profile":
            # The flux may be computed directly from the polynomial for c
            if self.domain == "Negative":
                r = pybamm.standard_spatial_vars.r_n
                N_s = -D_eff * 5 * (c_s_surf - c_s_rav) * r
            elif self.domain == "Positive":
                r = pybamm.standard_spatial_vars.r_p
                N_s = -D_eff * 5 * (c_s_surf - c_s_rav) * r
            N_s_xav = pybamm.x_average(N_s)
        elif self.name == "quartic profile":
            q_s_rav = variables[
                "R-averaged " + self.domain.lower() + " particle concentration gradient"
            ]
            # The flux may be computed directly from the polynomial for c
            if self.domain == "Negative":
                r = pybamm.standard_spatial_vars.r_n
                N_s = -D_eff * (
                    (-70 * c_s_surf + 20 * q_s_rav + 70 * c_s_rav) * r
                    + (105 * c_s_surf - 28 * q_s_rav - 105 * c_s_rav) * r ** 3
                )
            elif self.domain == "Positive":
                r = pybamm.standard_spatial_vars.r_p
                N_s = -D_eff * (
                    (-70 * c_s_surf + 20 * q_s_rav + 70 * c_s_rav) * r
                    + (105 * c_s_surf - 28 * q_s_rav - 105 * c_s_rav) * r ** 3
                )
            N_s_xav = pybamm.x_average(N_s)

        variables.update(self._get_standard_flux_variables(N_s, N_s_xav))
        variables.update(self._get_standard_diffusivity_variables(D_eff))
        variables.update(self._get_total_concentration_variables(variables))

        return variables

    def set_rhs(self, variables):
        domain_param = self.domain_param

        c_s_rav = variables[
            "R-averaged " + self.domain.lower() + " particle concentration"
        ]
        j = variables[self.domain + " electrode interfacial current density"]
        R = variables[self.domain + " particle radius"]

        self.rhs = {c_s_rav: -3 * j / domain_param.a_R / domain_param.gamma / R}

        if self.name == "quartic profile":
            # We solve an extra ODE for the average particle flux
            q_s_rav = variables[
                "R-averaged " + self.domain.lower() + " particle concentration gradient"
            ]
            c_s_rav = variables[
                "R-averaged " + self.domain.lower() + " particle concentration"
            ]
            D_eff = variables[self.domain + " effective diffusivity"]

            self.rhs.update(
                {
                    q_s_rav: -30
                    * pybamm.r_average(D_eff)
                    * q_s_rav
                    / domain_param.C_diff
                    - 45 * j / domain_param.a_R / domain_param.gamma / 2
                }
            )

    def set_algebraic(self, variables):
        domain_param = self.domain_param

        c_s_surf = variables[self.domain + " particle surface concentration"]
        c_s_rav = variables[
            "R-averaged " + self.domain.lower() + " particle concentration"
        ]
        D_eff = variables[self.domain + " effective diffusivity"]
        j = variables[self.domain + " electrode interfacial current density"]
        R = variables[self.domain + " particle radius"]

        if self.name == "uniform profile":
            # No algebraic equations since we only solve for the average concentration
            pass
        elif self.name == "quadratic profile":
            # We solve an algebraic equation for the surface concentration
            self.algebraic = {
                c_s_surf: pybamm.surf(D_eff) * (c_s_surf - c_s_rav)
                + domain_param.C_diff
                * (j * R / domain_param.a_R / domain_param.gamma / 5)
            }

        elif self.name == "quartic profile":
            # We solve a different algebraic equation for the surface concentration
            # that accounts for the average concentration gradient inside the particle
            q_s_rav = variables[
                "R-averaged " + self.domain.lower() + " particle concentration gradient"
            ]
            self.algebraic = {
                c_s_surf: pybamm.surf(D_eff) * (35 * (c_s_surf - c_s_rav) - 8 * q_s_rav)
                + domain_param.C_diff * (j * R / domain_param.a_R / domain_param.gamma)
            }

    def set_initial_conditions(self, variables):
        c_s_rav = variables[
            "R-averaged " + self.domain.lower() + " particle concentration"
        ]

        c_init = pybamm.r_average(self.domain_param.c_init)

        self.initial_conditions = {c_s_rav: c_init}

        if self.name in ["quadratic profile", "quartic profile"]:
            # We also need to provide an initial condition (initial guess for the
            # algebraic solver) for the surface concentration
            c_s_surf = variables[self.domain + " particle surface concentration"]
            self.initial_conditions.update({c_s_surf: c_init})
        if self.name == "quartic profile":
            # We also need to provide an initial condition for the average
            # concentration gradient
            q_s_rav = variables[
                "R-averaged " + self.domain.lower() + " particle concentration gradient"
            ]
            self.initial_conditions.update({q_s_rav: 0})
