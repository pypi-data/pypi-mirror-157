from conans import ConanFile, CMake


class ${project_camel_name}Conan(ConanFile):
    name = "${project_name}"
    license = "GNU Affero General Public License v3.0"
    author = "${project_author}"
    homepage = "${project_homepage}"
    url = "${project_url}"  # Package recipe repository url here, for issues about the package
    description = "${project_description}"
    topics = ("${project_name}",)
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"
    exports_sources = "%s/*" % name, "test_package/*.*"
    build_requires = "cpp_project_framework/1.0.0", "gtest/1.10.0", "doxygen/1.8.20", "benchmark/1.5.1"
    exports_resources = ".gitignore", "LICENSE", "conanfile.txt", "CMakeLists.txt", "make.bat", "Makefile", "cpp_project_framework_callables.cmake", "cpp_project_framework.cmake"

    def export_sources(self):
        for resource in self.exports_resources:
            self.copy(resource)
            self.copy(resource, dst="res")

    def build(self):
        cmake = CMake(self)
        self.run("conan install conanfile.txt -b missing -s build_type=%s -if ." % cmake.build_type)
        cmake.configure(source_folder=self.name)
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/cpp_project_framework %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include/%s" % self.name, src=self.name)
        self.copy("*.hpp", dst="include/%s" % self.name, src=self.name)
        self.copy("*.hxx", dst="include/%s" % self.name, src=self.name)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        for resource in self.exports_resources:
            self.copy(resource, dst="res", src="res")

    def package_info(self):
        postfix = "_d" if self.settings.build_type == "Debug" else ""
        name_with_postfix = self.name + postfix
        self.cpp_info.libs = []
