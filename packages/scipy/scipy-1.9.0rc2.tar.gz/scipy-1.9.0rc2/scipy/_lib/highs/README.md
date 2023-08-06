# HiGHS - Linear optimization software

[![Build Status](https://github.com/ERGO-Code/HiGHS/workflows/build/badge.svg)](https://github.com/ERGO-Code/HiGHS/actions?query=workflow%3Abuild+branch%3Amaster)

HiGHS is a high performance serial and parallel solver for large scale sparse
linear programming (LP) problems of the form

    Minimize c^Tx subject to L <= Ax <= U; l <= x <= u

and mixed integer programming (MIP) problems of the same form, for whch some of the variables must take integer values. It is mainly written in C++ with OpenMP directives, but also has some C. It has been developed and tested on various Linux, MacOS and Windows installations using both the GNU (g++) and Intel (icc) C++ compilers. Note that HiGHS requires (at least) version 4.9 of the GNU compiler. It has no third-party dependencies.

HiGHS is based on the dual revised simplex method implemented in HSOL, which was originally written by Qi Huangfu. Features such as presolve, crash and advanced basis start have been added by Julian Hall, Ivet Galabova. Other features, and interfaces to C, C#, FORTRAN, Julia and Python, have been written by Michael Feldmeier. The MIP solver has been written by Leona Gottwald.

Although HiGHS is freely available under the MIT license, we would be pleased to learn about users' experience and give advice via email sent to highsopt@gmail.com.

Reference
---------
If you use HiGHS in an academic context, please acknowledge this and cite the following article.
P
arallelizing the dual revised simplex method
Q. Huangfu and J. A. J. Hall
Mathematical Programming Computation, 10 (1), 119-142, 2018.
DOI: 10.1007/s12532-017-0130-5

http://www.maths.ed.ac.uk/hall/HuHa13/


Documentation
-------------

The rest of this file gives brief documentation for HiGHS. Comprehensive documentation is available via https://www.highs.dev.

Download
--------

Precompiled executables are available for a variety of platforms at https://github.com/JuliaBinaryWrappers/HiGHS_jll.jl/releases

Note that HiGHS is still pre-1.0, so the version numbers in the releases do not match versions of HiGHS in this repository.

For Windows users: if in doubt, choose the `x86_64-w64-mingw32-cxx11.tar.gz` file

For Mac users: choose the `x86_64-apple-darwin.tar.gz` file.


Compilation
-----------

HiGHS uses CMake as build system. First setup
a build folder and call CMake as follows

    mkdir build
    cd build
    cmake ..

Then compile the code using

    make

This installs the executable `bin/highs`.
The minimum CMake version required is 3.15.

Testing
-------

To perform a quick test whether the compilation was successful, run

    ctest

Run-time options
----------------

In the following discussion, the name of the executable file generated is
assumed to be `highs`.

HiGHS can read plain text MPS files and LP files and the following command
solves the model in `ml.mps`

    highs ml.mps

HiGHS options
-------------
Usage:
    highs [OPTION...] [file]

      --model_file arg       File of model to solve.
      --presolve arg         Presolve: "choose" by default - "on"/"off" are alternatives.
      --solver arg           Solver: "choose" by default - "simplex"/"ipm"/"mip" are alternatives.
      --parallel arg         Parallel solve: "choose" by default - "on"/"off" are alternatives.
      --time_limit arg       Run time limit (double).
      --options_file arg     File containing HiGHS options.

  -h, --help                 Print help.

Language interfaces and further documentation
---------------------------------------------

There are HiGHS interfaces for C, C#, FORTRAN, and Python in
HiGHS/src/interfaces, with example driver files in
HiGHS/examples. Documentation is availble via https://www.highs.dev/, and we are happy to give a reasonable level of support via
email sent to highsopt@gmail.com.

Parallel code
-------------

Parallel dual simplex is available in HiGHS under Linux, but not on
Windows or MacOS due to issues relating to OpenMP. This situation
should improve when parallelism in HiGHS is handled via the native C++
instructions. However, performance gain with the simplex solver is
unlikely to be significant. At best, speed-up is limited to the number
of memory channels, rather than the number of cores.

If OpenMP is found by CMake, the parallel code may be used. The number of threads used at run
time is the value of the environment variable `OMP_NUM_THREADS`. For example,
to use HiGHS with eight threads to solve `ml.mps` execute

    export OMP_NUM_THREADS=8
    highs --parallel ml.mps

If `OMP_NUM_THREADS` is not set, either because it has not been set or due to
executing the command

    unset OMP_NUM_THREADS

then all available threads will be used.

If run with `OMP_NUM_THREADS=1`, HiGHS is serial. The `--parallel` run-time
option will cause the HiGHS parallel dual simplex solver to run in serial. Although this
could lead to better performance on some problems, performance will typically be
diminished.

When compiled with the parallel option and `OMP_NUM_THREADS>1` or unset, HiGHS
will use multiple threads. If `OMP_NUM_THREADS` is unset, HiGHS will try to use
all available threads, so performance may be very slow. Although the best value
will be problem and architecture dependent, `OMP_NUM_THREADS=8` is typically a
good choice. Although HiGHS is slower when run in parallel than in serial for
some problems, it is typically faster in parallel.

HiGHS Library
-------------

HiGHS is compiled in a shared library. Running

`make install`

from the build folder installs the library in `lib/`, as well as all header files in `include/`. For a custom
installation in `install_folder` run

`cmake -DCMAKE_INSTALL_PREFIX=install_folder ..`

and then

`make install`

To use the library from a CMake project use

`find_package(HiGHS)`

and add the correct path to HIGHS_DIR.

Compiling and linking without CMake
-----------------------------------

An executable defined in the file `use_highs.cpp` (for example) is linked with the HiGHS library as follows. After running the code above, compile and run with

`g++ -o use_highs use_highs.cpp -I install_folder/include/ -L install_folder/lib/ -lhighs`

`LD_LIBRARY_PATH=install_folder/lib/ ./use_highs`

Interfaces
----------

Julia
-----

- A Julia interface is available at https://github.com/jump-dev/HiGHS.jl.

Rust
----

- HiGHS can be used from rust through the [`highs` crate](https://crates.io/crates/highs). The rust linear programming modeler [**good_lp**](https://crates.io/crates/good_lp) supports HiGHS. 

Javascript
----------

HiGHS can be used from javascript directly inside a web browser thanks to [highs-js](https://github.com/lovasoa/highs-js). See the [demo](https://lovasoa.github.io/highs-js/) and the [npm package](https://www.npmjs.com/package/highs).
