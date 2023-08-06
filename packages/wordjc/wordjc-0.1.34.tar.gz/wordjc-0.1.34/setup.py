from setuptools import setup, find_packages

VERSION = '0.1.34' 
DESCRIPTION = 'Scripture (Word) Visualization'
LONG_DESCRIPTION = 'Package to provide API for the Holy Scripture visualization'

# Setting up
setup(
       # the name must match the folder name 'wordjc'
        name="wordjc", 
        version=VERSION,
        author="Johnny Cheng",
        author_email="<drjohnnycheng@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['numpy', 'pandas', 'importlib_resources', 'regex', 'nltk', \
                          'matplotlib', 'wordcloud', 'pillow', 'jieba', \
                          'gensim', 'pyLDAvis'],

        include_package_data=True,
        package_dir={"wordjc":  "wordjc"},
        package_data={"wordjc": ["data/*.*", "dictionary/*.*", "images/*.*"]},

        keywords=['word', 'scripture', 'visualization'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Religion",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
