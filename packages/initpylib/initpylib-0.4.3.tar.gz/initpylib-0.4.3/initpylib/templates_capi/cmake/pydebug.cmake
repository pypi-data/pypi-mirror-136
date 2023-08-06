# CPM.cmake - CMake's missing package manager
# ===========================================
# See https://github.com/kirin123kirin/cmake/LICENSE for usage and update instructions.
#
# MIT License
# -----------
# This Module made for Could Not run debugger.(Access violation Error)
#    bug : https://github.com/scikit-build/scikit-build/issues/533
#    but Gerator is Ninja only.
#
## Usage include this cmake file After project function.
#  project(hoge)
#  include(cmake/pydebug.cmake)
# ===========================================

find_package(Python3 COMPONENTS Interpreter Development)
    set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${Python3_SITELIB}/skbuild/resources/cmake)
    find_package(PythonExtensions REQUIRED)

if (MSVC)
    SET(PY_COMMON_COMPILER_FLAG "/Zi /Od /Ob0")
    SET(PY_COMMON_LINKER_FLAG "/debug /INCREMENTAL")
else()
    SET(PY_COMMON_COMPILER_FLAG "-g -Xclang -gcodeview -O0")
    SET(PY_COMMON_LINKER_FLAG "")
endif()

# Add new build types
message("* PYDEBUG Adding build types...")

SET(CMAKE_CXX_FLAGS_PYDEBUG
    "${PY_COMMON_COMPILER_FLAG}"
    CACHE STRING "Flags used by the C++ compiler during coverage builds."
    FORCE )

SET(CMAKE_C_FLAGS_PYDEBUG
    "${PY_COMMON_COMPILER_FLAG}"
    CACHE STRING "Flags used by the C compiler during coverage builds."
    FORCE )

SET(CMAKE_MODULE_LINKER_FLAGS_PYDEBUG
    "${PY_COMMON_LINKER_FLAG}"
    CACHE STRING "Flags used for linking binaries during coverage builds."
    FORCE )

SET(CMAKE_EXE_LINKER_FLAGS_PYDEBUG
    "${PY_COMMON_LINKER_FLAG}"
    CACHE STRING "Flags used for linking binaries during coverage builds."
    FORCE )

SET(CMAKE_SHARED_LINKER_FLAGS_PYDEBUG
    "${PY_COMMON_LINKER_FLAG}"
    CACHE STRING "Flags used by the shared libraries linker during coverage builds."
    FORCE )

SET(CMAKE_STATIC_LINKER_FLAGS_PYDEBUG
    ""
    CACHE STRING "Flags used by the shared libraries linker during coverage builds."
    FORCE )

MARK_AS_ADVANCED(
    CMAKE_CXX_FLAGS_PYDEBUG
    CMAKE_C_FLAGS_PYDEBUG
    CMAKE_EXE_LINKER_FLAGS_PYDEBUG
    CMAKE_SHARED_LINKER_FLAGS_PYDEBUG
    CMAKE_STATIC_LINKER_FLAGS_PYDEBUG
    )

message("* Current build type is : ${CMAKE_BUILD_TYPE}")
