from conans import ConanFile, CMake, tools


class FmilibraryConan(ConanFile):
    name = "FMILibrary"
    version = "2.0.3"
    license = "https://svn.jmodelica.org/FMILibrary/tags/2.0.3/LICENSE.md"
    url = "https://github.com/kyllingstad/conan-FMILibrary"
    description = "An implementation of the FMI standard which enables FMU import in applications"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def source(self):
        tools.download("https://jmodelica.org/fmil/FMILibrary-2.0.3-src.zip", "FMILibrary-2.0.3-src.zip")
        tools.unzip("FMILibrary-2.0.3-src.zip")
        tools.patch(patch_file="build-static-c99snprintf.patch")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("FMILibrary-2.0.3/CMakeLists.txt", "project (FMILibrary)",
                              '''project (FMILibrary)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(
            source_folder="FMILibrary-2.0.3",
            defs={
                "FMILIB_BUILD_STATIC_LIB": "OFF" if self.options.shared else "ON",
                "FMILIB_BUILD_SHARED_LIB": "ON"  if self.options.shared else "OFF",
                "FMILIB_BUILD_TESTS": "OFF",
                "FMILIB_INSTALL_PREFIX": self.build_folder + "/install",
            })
        cmake.build()
        cmake.install()

    def package(self):
        fmilib_install_dir = self.build_folder + "/install"
        self.copy("*.h", dst="include", src=fmilib_install_dir+"/include")
        self.copy("fmilib*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*fmilib.a", dst="lib", keep_path=False)

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["fmilib_shared"]
        else:
            self.cpp_info.libs = ["fmilib"]

