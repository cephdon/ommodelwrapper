===========
Usage Guide
===========

Using OMModelWrapper
=========================

This is a wrapper of an OpenModelica model. It compiles OpenModelica's ``.mo``
file and builds its ``.exe`` executable to be used in OpenMDAO using OpenModelica 
compiler installed on your computer.

By default, the wrapper initiation reads through the model parameter and 
variable entries with their default values and creates the inputs 
and outputs of the wrapper component correspondingly.

OMModelWrapper(moFile[, pkgName]) -> new Python wrapper of OpenModelica model    

where

::

  moFile:   main model file name in String. `.mo` should not be included.
    
  addl_pkg_abs_path:  additional .mo file or library name in String
                      ('.mo' must be included if there is in the name)
                      More than one package is not supported yet.
                      Must be absolute path

The following parameters are created for all OpenModelica wrapping applications:
    
**startTime**
    Simulation start time (float)

**stopTime**
    Simulation stop time (float)

**stepSize**
    Time step on which simulation data are recorded as result (float)
    
**tolerance**
    Simulation solver accuracy (float)
    
**solver**
    Name of the chosen solver, which OpenModelica supports (string) 

With all the above, additional attributes will be accessible based on the parameter/variable
definitions of the original OpenModelica to be wrapped.    


Example
=========
In the distribution directory ``ommodelwrapper/test``, there are two OpenModelica
files, ``SimAcceleration.mo`` and ``VehicleDesign.mo``. The two files are basically
an OpenModelica translation of the vehicle design example included in OpenMDAO. 
Of the two files, ``SimAcceleration.mo`` is the main model file, and ``VehicleDesign.mo`` 
is the package that contains all the classes and function declarations used by
SimAcceleration model.

To generate an OpenMDAO component wrapping the OpenModelica's SimAcceleration 
model, you write in your script:

::

  testModel = OMModelWrapper('SimAcceleration','<repository_root>/ommodelwrapper/test/VehicleDesign.mo')

where ``<repository_root>`` is the absolute path to this repository.

This will create the testModel that is an instance of OpenModelica's SimAcceleration model.
The testModel is ready to use. The following example lines execute the model and
provide the 0 to 100km/hr time of the car:

::

    problem = Problem()
    root = problem.root = Group()
    test_model = OMModelWrapper('SimAcceleration', addl_lib_path)
    root.add('simacceleration', test_model)
    root.add('simtime', IndepVarComp('duration', val='15.0'))
    root.connect('simtime.duration', 'simacceleration.stopTime')

    problem.setup()
    problem.run()

    print 'simacceleration.accel_time: ', problem['simacceleration.accel_time']

