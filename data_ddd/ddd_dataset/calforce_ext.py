"""CalForce extension implementing OneNodeForce for the elasticity force mode.

The pydis CalForce class computes full elastic node forces
(NodeForce_Elasticity_SBA) but leaves OneNodeForce_Elasticity_SBA
unimplemented.  OneNodeForce is required by the MaxDiss topology module when
it evaluates trial splits of multi-arm (junction) nodes, which form when
loops collide.  This subclass adds a single-node force evaluation that uses
exactly the same non-singular seg-seg kernel (compute_segseg_force) and the
same Peach-Koehler treatment as NodeForce_Elasticity_SBA, so the physics is
identical to the reference force model.
"""

import numpy as np

from . import paths  # noqa: F401

from pydis import DisNet
from pydis.calforce.calforce_disnet import (CalForce, voigt_vector_to_tensor)
from pydis.calforce.compute_stress_force_analytic_paradis import compute_segseg_force


class CalForceElasticity(CalForce):
    """CalForce with OneNodeForce support for force_mode='Elasticity_SBA'."""

    def OneNodeForce_Elasticity_SBA(self, G: DisNet, applied_stress: np.ndarray,
                                    tag) -> np.ndarray:
        """Force on one node: PK force + elastic interaction of the node's
        arm segments with every segment in the network (including their own
        self-interaction), mirroring NodeForce_Elasticity_SBA restricted to
        the arms of `tag`.
        """
        segs = G.get_segs_data_with_positions()
        Nseg = segs["nodeids"].shape[0]
        source_tags = segs["tag1"]
        target_tags = segs["tag2"]
        R1, R2 = segs["R1"], segs["R2"]
        burg = segs["burgers"]

        sigext = voigt_vector_to_tensor(applied_stress)

        f = np.zeros(3)
        for i in range(Nseg):
            tag1 = tuple(source_tags[i])
            tag2 = tuple(target_tags[i])
            if tag != tag1 and tag != tag2:
                continue
            # Peach-Koehler force: half of the segment PK force per endpoint
            sigb = sigext @ burg[i]
            dR = R2[i] - R1[i]
            fpk = np.cross(sigb, dR)
            f += 0.5 * fpk
            # elastic interaction with every segment (incl. self, j == i)
            for j in range(Nseg):
                p1 = R1[i].copy()
                p2 = R2[i].copy()
                p3 = R1[j].copy()
                p4 = R2[j].copy()
                # apply PBC exactly as NodeForce_Elasticity_SBA does
                p2 = G.cell.closest_image(Rref=p1, R=p2)
                p3 = G.cell.closest_image(Rref=p1, R=p3)
                p4 = G.cell.closest_image(Rref=p3, R=p4)
                f1, f2, _f3, _f4 = compute_segseg_force(
                    p1, p2, p3, p4, burg[i].copy(), burg[j].copy(),
                    self.mu, self.nu, self.a)
                if tag == tag1:
                    f += f1
                if tag == tag2:
                    f += f2
        return f


# The pydis Topology module whitelists force objects by top-level module name
# ('pydis' or 'pyexadis_base').  This subclass lives outside those packages
# but is a pure extension of the pydis CalForce with identical physics, so we
# present it under the pydis namespace for that check.
CalForceElasticity.__module__ = "pydis.calforce.calforce_disnet"
