import matlab_wrapper


class matlabwrapper(matlab_wrapper.MatlabSession):
    def run_func(self, estimates, originals, method, rate):
        self.put('es', estimates)
        self.put('s', originals)
        self.put('fs', rate)
        if method == "BSSeval_matlab":
            self.eval(
                '[SDR,ISR,SIR,SAR,perm] = bss_eval(es, s, 30*fs,15*fs)'
            )
            SDR = self.get('SDR')
            ISR = self.get('ISR')
            SIR = self.get('SIR')
            SAR = self.get('SAR')

            return SDR, ISR, SIR, SAR

    def start(self):
        self.eval('addpath(\'external/\')')


class BSSeval(object):
    def __init__(self, method):
        methods = ("BSSeval_matlab", "mir_eval")
        if method not in methods:
            raise ValueError("method must be in %s" % ','.join(methods))

        self.method = method
        if method == "BSSeval_matlab":
            self.matlab = matlabwrapper(options="-nosplash -nodesktop -nojvm")
            self.matlab.start()
        else:
            self.matlab = None

    def evaluate(self, estimates, originals, rate, verbose=True):
        print "Evaluating with %s" % self.method

        if self.method == "mir_eval":
            import mir_eval
            SDR, SIR, SAR, perm = mir_eval.separation.bss_eval_sources(
                estimates,
                originals,
            )

            ISR = 0.0
        elif self.method == "BSSeval_matlab":
            SDR, ISR, SIR, SAR = self.matlab.run_func(
                estimates, originals, self.method, rate
            )

        if verbose:
            print "SDR: " + str(SDR)
            print "ISR: " + str(ISR)
            print "SIR: " + str(SIR)
            print "SAR: " + str(SAR)

        return SDR, ISR, SIR, SAR
