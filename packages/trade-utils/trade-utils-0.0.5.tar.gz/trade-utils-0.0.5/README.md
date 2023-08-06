# algo
Set of tools for algorithmic trading

# Contributing 
To get started [install pipenv](https://pipenv.pypa.io/en/latest/install/#crude-installation-of-pipenv)

Install dependencies
```
pipenv install --dev
```

Active environment
```
pipenv shell
```

To use VSCode `Pyhton: Select Interpreter` and choose suggested PipEnv environment.

At this point version update is manual. 

# Building And uploading
```sh
python -m build
twine upload ./dist/* --verbose
```


TODO: 
  * make config retry loading config file ie do not assign empty config on fail
    Now it raises error only once on the first attempt to access config. Then it returns empty/default values
  * make `install_requires` dynamic based on `Pipfile`