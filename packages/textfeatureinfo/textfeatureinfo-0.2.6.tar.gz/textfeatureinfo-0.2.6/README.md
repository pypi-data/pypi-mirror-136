# textfeatureinfo

[![Documentation Status](https://readthedocs.org/projects/textfeatureinfo/badge/?version=latest)](https://textfeatureinfo.readthedocs.io/en/latest/?badge=latest) 
[![ci-cd](https://github.com/UBC-MDS/textfeatureinfo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/UBC-MDS/textfeatureinfo/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/UBC-MDS/textfeatureinfo/branch/master/graph/badge.svg?token=P29ZWp0Oib)](https://codecov.io/gh/UBC-MDS/textfeatureinfo)


## **Description**


In Natural Language Processing, it is common for users to try and engineer their own features from a given text. It can be difficult to extract certain features from text without using additional Python tools. This python package includes functions that allows data scientists to extract information from text features which can be useful for feature engineering, or in other data science projects. Our package, textfeatureinfo, will help gather summary information from plain text such as the number of punctuations in the text, the average word lengths and the percentage of fully capitalised words which can be useful information for feature engineering. Additionally, our package can also manipulate text data by removing the stopwords for the ease of future processing steps. 

Our package and functions are inspired from a lab in the course, DSCI 573 (Feature and model selection), of UBC MDS program, and are tailored based on our own experience and interest. 

## **Function Details**

- `count_punc`: This function will count and return the number of punctuations within a given text.
- `avg_word_len`: This function will calculate and return the average length of words within a given text.
- `perc_cap_words`: This function will calculate the percentage of fully capitalised words in the text.
- `remove_stop_words`: This function will find and remove the stop words in a text and will return the list of clean words.

## **Python Ecosystem**

In the field of text feature engineering, we are cognisant that there are well established packages in the Python ecosystem - specifically [`nltk`](https://www.nltk.org/), [`SpaCy`](https://stackabuse.com/removing-stop-words-from-strings-in-python/#usingthespacylibrary) and [`genism`](https://radimrehurek.com/gensim/). For punctuations, we are aware that the [`nltk.tokenize`](https://www.nltk.org/api/nltk.tokenize.html) and [`nltk.probability: FreqDist`](https://www.kite.com/python/docs/nltk.FreqDist) package can be used to find the number of words and punctuations in a string. To calculate average word length, [`nltk.word_tokenize()`](https://www.nltk.org/api/nltk.tokenize.html) is able to divide strings into lists of substrings. To count the number of fully capitalised words in a text, the above functions do provide a means to isolate these characters, but not to count them explicitly. In the case of stop words, there are several modules that identify stop words. For instance, `genius.parsing.preprocessing` module has the function `remove_stopwords()` which allows users to remove specific stop words, as listed in their docstring from a string. `nltk.corpus` has a module [`stopwords`](https://www.geeksforgeeks.org/removing-stop-words-nltk-python/) to remove stop words from the `text_token` list. The package `SpaCy` similarly has a list of stopwords stored in `sp.Default.stop_words` in English. 

Based on our experience in our previous module, all the functions that we seek to use require several lines of code. For example, to calculate the average word length, we need to extract the punctuation, count total number of characters, then averaging out over the number of words present. As such, we seek to simplify these tasks into functions that users, including ourselves, can employ in one line of code. 


## Installation

```bash
$ pip install textfeatureinfo
```

## Usage

In order to use the package please go through the following steps:

1. Create a new conda environment:

```bash
conda create --name textfeatureinfo python=3.9 -y
```

2. Activate the conda environment:

```bash
conda activate textfeatureinfo
```

3. Install the package:

```bash
pip install textfeatureinfo
```

4. Open Python:

```bash
python
```

5. In the Python prompt type the followings to import all the functions:

```bash
>>> from textfeatureinfo import textfeatureinfo
>>> from textfeatureinfo.textfeatureinfo import count_punc
>>> from textfeatureinfo.textfeatureinfo import avg_word_len
>>> from textfeatureinfo.textfeatureinfo import perc_cap_words
>>> from textfeatureinfo.textfeatureinfo import remove_stop_words
```

6. You can use the functions as below:

```bash
>>> count_punc("Hello, World!")
>>> avg_word_len("Hello, World!")
>>> perc_cap_words("THIS is a SPAm MESSage.")
>>> remove_stop_words("Tomorrow is a big day!")
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`textfeatureinfo` was created by Kiran, Jacqueline, Paniz, Lynn. It is licensed under the terms of the MIT license.

## Credits

`textfeatureinfo` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
