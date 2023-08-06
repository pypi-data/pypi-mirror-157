from typing import List
from typing import Callable
import random


class DistVariable:

	def __init__(self, distribution: List[float]) -> None:
		self._arr = distribution

	def sample(self) -> float:
		return random.choice(self._arr)


class Propagator:

	def __init__(self, prop_func: Callable[[List[float]], float]) -> None:
		self.func = prop_func
		self.input_vars: List[DistVariable] = []

	def addDistVariable(self, variable: DistVariable) -> None:
		self.input_vars.append(variable)

	def propagate(self, samples: int) -> List[float]:
		res = [0.0] * samples
		n_params = len(self.input_vars)
		inp = [0.0] * n_params
		for i in range(0, samples):

			# Sample from input space
			for j in range(0, n_params):
				inp[j] = self.input_vars[j].sample()

			# Calculate monte carlo sample from input
			res[i] = self.func(inp)

		return res
