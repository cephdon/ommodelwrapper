import unittest
import nose
import logging
import sys
import os
from openmdao.core.problem import Problem, Group
from openmdao.components.indep_var_comp import IndepVarComp
from openmdao.recorders.dump_recorder import DumpRecorder
from ommodelwrapper.ommodelwrapper import OMModelWrapper


class OMModelWrapperTestCase(unittest.TestCase):
    def setUp(self):
        if os.name == 'nt':
            raise nose.SkipTest('Sorry, OMModelWrapper has not been validated on Windows.')
        pass

    def tearDown(self):
        pass

    def test_OMModelWrapper(self):
        logging.debug('')
        logging.debug('test_OMModelWrapper')

        this_dir_path = os.path.realpath(os.path.dirname(__file__))
        addl_lib_path = os.path.join(this_dir_path, 'VehicleDesign.mo')

        problem = Problem()
        root = problem.root = Group()
        test_model = OMModelWrapper('SimAcceleration', addl_lib_path)
        root.add('simacceleration', test_model)
        root.add('simtime', IndepVarComp('duration', val='15.0'))
        root.connect('simtime.duration', 'simacceleration.stopTime')

        dump_filename = 'dump.log'
        # Delete old dumpfile
        try:
            os.remove(dump_filename)
        except OSError:
            pass

        recorder = DumpRecorder(dump_filename)
        recorder.options['record_params'] = True
        recorder.options['record_metadata'] = True
        recorder.options['record_resids'] = True
        problem.driver.add_recorder(recorder)

        problem.setup()
        problem.run()

        problem.driver.recorders[0].close()

        self.assertTrue(os.path.exists(dump_filename))
        with open(dump_filename) as dumpf:
            dump = dumpf.readlines()
        self.assertTrue('  simtime.duration: 15.0\n' in dump)
        self.assertTrue('  simacceleration.accel_time: [  0.   0.   0. ...,  15.  15.  15.]\n' in dump)


if __name__ == "__main__":
    sys.argv.append('--cover-package=ommodelwrapper.')
    sys.argv.append('--cover-erase')
    nose.runmodule()
