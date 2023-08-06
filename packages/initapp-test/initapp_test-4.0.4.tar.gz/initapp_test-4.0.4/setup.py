from setuptools import setup, find_packages

setup(
    name='initapp_test',
    version='4.0.4',
    include_package_data=True,
    packages=['conf', 'util','.'],
    install_requires=[
        'numpy',
        'ffmpeg_python==0.2.0',
        'opencv_python',
        'openpyxl',
        'pandas',
        'pytesseract==0.3.8',
        'ffmpeg==1.4',
        'PyYAML',
    ],
    #packages= find_packages(),
    url='',
    license='',
    author='wangkejun',
    author_email='446093036@qq.com',
    description='initapp_test'
)
