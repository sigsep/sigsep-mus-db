import matlab_wrapper
import numpy as np
import os


class matlabwrapper(matlab_wrapper.MatlabSession):
    def run_func(self, estimates, originals, method, rate):
        self.put('es', estimates)
        self.put('s', originals)
        self.put('fs', rate)
        if method == "bss_eval":
            self.eval(
                '[SDR,ISR,SIR,SAR] = bss_eval(es, s, 30*fs,15*fs)'
            )
            SDR = self.get('SDR')
            ISR = self.get('ISR')
            SIR = self.get('SIR')
            SAR = self.get('SAR')

            return SDR, ISR, SIR, SAR

    def start(self):
        matlab_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'external'
        )
        self.eval('addpath(\'%s/\')' % matlab_path)


class BSSeval(object):
    def __init__(self, method):
        methods = ("bss_eval", "mir_eval")
        if method not in methods:
            raise ValueError("method must be in %s" % ','.join(methods))

        self.method = method
        if method == "bss_eval":
            self.matlab = matlabwrapper(options="-nosplash -nodesktop -nojvm")
            self.matlab.start()
        else:
            self.matlab = None

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
        print "Evaluating with %s" % self.method

        if self.method == "mir_eval":
            import mir_eval
            mono_estimates = np.sum(np.array(estimates), axis=0)
            mono_originals = np.sum(np.array(originals), axis=0)
            SDR, SIR, SAR, perm = mir_eval.separation.bss_eval_sources(
                mono_estimates,
                mono_originals,
            )

            ISR = 0.0
        elif self.method == "bss_eval":
            shaped_estimates = np.transpose(estimates, (1, 2, 0))
            shaped_originals = np.transpose(originals, (1, 2, 0))
            SDR, ISR, SIR, SAR = self.matlab.run_func(
                shaped_estimates, shaped_originals, self.method, rate
            )

        if verbose:
            print "SDR: " + str(SDR)
            print "ISR: " + str(ISR)
            print "SIR: " + str(SIR)
            print "SAR: " + str(SAR)

        return SDR, ISR, SIR, SAR
