from setuptools import setup

setup(
    name='DXR',
    version='1.0.0',
    packages=['Dxr_mqtt', 'Dxr_log', 'Dxr_bytes', 'Dxr_utils', 'Dxr_video'],
    install_requires=['paho-mqtt', 'pyyaml', 'grpcio', 'grpcio-tools', 'opencv-python'],
    author='luzhipeng',
    author_email='402087139@qq.com',
    license='MIT',
    url='http://pycn.me',
    package_data={
        '': ['*.so'],
        'bandwidth_reporter': ['*.so']
    },
    data_files=[
        ('', ['Dxr_video/lib/linux/*.so'])
    ]
)
