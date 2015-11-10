__all__ = ['OMModelWrapper']

from openmdao.core.component import Component
from xml.etree import ElementTree as ET
import sys
import os
import numpy as np
import load_modelica_mat as lmm
import OM_build
import subprocess


class OMModelWrapper(Component):
    """
    This is a wrapper of an OpenModelica model. It compiles OpenModelica's .mo
    file and builds its .exe executable to be used in OpenMDAO.
    
    By default, the wrapper initiation reads through the model parameter and 
    variable entries and their default values, and creates the inputs 
    and outputs of the wrapper component, correspondingly.
    
    OMModelWrapper(moFile[, pkgName]) -> new Python wrapper of OpenModelica model    
        moFile          : main model file name in String. '.mo' is not included 
        pkgName         : additional .mo file or library name in String 
                          ('.mo' must be included if there is in the name)
                          More than one package is not supported yet.
        
        
    startTime
        Simulation start time (float)
    
    stopTime
        Simulation stop time (float)

    stepSize
        Time step on which simulation data are recorded as result (float)
        
    tolerance
        Simulation solver accuracy (float)
        
    solver
        Name of the chosen solver, which OpenModelica supports (string) 
        
    execute(...)
        Execute the model and update the output
        
    Additional attributes will be accessible based on the parameter/variable
    definitions of the original OpenModelica to be wrapped.    
    """

    def __init__(self, moFile, pkgName=None):
        super(OMModelWrapper, self).__init__()

        self.moFile = moFile
        self._init_xml = moFile + "_init.xml"
        self._prm_attrib = []
        self._var_attrib = []
        self._wdir = os.getcwd()

        OM_build.build_modelica_model(usr_dir=self._wdir, fname=self.moFile, additionalLibs=pkgName)
        try:
            etree = lmm.get_etree(self._init_xml)
        except:
            sys.exit("FMI xml file incorrect or not exist")

        # Get the simulation settings
        sim_set = etree.find("DefaultExperiment").attrib
        for param_name in ['startTime', 'stopTime', 'stepSize', 'tolerance', 'solver']:
            self.add_param(param_name, val=sim_set[param_name])

        # Model param inputs
        model_variables = etree.find("ModelVariables").getchildren()
        file_name = self.moFile + ".mo"
        for var in model_variables:
            if (file_name in var.attrib['fileName']) and var.attrib['variability'] == "parameter":
                name = var.attrib['name']
                print ' ', name
                if var.find('Real') is not None:
                    value = float(var.find('Real').attrib['start'])
                    self.add_param(name, val=value)
                elif var.find('Integer') is not None:
                    value = int(var.find('Integer').attrib['start'])
                    self.add(name, val=value)
                elif var.find('Boolean') is not None:
                    if var.find('Boolean').attrib['start'] == "0.0":
                        value = 0
                    else:
                        value = 1
                    self.add_param(name, val=value)
                self._prm_attrib += [name]

        # Next, outputs are found. Any variables except "parameters" in the
        # model file becomes output.
        for var in model_variables:
            if (file_name in var.attrib['fileName']) and \
                            var.attrib['variability'] != "parameter":
                name = var.attrib['name']
                print ' ', name

                val = None
                if var.find('Real') is not None:
                    val = 0.0
                elif var.find('Integer') is not None:
                    val = 0
                elif var.find('Boolean') is not None:
                    val = 0

                try:
                    self.add_output(name, val=val)
                    self._var_attrib += [name]
                except:
                    pass

        self.add_output('time', val=0.0)
        self._var_attrib += ['time']

    def solve_nonlinear(self, params, unknowns, resids):
        """ 
        The .exe executable is run to obtain the simulation result of the
        OpenModelica model.
        """
        etree = lmm.get_etree(self._init_xml)

        # Update the sim settings to the element tree
        lmm.change_experiment(etree,
                              startTime=params['startTime'],
                              stopTime=params['stopTime'],
                              stepSize=str(params['stepSize']),
                              tolerance=str(params['tolerance']),
                              solver=params['solver'])

        # Update the parameters to the element tree
        prm_dict = {}
        for prm_name in self._prm_attrib:
            prm_dict[prm_name] = params[prm_name]
        lmm.change_parameter(etree, prm_dict)

        # Rebuild _init.xml with the updated element tree
        etree.write(self._init_xml)
        subprocess.call([self.moFile + '.exe'], shell=True)

        # Obtain the result from the result (.mat) file
        dd, desc = lmm.load_mat(self.moFile + '_res.mat')
        for var_name in self._var_attrib:
            unknowns[var_name] = dd[var_name]


def main():
    testModel = OMModelWrapper('SimAcceleration', 'VehicleDesign.mo')
    testModel.stopTime = 10

    testModel.execute()
    for i in xrange(testModel.time.size):
        print testModel.time[i], testModel.accel_time[i]


if __name__ == '__main__':
    main()
