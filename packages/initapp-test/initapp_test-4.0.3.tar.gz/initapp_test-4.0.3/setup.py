from setuptools import setup, find_packages

setup(
    name='initapp_test',
    version='4.0.3',
    include_package_data=True,
    packages=['conf', 'util','.'],
    install_requires=[
        'numpy==1.21.0',
        'ffmpeg_python==0.2.0',
        'opencv_python',
        'openpyxl',
        'pandas==1.3.2',
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
