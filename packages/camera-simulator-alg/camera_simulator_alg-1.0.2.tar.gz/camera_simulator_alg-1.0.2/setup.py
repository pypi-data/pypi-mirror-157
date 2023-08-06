from distutils.core import setup

setup(
    name = 'camera_simulator_alg',        
    packages = ['camera_simulator_alg'],  
    version = '1.0.2',     
    license='MIT',       
    description = 'Python library for creating a basic lens and sensor simulator',  
    author = 'Juan Cepeda',                
    author_email = 'juancepeda.gestion@gmail.com',      
    url = 'https://github.com/Juanchobanano/algolux_test', 
    download_url = 'https://github.com/Juanchobanano/algolux_test/archive/refs/tags/1.0.2.tar.gz',    
    keywords = ['ALGOLUX', 'CAMERA', 'LENS', "SENSOR", "SIMULATOR"],  
    
    entry_points = {
        "console_scripts" : [
            "pysensor = camera_simulator_alg.utils:mymean",
        ],
    },

    install_requires=[           
            'numpy',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)