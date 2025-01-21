import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory


class LandCoverOptimisation:
    """
    A class to manage optimisation tasks for land cover allocation and distribution.

    Attributes:
    ----------
    solver : str
        The optimization solver to use (e.g., 'cplex', 'gurobi', 'glpk').

    Methods:
    -------
    optimise_mineral_spared_area_distribution(mineral_area_available, target_areas)
        Optimises land distribution to minimize deviation from target areas.
    """

    def __init__(self, solver="cplex_direct"):
        """
        Initializes the optimisation class with a specified solver.

        :param solver: Solver to use for optimisation (default: 'cplex').
        """
        self.solver = solver


    def optimise_mineral_spared_area_distribution(self, mineral_area_available, target_areas):
        """
        Optimises land distribution to minimize deviation from target areas.
        Includes a fallback mechanism for leftover area to "farmable condition."

        :param mineral_area_available: Total mineral area available (float).
        :param target_areas: Target areas for each land class (dict).
        :return: Optimized land allocations (dict).
        """
        # Define scale factor as the total mineral area available
        scale_factor = mineral_area_available

        # Normalize inputs
        normalized_target_areas = {k: v / scale_factor for k, v in target_areas.items()}
        normalized_available_area = 1.0  # Normalize total area to 1

        model = pyo.ConcreteModel()

        # Define Sets
        land_uses = list(target_areas.keys())
        model.i = pyo.Set(initialize=land_uses)

        # Define Parameters
        model.target_area = pyo.Param(model.i, initialize=normalized_target_areas)
        model.actual_mineral_area_available = pyo.Param(initialize=normalized_available_area)


        # Decision Variables
        model.allocation = pyo.Var(model.i, domain=pyo.NonNegativeReals)
        model.fallback_area = pyo.Var(domain=pyo.NonNegativeReals)

        # Objective Function
        def objective_function(model):
            # Minimize the deviation from target areas and handle spillover
            return sum(
                (model.allocation[i] - model.target_area[i])**2 for i in model.i
            ) + model.fallback_area**2

        model.obj = pyo.Objective(rule=objective_function, sense=pyo.minimize)

        # Constraints
        def total_area_constraint(model):
            # Ensure total allocation matches available area
            return sum(model.allocation[i] for i in model.i) + model.fallback_area == model.actual_mineral_area_available

        model.total_area_constraint = pyo.Constraint(rule=total_area_constraint)

        def cap_target_area_constraint(model, i):
            # Prevent allocation from exceeding the target area for each land class
            return model.allocation[i] <= model.target_area[i]

        model.cap_target_area_constraint = pyo.Constraint(model.i, rule=cap_target_area_constraint)

        # Solve
        solver = SolverFactory(self.solver) 

        results = solver.solve(model)

        if results.solver.termination_condition == pyo.TerminationCondition.optimal:
            print("Land use Assignment Solution is optimal!")
        elif results.solver.termination_condition == pyo.TerminationCondition.infeasible:
            print("Land use Assignment Solution is infeasible!")
            raise ValueError("Infeasible solution!")
        else:
            print(f"Solver terminated with condition: {results.solver.termination_condition}")
            raise RuntimeError("Land use Assignment Solver did not find an optimal solution!")

        # Rescale results
        optimised_allocations = {
            i: model.allocation[i].value * scale_factor for i in model.i
        }
        optimised_allocations["farmable_condition"] = model.fallback_area.value * scale_factor

        return optimised_allocations


