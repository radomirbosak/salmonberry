# Salmonberry

Machine learning powered RSS feed filtering

![salmonberry screenshot](screenshot.png)

Inspiration: https://blog.algorithmia.com/create-your-own-machine-learning-powered-rss/


## Model accuracy

| Date | Model | Test dataset | l_2 error (k-fold cross-validation) |
| ---- | ----- | ------------ | ----------------------------------- |
| 9.5.2018 | Tf-Idf + linear regression | Random 50 reddit ML/AI articles | 42% +- (3% std) |

* the *l_2 error* is defined as the the average euclidian distance between the predicted and target value. An error rate of 42% rougly means that 42 samples out of 100 are mislabeled.


To test model accuracy, run
```console
$ python accutest.py
```

## Changelog

| date     | changes |
| -------- | --------------------------------------- |
| 9.5.2018 | Added basic error estimation            |
| 8.5.2018 | Added article "niceness" predictions    |
| 7.5.2018 | Repo created, added basic rating system |


## Supported versions of python

* python 3.6 and newer
