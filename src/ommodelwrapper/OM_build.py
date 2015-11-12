import os
import sys
import subprocess


def build_modelica_model(usr_dir, fully_qualified_class_name, additional_libs="", extension=".mo", ):
    cur_dir = os.getcwd()
    omc_dir = os.getenv('OPENMODELICAHOME')
    print cur_dir, omc_dir
    if omc_dir is None:
        sys.exit('Can not find OpenModelica directory.')

    class_name = fully_qualified_class_name.split('.')[-1]

    # make the compiler happy
    additional_libs = additional_libs.replace("\\", "/")

    print 'Generating flat modelica model and source code. (' + fully_qualified_class_name + ')'

    # Get the package name, if applicable
    if additional_libs != "":
        addl_lib_filename = os.path.basename(additional_libs)
        library_path = os.path.dirname(additional_libs)

        if addl_lib_filename == "package.mo":
            addl_lib_filename = os.path.basename(os.path.dirname(additional_libs))
            library_path = os.path.dirname(library_path)

        elif addl_lib_filename.endswith(".mo"):
            addl_lib_filename = os.path.splitext(os.path.basename(addl_lib_filename))[0]

    mos_lines = []
    mos_lines.append("// OpenModelica script file to run a model")
    mos_lines.append("loadModel(Modelica, { \"3.2.1\" });")
    if additional_libs != "":
        mos_lines.append("loadModel( %s );" % addl_lib_filename)
    mos_lines.append(
        "translateModel( %s, fileNamePrefix=\"%s\" );" % (fully_qualified_class_name, class_name))
    mos_lines.append("getErrorString();")

    mos_content = str.join('\n', mos_lines)
    mos_filename = "%s.mos" % class_name
    with open(mos_filename, 'w') as f:
        f.write(mos_content)

    cmd_compile = os.path.join(omc_dir, 'bin', 'omc') + ' ' + mos_filename

    my_env = os.environ
    lib_paths = ""
    if additional_libs != "":
        lib_paths = library_path

    if 'OPENMODELICALIBRARY' in my_env:
        my_env['OPENMODELICALIBRARY'] = lib_paths + os.pathsep + my_env['OPENMODELICALIBRARY']
    else:
        om_std_lib = os.path.join(os.environ['OPENMODELICAHOME'], 'lib', 'omlibrary')
        om_lib = {'OPENMODELICALIBRARY': '{0}{1}{2}'.format(lib_paths, os.pathsep, om_std_lib)}
        print "No environment variable OPENMODELICALIBRARY found, created;"
        my_env.update(om_lib)

    subprocess.call(cmd_compile,
                    shell=True,
                    env=my_env)

    print 'Flat model and generated code are ready. (' + fully_qualified_class_name + ')'
    print 'Compiling the code into an executable package. (' + fully_qualified_class_name + ')'

    subprocess.call('make -f ' + class_name + '.makefile', shell=True)

    print 'Done. (' + fully_qualified_class_name + ')'
