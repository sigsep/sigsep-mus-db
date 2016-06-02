from __future__ import print_function
import numpy as np


class BSSeval(object):
    def __init__(self, method):
        methods = ("mir_eval")
        if method not in methods:
            raise ValueError("method must be in %s" % ','.join(methods))

        self.method = method

    def evaluate(self, estimates, originals, rate, verbose=True):
        """Universal BSS evaluate frontend for several evaluators

        Parameters
        ----------
        originals : np.ndarray, shape=(nsrc, nsampl, nchan)
            array containing true reference sources
        estimates : np.ndarray, shape=(nsrc, nsampl, nchan)
            array containing estimated sources

        Returns
        -------
        SDR : np.ndarray, shape=(nsrc,)
            vector of Signal to Distortion Ratios (SDR)
        ISR : np.ndarray, shape=(nsrc,)
            vector of Source to Spatial Distortion Image (ISR)
        SIR : np.ndarray, shape=(nsrc,)
            vector of Source to Interference Ratios (SIR)
        SAR : np.ndarray, shape=(nsrc,)
            vector of Sources to Artifacts Ratios (SAR)
        """
        print("Evaluating with %s" % self.method)

        if self.method == "mir_eval":
            import mir_eval
            mono_estimates = np.mean(estimates, axis=0).T
            mono_originals = np.mean(originals, axis=0).T
            SDR, SIR, SAR, perm = mir_eval.separation.bss_eval_sources(
                mono_estimates,
                mono_originals,
            )

            ISR = np.nan

        if verbose:
            print("SDR: ", str(SDR))
            print("ISR: ", str(ISR))
            print("SIR: ", str(SIR))
            print("SAR: ", str(SAR))

        return SDR, ISR, SIR, SAR
