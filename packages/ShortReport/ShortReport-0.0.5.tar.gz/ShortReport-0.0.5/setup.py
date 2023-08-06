from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Intended Audience :: Science/Research',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='ShortReport',
  version='0.0.5',
  description='It generates the Report of the dataset',
  long_description_content_type="text/markdown",
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Chiransh Singh Mehra , Raghav Aggarwal',
  author_email='singhchiransh4@gmail.com , raghavaggarwal200004@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['report','python','data-analysis','jupyter','ShortReport'], 
  packages=find_packages(),
  install_requires=['numpy','pandas','bokeh','ipywidgets','ipython','plotly','matplotlib','matplotlib-inline','seaborn','statistics'] 
)