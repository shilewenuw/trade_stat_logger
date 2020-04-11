from distutils.core import setup
setup(
  name = 'trade_stat_logger',
  packages = ['trade_stat_logger'],
  version = '0.2',
  license='MIT',
  description = 'Log trades and analyze performance, risk, and other statistical measures',
  long_description = 'View documentation at https://github.com/shilewenuw/trade_stat_logger/README.md',
  author = 'Shile Wen',
  author_email = 'shilewen1@gmail.com',
  url = 'https://github.com/shilewenuw',
  download_url = 'https://github.com/shilewenuw/trade_stat_logger/archive/v_01.tar.gz',
  keywords = ['PYTHON', 'STOCKS', 'TRADING', 'BACKTEST', 'STATISTICS'],
  install_requires=[
          'numpy', 'pandas', 'pytz', 'matplotlib', 'yahoo_fin'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)