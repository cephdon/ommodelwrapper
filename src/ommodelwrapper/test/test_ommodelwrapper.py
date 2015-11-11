import unittest
import glob
import nose
import logging
import sys
import os
from openmdao.core.problem import Problem, Group
from openmdao.recorders.dump_recorder import DumpRecorder


class OMModelWrapperTestCase(unittest.TestCase):
    def setUp(self):
        #if os.name != 'nt':
        #    raise nose.SkipTest('Sorry, OMModelWrapper has only been validated on Windows.')
        #if os.name == 'posix':
        #    raise nose.SkipTest('Sorry, OMModelWrapper has only been validated on Windows.')
        pass

    def tearDown(self):
        pass

    def test_OMModelWrapper(self):
        logging.debug('')
        logging.debug('test_OMModelWrapper')

        from ommodelwrapper.ommodelwrapper import OMModelWrapper

        problem = Problem()
        root = problem.root = Group()
        test_model = OMModelWrapper('SimAcceleration', 'VehicleDesign.mo')
        root.add('simacceleration', test_model)

        recorder = DumpRecorder()
        recorder.options['record_params'] = True
        recorder.options['record_metadata'] = True
        recorder.options['record_resids'] = True
        problem.driver.add_recorder(recorder)

        problem.setup()
        problem.run()

        problem.driver.recorders[0].close()

        # assert_rel_error(self, testModel.accel_time[-1], 6.935, 0.01)
        # del (testModel)
        # os._exit(1)


if __name__ == "__main__":
    sys.argv.append('--cover-package=ommodelwrapper.')
    sys.argv.append('--cover-erase')
    nose.runmodule()
