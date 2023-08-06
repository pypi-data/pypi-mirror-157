from setuptools import setup, find_packages


classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='raghavcalculator',
  version='0.0.20',
  description='A very basic calculator',
  long_description_content_type="text/markdown",
  # long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Chiransh Singh Mehra , Raghav Aggarwal',
  author_email='singhchiransh4@gmail.com , raghavaggarwal200004@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['report','python','calculator'], 
  packages=find_packages(),
  install_requires=['bashplotlib', 'numpy','pandas','bokeh','ipywidgets','ipython','plotly','matplotlib','matplotlib-inline','seaborn','statistics'] 
)