from setuptools import setup

package_name = 'my_g1_audio'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'my_g1_audio/silero_vad.onnx']),
    ],
    install_requires=[
        'setuptools',
        'numpy',
        'onnxruntime',
        'faster-whisper',
    ],
    zip_safe=True,
    maintainer='luolixin',
    maintainer_email='luolixin@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'brain_service = my_g1_audio.brain:main' ,
            'search_service = my_g1_audio.search_neuroxiv:main',
            'brain_update_service = my_g1_audio.brain_update:main',
            'ear_service = my_g1_audio.audio_bridge_node:main',
        ],
    },
)
