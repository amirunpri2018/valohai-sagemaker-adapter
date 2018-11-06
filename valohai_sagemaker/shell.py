import subprocess
import sys


class CommandRunner(object):
    def __init__(self):
        self.out = None
        self.err = None
        self.reset()


    def reset(self):
        self.out = []
        self.err = []


    @property
    def stdout(self):
        return "".join(self.out)


    @property
    def stderr(self):
        return "".join(self.err)


    def run(self, argv, output=sys.stdout, encoding="utf8", verbose=True, popen_kwargs={}):
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   encoding=encoding, **popen_kwargs)
        return_code = None

        def get_output(oarray, ostream, istream, verbose):
            while True:
                gotten_line = istream.readline()
                if len(gotten_line) == 0:
                    break
                oarray.append(gotten_line)
                if verbose:
                    ostream.write(oarray[-1])

        while return_code is None:
            get_output(self.out, output, process.stdout, verbose)
            get_output(self.err, output, process.stderr, verbose)
            return_code = process.poll()

        get_output(self.out, output, process.stdout, verbose)
        get_output(self.err, output, process.stderr, verbose)

        return return_code
