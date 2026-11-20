# Mutante 7: sin __post_init__.
import aco_gemelo.motor.simulacion as s
s.ConfigEnsayo.__post_init__ = lambda self: None
