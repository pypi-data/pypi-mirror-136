import base64
import io
from datetime import datetime, time
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import pydantic
from matplotlib.ticker import MaxNLocator
from PIL import Image
from tabulate import tabulate

from classiq_interface.helpers.custom_pydantic_types import pydanticProbabilityFloat

Solution = Tuple[int, ...]


class SolverResult(pydantic.BaseModel):
    best_cost: float
    # TODO: add time units (like seconds)
    time: time
    solution: Solution


class SolutionData(pydantic.BaseModel):
    solution: Solution
    repetitions: Optional[pydantic.PositiveInt]
    probability: Optional[pydanticProbabilityFloat]
    cost: float


class VQEIntermediateData(pydantic.BaseModel):
    utc_time: datetime = pydantic.Field(description="Time when the iteration finished")
    iteration_number: pydantic.PositiveInt = pydantic.Field(
        description="The iteration's number (evaluation count)"
    )
    parameters: List[float] = pydantic.Field(
        description="The optimizer parameters for the variational form"
    )
    mean_all_solutions: Optional[float] = pydantic.Field(
        default=None, description="The mean score of all solutions in this iteration"
    )
    solutions: List[SolutionData] = pydantic.Field(
        description="Solutions found in this iteration, their score and"
        "number of repetitions"
    )


_MAX_BIN = 50


class VQESolverResult(SolverResult):
    energy: Optional[float]
    solution_distribution: List[SolutionData] = []
    intermediate_results: List[VQEIntermediateData] = []
    optimal_parameters: List[float] = []
    convergence_graph_str: Optional[str]

    def show_convergence_graph(self) -> None:
        self.convergence_graph.show()

    @property
    def convergence_graph(self):
        return Image.open(io.BytesIO(base64.b64decode(self.convergence_graph_str)))

    def optimal_parameters_graph(self, num_lines: int = 2):
        layers = list(range(len(self.optimal_parameters) // num_lines))

        if num_lines == 2:
            legends = [r"$\gamma$", r"$\beta$"]
        else:
            legends = [f"line{i}" for i in range(num_lines)]

        for i in range(num_lines):
            plt.plot(
                layers,
                self.optimal_parameters[i::num_lines],
                marker="o",
                linestyle="--",
            )
        plt.xlabel("repetition")
        plt.ylabel("value")
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.legend(legends)

    def __str__(self) -> str:
        return "\n".join(self.formatted())

    def formatted(self) -> List[str]:
        lines = []
        lines.append("=== OPTIMAL SOLUTION ===")
        lines.append(
            tabulate(
                [[tuple(self.solution), self.best_cost]], headers=["solution", "cost"]
            )
        )

        lines.append("=== SOLUTION DISTRIBUTION ===")
        solution_distribution_table = [
            [solution_data.solution, solution_data.cost, solution_data.probability]
            for solution_data in self.solution_distribution
        ]
        lines.append(
            tabulate(
                solution_distribution_table, headers=["solution", "cost", "probability"]
            )
        )
        lines.append("=== OPTIMAL_PARAMETERS ===")
        lines.append(str(self.optimal_parameters))
        lines.append("=== TIME ===")
        lines.append(str(self.time))
        return lines

    def histogram(self):
        repetitions = [
            solution_data.repetitions for solution_data in self.solution_distribution
        ]
        costs = [solution_data.cost for solution_data in self.solution_distribution]

        bins = min(len(set(costs)), _MAX_BIN)
        eps = (max(costs) - min(costs)) / bins / 2
        hist_range = (min(costs) - eps, max(costs) + eps)
        plt.hist(
            x=costs, bins=bins, density=True, weights=repetitions, range=hist_range
        )

        plt.ylabel("Probability")
        plt.xlabel("value")
