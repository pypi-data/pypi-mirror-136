"""Molecular dynamics fortran backend for atooms"""

import os
import math
import numpy
import logging
import f2py_jit
from atooms.system import Thermostat
from .base import _Dynamics

_log = logging.getLogger(__name__)
_f90_kernel_soft = os.path.join(os.path.dirname(__file__), 'kernels_soft.f90')
_f90_kernel_hard = os.path.join(os.path.dirname(__file__), 'kernels_hard.f90')


class VelocityVerlet(_Dynamics):

    def __init__(self, system, timestep=0.001):
        _Dynamics.__init__(self, system)

        # Molecular dynamics specific stuff
        self.conserved_energy = 0.0
        self.timestep = timestep

        # We compute the initial potential energy
        self.system.compute_interaction('forces')
        self._reference_energy = None

    def __str__(self):
        return """
backend: newtonian dynamics
algorithm: {}
timestep: {}
""".format(self.__class__, self.timestep)

    def run(self, steps):
        # Dump the arrays before we start. This can be done at each
        # run() call because we ask for views, and this does not incur
        # into overhead.
        _box = self.system.dump('cell.side', dtype='float64', view=True)
        _pos = self.system.dump('particle.position', dtype='float64', order='F', view=True)
        _vel = self.system.dump('particle.velocity', dtype='float64', order='F', view=True)
        _ids = self.system.dump('particle.species', dtype='int32', view=True)
        _rad = self.system.dump('particle.radius', dtype='float64', view=True)
        _pos_unf = self.system.dump('particle.position_unfolded', order='F', view=True)
        # Masses have to be replicated along the spatial dimensions to keep the vector syntax
        # The None indexing syntax adds a new dimension to the array
        _mas = self.system.dump('particle.mass', dtype='float64', view=True)
        _mas = numpy.repeat(_mas[:, numpy.newaxis], len(_box), axis=1)
        _mas = numpy.transpose(_mas, (1, 0))
        if self._reference_energy is None:
            self._reference_energy = self.system.total_energy()

        # Build f90 kernel module
        f90 = f2py_jit.jit(_f90_kernel_soft)

        # Main loop
        for _ in range(steps):
            f90.methods.evolve_velocity_verlet(1,
                                               self.timestep,
                                               self.system.interaction.forces,
                                               _box,
                                               _pos,
                                               _pos_unf,
                                               _vel,
                                               _ids,
                                               _mas)
            self.system.compute_interaction('forces')
            f90.methods.evolve_velocity_verlet(2,
                                               self.timestep,
                                               self.system.interaction.forces,
                                               _box,
                                               _pos,
                                               _pos_unf,
                                               _vel,
                                               _ids,
                                               _mas)

        self.conserved_energy = self.system.total_energy(cache=True) - self._reference_energy


class NosePoincare(_Dynamics):

    def __init__(self, system, timestep=0.001, temperature=-1.0):
        _Dynamics.__init__(self, system)

        # Molecular dynamics specific stuff
        self.conserved_energy = 0.0
        self.timestep = timestep

        # Thermostat
        if not hasattr(system, 'thermostat'):
            assert temperature > 0.0
            system.thermostat = Thermostat()
            system.thermostat.temperature = temperature

        # We compute the initial potential energy
        self.system.compute_interaction('forces')
        self._reference_energy = None

    def __str__(self):
        return """
backend: newtonian dynamics
algorithm: nose-poincare
timestep: {}
temperature: {}
""".format(self.timestep, self.system.thermostat.temperature)

    def run(self, steps):
        # Dump the arrays before we start. This can be done at each
        # run() call because we ask for views, and this does not incur
        # into overhead.
        _box = self.system.dump('cell.side', dtype='float64', view=True)
        _pos = self.system.dump('particle.position', dtype='float64', order='F', view=True)
        _vel = self.system.dump('particle.velocity', dtype='float64', order='F', view=True)
        _ids = self.system.dump('particle.species', dtype='int32', view=True)
        _rad = self.system.dump('particle.radius', dtype='float64', view=True)
        _pos_unf = self.system.dump('particle.position_unfolded', order='F', view=True)
        # Masses have to be replicated along the spatial dimensions to keep the vector syntax
        # The None indexing syntax adds a new dimension to the array
        _mas = self.system.dump('particle.mass', dtype='float64', view=True)
        _mas = numpy.repeat(_mas[:, numpy.newaxis], len(_box), axis=1)
        _mas = numpy.transpose(_mas, (1, 0))
        # Make sure the thermostat coordinates are 0-dim arrays
        # TODO: this calls for coords/moms to be added to Thermostat
        thermostat = self.system.thermostat
        # Reference energy
        ndim = self.system.number_of_dimensions
        ndf = ndim * (len(self.system.particle) - 1)
        if self._reference_energy is None:
            thermostat = self.system.thermostat
            # TODO: this calls for a NosePoincareThermostat.energy method?
            self._reference_energy = self.system.total_energy() + \
                thermostat.momentum**2 / (2*thermostat.mass) + \
                ndf * thermostat.temperature * math.log(thermostat.coordinate)

        # Build f90 kernel module
        f90 = f2py_jit.jit(_f90_kernel_soft)

        # Main loop
        for _ in range(steps):
            f90.methods.evolve_nose_poincare(1,
                                             self.timestep,
                                             self.system.interaction.forces,
                                             0.0, 0.0,
                                             thermostat.temperature,
                                             thermostat.coordinate,
                                             thermostat.momentum,
                                             thermostat.mass,
                                             self._reference_energy,
                                             _box,
                                             _pos,
                                             _pos_unf,
                                             _vel,
                                             _ids,
                                             _mas)
            epot_old = self.system.interaction.energy
            self.system.compute_interaction('forces')
            epot_new = self.system.interaction.energy
            f90.methods.evolve_nose_poincare(2,
                                             self.timestep,
                                             self.system.interaction.forces,
                                             epot_old, epot_new,
                                             thermostat.temperature,
                                             thermostat.coordinate,
                                             thermostat.momentum,
                                             thermostat.mass,
                                             self._reference_energy,
                                             _box,
                                             _pos,
                                             _pos_unf,
                                             _vel,
                                             _ids,
                                             _mas)

        energy = self.system.total_energy(cache=True) + \
            thermostat.momentum**2 / (2*thermostat.mass) + \
            ndf * thermostat.temperature * math.log(thermostat.coordinate)
        self.conserved_energy = thermostat.coordinate * (energy - self._reference_energy)


class EventDrivenAllenTildesley(_Dynamics):

    def __init__(self, system, timestep=0.001):
        _Dynamics.__init__(self, system)
        if self.system.interaction is None:
            from atooms.system.interaction import InteractionBase
            self.system.interaction = InteractionBase()
        self.timestep = timestep
        self._init = False

    def __str__(self):
        txt = """
backend: netwonian dynamics
algorithm: event-driven
method: allen-tildesley
timestep: {}
""".format(self.timestep)
        return txt

    def run(self, steps):
        # Build f90 kernel module
        f90 = f2py_jit.jit(_f90_kernel_hard)
        # TODO: Inlining with 0.6.0 gives a seg fault
        # f90 = f2py_jit.jit(f2py_jit.inline(_f90_kernel_hard))  #, extra_args='--opt="-fbounds-check"')

        # Dump variables
        box = self.system.dump('cell.side', view=True)
        pos = self.system.dump('particle.position', order='F', view=True)
        unf = self.system.dump('particle.position_unfolded', order='F', view=True)
        vel = self.system.dump('particle.velocity', order='F', view=True)
        ids = self.system.dump('particle.species', dtype='int32', view=True)
        rad = self.system.dump('particle.radius', view=True)
        if not self._init:
            self._coltime = numpy.ndarray(len(self.system.particle))
            self._partner = numpy.ndarray(len(self.system.particle), dtype='int32')
            f90.methods.run(pos, unf, vel, rad*2, box[0], self.timestep, 0, self._coltime, self._partner)
            self._init = True

        # Main loop
        virial = f90.methods.run(pos, unf, vel, rad*2, box[0], self.timestep, steps, self._coltime, self._partner)
        self.system.interaction.virial = virial * self.system.number_of_dimensions


EventDriven = EventDrivenAllenTildesley
