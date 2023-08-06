import sys, os, setuptools

libraries = []
library_dirs = []
extra_compile_args = []

if sys.platform == "win32":
    library_dirs = [
        "glfw/build/src/Release", "freetype/build/Release",
        "Chipmunk2D/build/src/Release"
    ]

    libraries = [
        "glfw3", "opengl32", "kernel32", "user32", "gdi32",
        "winspool", "shell32", "ole32", "oleaut32", "uuid",
        "comdlg32", "advapi32", "freetype", "chipmunk"
    ]

elif sys.platform == "darwin":
    library_dirs = ["glfw/build/src", "freetype/build", "Chipmunk2D/build/src"]
    os.environ["LDFLAGS"] = "-framework OpenGL -framework IOKit -framework Cocoa"
    libraries = ["glfw3", "freetype", "chipmunk"]

elif sys.platform == "linux":
    library_dirs = ["glfw/build/src", "freetype/build", "Chipmunk2D/build/src"]
    extra_compile_args = ["-Wextra", "-Wno-comment", "-Wfloat-conversion"]

    libraries = [
        "glfw3", "GL", "m", "X11", "pthread", "Xi", "Xrandr",
        "dl", "rt", "png", "freetype", "z", "chipmunk"
    ]

setuptools.setup(
    name = "JoBase",
    version = "2.1",
    author = "Reuben Ford",
    author_email = "hello@jobase.org",
    description = "Fast Python Game Library",
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    url = "https://jobase.org",
    python_requires = ">=3.6",
    license = "GPL-3.0-or-later",
    packages = ["JoBase"],
    package_data = {"JoBase": ["images/*.png", "examples/*.py", "fonts/*.ttf"]},
    include_package_data = True,

    keywords = [
        "fast", "beginner", "extension",
        "library", "opengl", "glfw",
        "games", "c", "children", "freetype"
    ],

    project_urls = {
        "Source": "https://github.com/JoBase/JoBase",
        "Documentation": "https://jobase.org/reference"
    },

    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    
    ext_modules = [
        setuptools.Extension(
            "JoBase.__init__", ["src/module.c", "src/glad.c"],

            include_dirs = [
                "include", "glfw/include",
                "freetype/include", "Chipmunk2D/include"
            ],

            extra_compile_args = extra_compile_args,
            library_dirs = library_dirs,
            libraries = libraries)
    ])