import os
import sys
import subprocess


def build_modelica_model(usr_dir, fname, additionalLibs="", extension=".mo", ):
    cur_dir = os.getcwd()
    omc_dir = os.getenv('OPENMODELICAHOME')
    print cur_dir, omc_dir
    if omc_dir is None:
        sys.exit('Can not find OpenModelica directory.')

    full_path_fname = os.path.join(usr_dir, fname + extension)

    # make the compiler happy
    full_path_fname = full_path_fname.replace("\\", "/")
    additionalLibs = additionalLibs.replace("\\", "/")

    print 'Generating flat modelica model and source code. (' + full_path_fname + ')'

    cmd_compile = os.path.join(omc_dir, 'bin',
                               'omc') + ' +q +s "' + full_path_fname + '" "' + additionalLibs + '" ModelicaServices Modelica'

    print 'Flat model and generated code are ready. (' + full_path_fname + ')'

    print 'Compiling the code into an executable package. (' + fname + ')'

    subprocess.call(cmd_compile, shell=True)

    subprocess.call('make -f ' + fname + '.makefile', shell=True)

    print 'Done. (' + full_path_fname + ')'
