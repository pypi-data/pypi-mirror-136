from setuptools import setup, find_packages
  
setup(
        name ='TrashPandasPiervn',
        version ='1.0.1',
        author ='Aleksander Łopusiewicz',
        author_email ='oleklopusiewicz@gmail.com',
        scripts=['TrashPandas/scoreboard.py', 'TrashPandas/window.py', 'TrashPandas/units.py', 'TrashPandas/levels.py'],
        description ='Simple game written with pygame.',
        license ='MIT',
        packages = find_packages(),
        entry_points ={
            'console_scripts': [
                'trashpandas = TrashPandas.main:main'
            ]
        },
        classifiers =[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        keywords ='TrashPandas',
        install_requires = ['pygame', 'sqlalchemy'],
        zip_safe = False
)