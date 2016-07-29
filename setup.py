import setuptools

setuptools.setup(name="d16i",
                 version="0.0.1",
                 description="Interpreter for Michael Nolan's d16 CPU",
                 author="Flaviu Tamas",
                 author_email="tamasflaviu@gmail.com",
                 license="MIT License",
                 packages=setuptools.find_packages(),
                 entry_points={
                     'console_scripts': ['d16i=d16i.cmdline:cmdline_main']
                 }
                 )
