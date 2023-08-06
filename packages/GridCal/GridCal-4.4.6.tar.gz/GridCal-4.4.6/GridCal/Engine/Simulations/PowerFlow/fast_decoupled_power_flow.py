import numpy as np
from numpy import angle, conj, exp, r_, Inf
from numpy.linalg import norm
from scipy.sparse.linalg import splu
import time
from GridCal.Engine.Simulations.PowerFlow.power_flow_results import NumericPowerFlowResults

np.set_printoptions(linewidth=320)


def FDPF(Vbus, Sbus, Ibus, Ybus, B1, B2, pq, pv, pqpv, tol=1e-9, max_it=100) -> NumericPowerFlowResults:
    """
    Fast decoupled power flow
    :param Vbus: array of initial voltages
    :param Sbus: array of power injections
    :param Ibus: array of current injections
    :param Ybus: Admittance matrix
    :param B1: B' matrix for the fast decoupled algorithm
    :param B2: B'' matrix for the fast decoupled algorithm
    :param pq: array of pq indices
    :param pv: array of pv indices
    :param pqpv: array of pqpv indices
    :param tol: desired tolerance
    :param max_it: maximum number of iterations
    :return: NumericPowerFlowResults instance
    """

    start = time.time()
    # pvpq = np.r_[pv, pq]

    # set voltage vector for the iterations
    voltage = Vbus.copy()
    Va = np.angle(voltage)
    Vm = np.abs(voltage)

    # Factorize B1 and B2
    J1 = splu(B1[np.ix_(pqpv, pqpv)])
    J2 = splu(B2[np.ix_(pq, pq)])

    # evaluate initial mismatch
    Scalc = voltage * np.conj(Ybus * voltage - Ibus)
    mis = (Scalc - Sbus) / Vm  # complex power mismatch
    dP = mis[pqpv].real
    dQ = mis[pq].imag

    if len(pqpv) > 0:
        normP = norm(dP, Inf)
        normQ = norm(dQ, Inf)
        converged = normP < tol and normQ < tol

        # iterate
        iter_ = 0
        while not converged and iter_ < max_it:

            iter_ += 1

            # ----------------------------- P iteration to update Va ----------------------
            # solve voltage angles
            dVa = J1.solve(dP)

            # update voltage
            Va[pqpv] -= dVa
            voltage = Vm * exp(1j * Va)

            # evaluate mismatch
            Scalc = voltage * conj(Ybus * voltage - Ibus)
            mis = (Scalc - Sbus) / Vm  # complex power mismatch
            dP = mis[pqpv].real
            dQ = mis[pq].imag
            normP = norm(dP, Inf)
            normQ = norm(dQ, Inf)

            if normP < tol and normQ < tol:
                converged = True
            else:
                # ----------------------------- Q iteration to update Vm ----------------------
                # Solve voltage modules
                dVm = J2.solve(dQ)

                # update voltage
                Vm[pq] -= dVm
                voltage = Vm * exp(1j * Va)

                # evaluate mismatch
                Scalc = voltage * conj(Ybus * voltage - Ibus)
                mis = (Scalc - Sbus) / Vm  # complex power mismatch
                dP = mis[pqpv].real
                dQ = mis[pq].imag
                normP = norm(dP, Inf)
                normQ = norm(dQ, Inf)

                if normP < tol and normQ < tol:
                    converged = True

        F = r_[dP, dQ]  # concatenate again
        normF = norm(F, Inf)

    else:
        converged = True
        iter_ = 0
        normF = 0

    end = time.time()
    elapsed = end - start

    return NumericPowerFlowResults(V=voltage, converged=converged,
                                   norm_f=normF,
                                   Scalc=Scalc,
                                   ma=None,
                                   theta=None,
                                   Beq=None,
                                   Ybus=None, Yf=None, Yt=None,
                                   iterations=iter_,
                                   elapsed=elapsed)


if __name__ == '__main__':

    fname = r'/home/santi/Documentos/GitHub/GridCal/Grids_and_profiles/grids/IEEE 9 Bus.gridcal'

    from GridCal.Engine import FileOpen

    circuit = FileOpen(fname).open()
    nc = circuit.compile_snapshot()
    islands = nc.compute()
    island = islands[0]

    voltage_, converged_, normF_, Scalc_, iter_, elapsed_ = FDPF(Vbus=island.Vbus,
                                                                 Sbus=island.Sbus,
                                                                 Ibus=island.Ibus,
                                                                 Ybus=island.Ybus,
                                                                 B1=island.B1,
                                                                 B2=island.B2,
                                                                 pq=island.pq,
                                                                 pv=island.pv,
                                                                 pqpv=island.pqpv,
                                                                 tol=1e-9,
                                                                 max_it=100)

    print(np.abs(voltage_))
    print('iter:', iter_)
    print('Error:', normF_)
