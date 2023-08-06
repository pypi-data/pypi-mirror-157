# pylint: skip-file
from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class PyleneNumpyConan(ConanFile):
    name = "pylene-numpy"
    version = "head"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True, "pylene:fPIC": True}
    exports_sources = "CMakeLists.txt", "pylene-numpy/*", "LICENCE"
    requires = ["pylene/head@lrde/unstable", "pybind11/2.9.2"]
    generators = "CMakeDeps"

    def configure(self):
        tools.check_min_cppstd(self, 20)
        if self.options.shared:
            self.options.fPIC = True
        if self.settings.os != "Windows" and not self.options.fPIC:
            self.output.error("pylene-numpy is intended to be linked to python module and should be compiled with fPIC")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def layout(self):
        self.folders.source = "."
        self.folders.build = "build"
        self.folders.generators = "build"

        self.cpp.source.includedirs = ["pylene-numpy/include"]

        self.cpp.build.libdirs = ["pylene-numpy"]

        self.cpp.package.libs = ["lib"]
        self.cpp.package.includedirs = ["include"]

    def build(self):
        variables = {"BUILD_PYLENA": "OFF"}
        cmake = CMake(self)
        cmake.configure(variables)
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "pylene-numpy::pylene-numpy")

        # Core pylene numpy
        self.cpp_info.requires = ["pylene::core"]
        self.cpp_info.libs = ["pylene-numpy"]
        self.cpp_info.system_libs = ["pybind11::pybind11"]

    def package_id(self):
        del self.info.settings.compiler.cppstd
