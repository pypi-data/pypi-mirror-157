Pythonesque is a package of functions to make Python code more readable to non-Python programmers.

![do not understand](https://media.giphy.com/media/SRnCiL9v0TgaBbe8l7/giphy.gif)

Python is one of the most readable programming languages. 

However, there are some areas which are are not intuitive to non-Python progammers, and especially non-programmers. 

For example, the range() function and its parameters can be a source of confusion.

Other programming constructs, eg. modulus operator, are obvious to programmers, but can be a real stumbling block for others.

The aim of this package is to to facilitate writing pseudo code (that is actually Python code) in order to to convey logic more easily to non-Python programmers, or perhaps even non-programmers.

If Python code can be written to resemble pseudo code, it would be a great way to:

* communicate your ideas

* demonstrate logic

* allow stakeholders to play with your pseudo code

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Pythonesque.
```bash
pip install pythonesque
```


## Usage
Example:

```python
from pythonesque import consecutive_numbers
# or specify sub-modules:
# from pythonesque.series import consecutive_numbers

# much less confusing to non-programmers than "range(10, 0, -1)"
for count in consecutive_numbers(10, 1):
    print(count)
print("Blast off!")
```

*For more examples, please refer to the [Documentation](https://stock90975.github.io/pythonesque/series.html)*


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.


## License

[MIT](https://choosealicense.com/licenses/mit/)




