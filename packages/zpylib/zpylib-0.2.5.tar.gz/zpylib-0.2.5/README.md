# Zpy Lib

Zpy Lib - Chinese programming lib



## 快速开始

1. 通过pip安装

```shell
pip install zpylib
```

2. 创建后缀为`.zpy`的文件（例：`test.zpy`）

```shell
touch test.zpy
```

3. 编写代码

```zpy
星星数 = 12
如果 星星数 % 2 != 1:
    星星数 += 1
对于 层数 在 范围(舍入((星星数-1)/2)+1):
    星星 = '*'*(层数*2+1)
    打印(星星.center(星星数, " "))
```

4. 通过命令行运行文件

```shell
zpy run test.zpy
```

5. 编译成python文件

```shell
zpy build test.zpy
```

