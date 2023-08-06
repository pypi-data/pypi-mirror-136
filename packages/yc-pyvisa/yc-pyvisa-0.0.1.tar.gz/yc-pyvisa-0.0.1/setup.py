from setuptools import setup
from setuptools import find_packages
requires = [
"threading","statistics","pyvisa","tkinter","ctypes.wintypes"
]
with open('README.md','r') as f:
    readme = f.read()
setup(
    name='yc-pyvisa',
    version='0.0.1',
    description='=用于YICHIP内部仪器设备的控制',
    author='Susunl',
    author_email='1253013130@qq.com',
    long_description = readme,
    license='MIT',
    packages = find_packages(),
    include_package_data = True,
    python_requires=">=3.5",
    zip_safe=False,
    platforms = 'any',
    install_requires = [],
    url="https://gitee.com/susunl/yc_-pyvisa",
    classifiers=[ 'Programming Language :: Python :: 3'],
)
