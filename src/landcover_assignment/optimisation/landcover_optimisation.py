"""
Land cover optimisation
=======================
Allocates a scenario's spared **mineral** grassland between land-use targets with a small Pyomo model, solved by the
open-source HiGHS solver.

The model
---------
All areas are divided by the available mineral area A, so the model works in shares of A. This keeps the problem
well scaled; the results are multiplied back to hectares.

Sets
    ``LAND_USES``: the land uses with a target (currently forest and cropland). It is built from ``target_areas``, so
    adding a land use needs no code change.
Parameters
    ``target[i]``: the target area of land use *i* (share of A).
    ``area_available``: 1 (all of A).
Variables
    ``allocation[i] >= 0``: area allocated to land use *i*.
    ``fallback >= 0``: area allocated to no target, returned as ``farmable_condition``.
Objective (minimise)
    sum over i of (allocation[i] - target[i])^2, plus fallback^2.
Constraints
    ``use_all_area``: sum of allocation[i] + fallback = area_available.
    ``cap_at_target[i]``: allocation[i] <= target[i].

What this gives:
- If the targets fit within the available area, every target is met and the rest goes to ``farmable_condition``.
- If they don't fit, ``farmable_condition`` is 0 and every target is cut by the same area: the squared objective
  spreads the shortfall evenly in absolute terms, and any target that reaches 0 stops there.
- The objective is strictly convex, so the solution is unique. Any correct solver gives the same answer.

Extending the model
-------------------
``optimise_mineral_spared_area_distribution`` accepts ``extra_constraints``: functions that take the Pyomo model
and add components to it. They are added after the standard ones, so they can use ``model.LAND_USES``,
``model.target``, ``model.allocation`` and ``model.fallback``. For example, a cap on cropland:

.. code-block:: python

    def cap_cropland(model):
        model.cap_cropland = pyo.Constraint(expr=model.allocation["cropland"] <= 0.1)   # share of A

    LandCoverOptimisation().optimise_mineral_spared_area_distribution(area, targets, extra_constraints=[cap_cropland])

A new land use (for example willow) needs only a new entry in ``target_areas``.
"""
import logging

import pyomo.environ as pyo

logger = logging.getLogger(__name__)

DEFAULT_SOLVER = "highs"
FALLBACK_LAND_USE = "farmable_condition"


def _objective(model):
    """Squared deviation from each target, plus the squared unallocated area."""
    return sum((model.allocation[i] - model.target[i]) ** 2 for i in model.LAND_USES) + model.fallback ** 2


def _use_all_area(model):
    """All of the available mineral area is allocated, to a target or to the fallback."""
    return sum(model.allocation[i] for i in model.LAND_USES) + model.fallback == model.area_available


def _cap_at_target(model, i):
    """No land use receives more than its target."""
    return model.allocation[i] <= model.target[i]


class LandCoverOptimisation:
    """
    Allocates spared mineral grassland between land-use targets (see the module docstring for the model).

    :param solver: Pyomo solver name. The default is ``"highs"`` (open-source HiGHS, through ``highspy``). Pyomo's
        ``"appsi_highs"`` interface does not accept the quadratic objective.
    """

    def __init__(self, solver=DEFAULT_SOLVER):
        self.solver = solver

    @staticmethod
    def build_model(target_shares, extra_constraints=()):
        """
        Build the allocation model.

        :param target_shares: Target area of each land use, as a share of the available area (dict).
        :param extra_constraints: Functions ``f(model)`` that add further constraints (optional).
        :return: The Pyomo model.
        :rtype: pyomo.environ.ConcreteModel
        """
        model = pyo.ConcreteModel()
        model.LAND_USES = pyo.Set(initialize=list(target_shares), ordered=True)
        model.target = pyo.Param(model.LAND_USES, initialize=target_shares)
        model.area_available = pyo.Param(initialize=1.0)
        model.allocation = pyo.Var(model.LAND_USES, domain=pyo.NonNegativeReals)
        model.fallback = pyo.Var(domain=pyo.NonNegativeReals)
        model.objective = pyo.Objective(rule=_objective, sense=pyo.minimize)
        model.use_all_area = pyo.Constraint(rule=_use_all_area)
        model.cap_at_target = pyo.Constraint(model.LAND_USES, rule=_cap_at_target)
        for add in extra_constraints:
            add(model)
        return model

    def solve(self, model):
        """
        Solve the model and check that the solver found the optimum.

        :raises RuntimeError: if the solver is unavailable or does not report an optimal solution.
        """
        solver = pyo.SolverFactory(self.solver)
        if not solver.available(exception_flag=False):
            raise RuntimeError(f"Solver '{self.solver}' is not available. Install highspy for the default HiGHS solver.")
        results = solver.solve(model)
        if not pyo.check_optimal_termination(results):
            raise RuntimeError(
                f"Land use allocation: solver '{self.solver}' did not find an optimal solution "
                f"(termination condition: {results.solver.termination_condition})."
            )
        logger.debug("Land use allocation solved to optimality with %s", self.solver)
        return results

    def optimise_mineral_spared_area_distribution(self, mineral_area_available, target_areas, extra_constraints=()):
        """
        Allocate the available spared mineral area to the target land uses. The rest goes to farmable condition.

        :param mineral_area_available: Spared mineral area available (ha).
        :param target_areas: Target area of each land use (ha), e.g. ``{"forest": ..., "cropland": ...}``.
        :param extra_constraints: Functions ``f(model)`` that add further constraints (optional; see module docstring).
        :return: Allocated area per land use (ha), plus ``farmable_condition``. The values sum to
            ``mineral_area_available``.
        :rtype: dict
        """
        if mineral_area_available <= 0:
            # Nothing to allocate (e.g. all spared area is rewetted, or no mineral grassland is left).
            return {**{land_use: 0.0 for land_use in target_areas}, FALLBACK_LAND_USE: 0.0}

        scale = mineral_area_available
        model = self.build_model({k: v / scale for k, v in target_areas.items()}, extra_constraints)
        self.solve(model)

        allocations = {i: pyo.value(model.allocation[i]) * scale for i in model.LAND_USES}
        allocations[FALLBACK_LAND_USE] = pyo.value(model.fallback) * scale
        return allocations
