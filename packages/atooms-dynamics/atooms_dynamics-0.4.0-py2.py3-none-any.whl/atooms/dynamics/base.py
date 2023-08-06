import numpy


class _Dynamics:

    def __init__(self, system):
        self.system = system
        self.verlet_list = None

        # Add unfolded position to particles, initialized as the folded ones
        # We reuse existing arrays, if possible
        for p in self.system.particle:
            if hasattr(p, 'position_unfolded'):
                p.position_unfolded[:] = p.position.copy()
            else:
                p.position_unfolded = p.position.copy()

        # Store initial state of the system
        self.initial = system.__class__()
        self.initial.update(self.system, exclude=['interaction'])

    def __str__(self):
        return """
backend: {}
""".format(self.__class__)

    @property
    def rmsd(self):
        current = self.system.dump('particle.position_unfolded', order='F', view=True)
        initial = self.initial.dump('particle.position_unfolded', order='F', view=True)
        msd = numpy.sum((current - initial)**2) / len(self.system.particle)
        return msd**0.5

    def run(self):
        # Implement this
        pass
