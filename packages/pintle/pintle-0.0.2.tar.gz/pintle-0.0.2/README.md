<h1 align="center"> Pynboard </h1> <br>

[![Tests](https://github.com/nkrokhmal/pintle/actions/workflows/python-package.yml/badge.svg?branch=master)](https://github.com/AlexandreDecan/portion/actions/workflows/python-package.yaml)

<p align="center">
  <img alt="Pynboard" title="GitPoint" src="https://github.com/nkrokhmal/pintle/blob/master/imgs/logo.png?raw=true" width="450">
</p>

The library `pynboard` offers a wide range of options when working with intervals. 

- Support interval creation for any comparable objects.
- The ability to create infinite intervals and to work in the affinely extended system.
- Support for a many operations such as union, intersection, difference and etc.
- Visualization of intervals.

## Some requirements to interval value objects
tratata

## How to install and import
```python
import pynboard.Intervals as I
```


## Intervals creation

Each set of intervals consist of atomic intervals. Atomic interval can be one of the following types:

- Open atomic interval:

    ```python
    >> I.open(0, 1)
    (0, 1)
    >>I.open(-I.inf, 0) 
    (-inf, 0)
    ```
- Closed atomic interval:
    ```python
    >> I.closed(0, 1)
    [0, 1]
    >>I.open(0, I.inf) # It's possible to create intervals in extended space 
    [0, inf]
    ```
- Open closed atomic interval:
    ```python
    >> I.open_closed(0, 1)
    (0, 1]
    ```
- Closed open atomic interval:
    ```python
    >> I.closed_open(0, 1)
    [0, 1)
    ```
- Single point:
    ```python
    >> I.point(1)
    [1]
    ```

## paragraph about and, or operations
tratata
