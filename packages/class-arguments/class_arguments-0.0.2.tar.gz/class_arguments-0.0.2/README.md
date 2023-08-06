# Class-Arguments

a new written style for argparse

------------------

## 一种新的argparser写法

样例代码

```python
# example.py
from arguments import Argument, Option


class ComputeArg(Argument):
    """
    THIS IS A DESCRIPTION ! ! ! !

    a compute program
    """

    x = Option("x", type=int, help="variable x")
    y = Option("y", type=int, help="variable y")
    opt = Option("--operator", "-opt", type=str, required=True, help="operator")


if __name__ == "__main__":

    args = ComputeArg()

    if args.opt == "x":
        print(args.x * args.y)
    elif args.opt == "+":
        print(args.x + args.y)
    elif args.operator == "-":
        print(args.x - args.y)
    elif args.operator == "/":
        print(args.x / args.y)

```

样例输出

```cmd
❯ python example.py --help
usage: example.py [-h] --operator OPERATOR x y

THIS IS A DESCRIPTION ! ! ! ! a compute program

positional arguments:
  x                     variable x
  y                     variable y

options:
  -h, --help            show this help message and exit
  --operator OPERATOR, -opt OPERATOR
                        operator
```

```cmd
❯ python example.py 1 2 -opt + 
3
```

```cmd
❯ python example.py 1 2 --operator /
0.5
```

```cmd
❯ python example.py           
usage: example.py [-h] --operator OPERATOR x y
example.py: error: the following arguments are required: x, y, --operator/-opt
```

## 安装

`pip install class-arguments`

## 说明

- 开发动机纯粹为了取悦自己而对 argparser 模块进行了包装
  
- Option 的 `__init__` 参数与 argparser 模块的 `add_argument` 的参数完全一致,不改变原有编写习惯
