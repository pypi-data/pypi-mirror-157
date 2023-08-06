import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='rcn',
     version='1',
     author="Mayank Shinde",
     author_email="mayank31313@gmail.com",
     description="CLI Interface for RCN",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/mayank31313/rcn-cli",
     packages=setuptools.find_packages(),
     # packages=['rcn'],
     keywords=['ior','iot','network_robos', 'control_net'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
         'Intended Audience :: Developers',
     ]
 )