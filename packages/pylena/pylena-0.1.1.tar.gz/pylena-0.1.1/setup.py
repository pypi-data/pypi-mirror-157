# pylint: skip-file
from platform import platform
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.errors import OptionError, SetupError
from conans.client.conan_api import ConanAPIV1
import subprocess
import pybind11
import os

from typing import Tuple, List

#-------------------------------------------------------------
# CMake Wrapper
#-------------------------------------------------------------

def _from_subprocess_output(subprocess_result : subprocess.Popen) -> Tuple[str, str]:
    return subprocess_result.stdout.decode("utf-8"), subprocess_result.stderr.decode("utf-8")

class CMake:
    def __init__(self, path=os.path.abspath(os.path.dirname(__file__)), variables={}, verbose=False):
        self.path = path
        self.variables = variables
        self.verbose = verbose

    def add_variable(self, name, value):
        if self.variables.get(name) is not None:
            raise ValueError(f"CMake variable {name} already set to {self.variable[name]}")
        self.variables[name] = value

    def configure(self):
        print("-- Configuring CMake")
        out = subprocess.run(["cmake", self.path] + [f"-D{variable}={value}" for (variable, value) in self.variables.items()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if out.returncode != 0:
            stdout, stderr = _from_subprocess_output(out)
            raise SetupError(f"[ERROR]: No able to configure CMake\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
        print("-- CMake configured")

    def build(self, target=None):
        target_log = f" for target {target}" if target is not None else ""
        target_invoke = ["--target", target] if target is not None else []
        print(f"-- Building project{target_log}")
        out = subprocess.run(["cmake", "--build", "."] + target_invoke, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if out.returncode != 0:
            stdout, stderr = _from_subprocess_output(out)
            raise SetupError(f"[ERROR]: No able to build{target_log}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
        print(f"-- Project built{target_log}")


#-------------------------------------------------------------
# Extension class
#-------------------------------------------------------------

class ConanCMakeExtension(Extension):
    def __init__(self, name, build_type="Release"):
        if build_type not in ["Debug", "Release"]:
            raise OptionError(f"Extension build_type should be Debug or Release (Got {build_type}")
        self.build_type = build_type
        super().__init__(name, sources=[])

class ConanCMakeBuildExtension(build_ext):
    def run(self):
        for ext in self.extensions:
            if not isinstance(ext, ConanCMakeExtension):
                raise SetupError("Extension is not ConanCMakeExtension")
            self._build(ext)
        super().run()

    def _build(self, ext : ConanCMakeExtension):
        cwd = os.path.abspath(os.path.dirname(__file__))
        self.output_dir = os.path.join(os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name))), "pylena")
        self.is_msvc = False

        old_build_temp = self.build_temp
        self.build_temp = f"{cwd}/build"
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        os.chdir(self.build_temp)

        # Conan install
        conan = ConanAPIV1()
        conan.config_init()
        lrde_public = 'https://artifactory.lrde.epita.fr/artifactory/api/conan/lrde-public'
        if not lrde_public in [e.url for e in conan.remote_list()]:
            conan.remote_add("lrde-public", lrde_public)
        settings = self._make_conan_settings(conan, ext)
        conan.install(cwd, settings=settings, build=["missing", "openjpeg"], env=["CCFLAGS=", "CXXFLAGS="])
        
        # CMake
        cmake_variables = self._make_cmake_variable(ext)
        cmake = CMake(cwd, cmake_variables)
        cmake.configure()
        cmake.build()

        os.chdir(cwd)
        self.build_temp = old_build_temp

    def _make_conan_settings(self, conan : ConanAPIV1, ext : ConanCMakeExtension) -> List[str]:
        print("-- Using default conan profile")
        profile = conan.read_profile("default")
        if profile.settings["compiler"] == "Visual Studio":
            self.is_msvc = True
        settings = ["compiler.cppstd=20", f"build_type={ext.build_type}"]
        if profile.settings.get("compiler.libcxx") == "libstdc++":
            print("-- Conan default profile is using `compiler.libcxx=libstdc++`, which is not compatible with the Pylene library. Updating to `compiler.libcxx=libstdc++11`")
            settings.append("compiler.libcxx=libstdc++11")
        return settings

    def _make_cmake_variable(self, ext : ConanCMakeExtension):
        cmake_variables = {
            "CMAKE_BUILD_TYPE": ext.build_type,
            "CMAKE_TOOLCHAIN_FILE": f"{self.build_temp}/conan_toolchain.cmake",
            "pybind11_DIR": pybind11.get_cmake_dir(),
            "CMAKE_LIBRARY_OUTPUT_DIRECTORY": self.output_dir,
            "CMAKE_BUILD_PARALLEL_LEVEL": 8
        }
        if "PYTHON_EXECUTABLE" in os.environ:
            cmake_variables["PYTHON_EXECUTABLE"] = os.environ["PYTHON_EXECUTABLE"]
        if self.is_msvc:
            cmake_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"
        return cmake_variables

#-------------------------------------------------------------
# Setup
#-------------------------------------------------------------

setup(
    cmdclass={"build_ext": ConanCMakeBuildExtension},
    ext_modules=[ConanCMakeExtension("pylena_cxx")],
    platforms=["linux"],
    packages=find_packages(exclude=["tests", "doc"])
)