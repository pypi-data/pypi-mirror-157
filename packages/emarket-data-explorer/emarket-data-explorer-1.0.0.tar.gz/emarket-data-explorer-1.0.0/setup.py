import setuptools
setuptools.setup(

    #packages=setuptools.find_packages()

    #packages=setuptools.find_packages() + ['emarket_data_explorer.tools'],
    packages=setuptools.find_packages() + ['emarket_data_explorer'],
    #packages=setuptools.find_packages() + ['src.tools'],
    package_dir={
        #'src':'src/',
        #'src.tools':'tools',
        'emarket_data_explorer': 'src/emarket_data_explorer/',
        #'emarket_data_explorer.tools': 'tools',
    },


)