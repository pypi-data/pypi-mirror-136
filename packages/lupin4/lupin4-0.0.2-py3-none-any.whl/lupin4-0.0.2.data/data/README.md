

# lupin4

[![PyPi version][pypi-image]][pypi-url]
[![Python version][python-image]][docs-url]



lupin4 is developed to facilitate the dichotomy model development work.

## Usage
lupin4 is designed to develop standard scorecard model. It contains the main steps as follows:  
1.Exploratory Data Analysis  
lupin4.detect()  
lupin4.quality()  
lupin4.IV()  
lupin4.VIF()  

2.Feature Selection  
lupin4.select()  
lupin4.stepwise()  

3.Binnings  
lupin4.Combiner()  
lupin4.WOETransformer()  
lupin4.bin_stats()  
lupin4.bin_plot()  

4.Modeling  
lupin4.ScoreCard()  

5.Performance Measure  
lupin4.perform()  
lupin4.LIFT()  
lupin4.score_plot()  
lupin4.KS_bucket()  
lupin4.PSI()  
lupin4.KS()  
lupin4.AUC()  

Also lupin4 provides a function which runs all the steps above automaticly:  
lupin4.auto_model()  

For detailed usage, please refer to the wiki. Enjoy.  


## Install


via pip

```bash
pip install lupin4 --upgrade -i https://pypi.org/simple
```

via source code

```bash
python setup.py install
```

install_requires = [
        'numpy >= 1.18.4',
        'pandas >= 0.25.1, <=0.25.3',
        'scipy >= 1.3.2',
        'scikit-learn =0.22.2',
        'seaborn >= 0.10.1',
        'statsmodels >= 0.13.1',
        'tensorflow >= 2.2.0, <=2.5.0',
        'hyperopt >= 0.2.7',
        'pickle >= 4.0',
    ]



[pypi-image]: https://img.shields.io/badge/pypi-V0.0.1-%3Cgreen%3E
[pypi-url]: https://www.baidu.com
[python-image]: https://img.shields.io/pypi/pyversions/toad.svg?style=flat-square
[docs-url]: https://www.baidu.com

