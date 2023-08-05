# Suppres

Decorator to ignore exceptions in functions. A simple wrapper around contextlib.suppress.

## Install

```
pip install suppress
```

## Usage

```python
from suppress import suppress


@suppress(ZeroDivisionError)
def zero_division_error_function():
    return 1 / 0


def main():
    print('First print')
    zero_division_error_function()
    print('Second print')


if __name__ == '__main__':
    main()
```
Output:

```
First print
Second print
```
## Async Usage
```python
import asyncio
from suppress import async_suppress


@async_suppress(ZeroDivisionError)
async def zero_division_error_function():
    return 1 / 0


async def main():
    print('First print')
    await zero_division_error_function()
    print('Second print')


if __name__ == '__main__':
    asyncio.run(main())
```
Output:

```
First print
Second print
```