# XLRP使用手册
> xlrp是用于生成excel报告的python库，可以在不破坏当前代码结构的基础上，添加测试用例分类，生成报告，可应用大部分数据驱动场景

## 安装和导入
```python=
pip install xlrp    # 安装

from XLRP import xlrp
```

## 用例分类
> 对于类、方法的形式，通常一个方法代表一个用例，所以，在方法上可以使用装饰器的形式，对于常见excel驱动，单函数的形式，可以使用with的形式进行分类

```python=
# 装饰器形式

@xlrp.SysName("测试模块")
class ExcelTest:
    @xlrp.ModelName('模块1')
    @xlrp.StepName("步骤1")
    def xl_pr(self, a, b):
        print(a, b)

# with形式
@xlrp.SysName("系统名称")
def excel_data():
    with xlrp.ModelName("模块1"):
        with xlrp.StepName("用例1):
            print(123)
```

## 单函数用例运行
> 对于单个用例的形式，可以直接使用run方法进行运行，并可以向其中传入一个列表作为参数，列表中一个元素代表一个用例

```python=
def pr(a, b):
    print(a + b)

# Runner可以接受一个布尔值参数，用来确定是否立即显示创建的图像
runner = Runner()
runner.run(excel_data, [(1, 3), (4, 5), (6, 7)])
```

## 运行类
> 对于类的形式，对方法的命名做了一定的规定，类中的方法，必须是以 **"xl"** 开头的，才会作为xlrp的用例运行


```python=
@xlrp.SysName("测试")
Class ExcelData:
    @xlrp.ModelName("模块1")
    @xlrp.StepName("用例1")
    def xl_pr():
        print(123)
    
    @xlrp.ModelName("模块2")
    @xlrp.StepName("用例2")
    def xl_pr2():
        print(456)

# 需要注意的是，这里传入的是类的实例对象
runner = Runner().run_class(ExcelData())
```

## 类方法参数化
> 我们已经知道在run的方法中，是可以传入函数名和参数来进行参数化设置的，但是对于类来说，则不能这么进行处理，所以，xlrp自带了参数化的装饰器，为了方便记忆，则延用大家熟悉的ddt，但为了区分，这里为xl_ddt，虽然名字相同，但是他们的内部逻辑是有区别的

```python=
@SysName("测试模块")
@xl_ddt
class ExcelTest:
    @ModelName('模块1')
    @xl_data([(1, 2, '步骤1'), (2, 3, '步骤2'), (5, 5, '步骤3')])
    def xl_pr(self, a, b, step):
        with StepName(step):
            assert a == b

    @xl_data([(1, 2, '步骤1'), (2, 3, '步骤2'), (5, 5, '步骤3')])
    @ModelName('模块2')
    def xl_pr2(self, a, b, step):
        with StepName(step):
            assert a > b/a

    @ModelName("模块3")
    @StepName("步骤")
    def xl_pr3(self):
        print(123)

    @ModelName("模块4")
    @StepName("步骤")
    def xl_pr4(self):
        print(666)
```

> 通过上述的例子，我们可以看到，他的使用方法，和常用的ddt区别并不是很大，而我们作为类方式运行，其实xl_ddt的意义并不大，但是为了让run_class的方法更小更易维护，还是选择重新设置一个xl_ddt来捕获当前类

> xl_data和run的参数化相似，也是传入一个列表，列表中每个元素代表一个用例的参数，三个参数会生成三个用例，**注意事项** xlrp在收集参数构造用例的时候，是在原有的方法上，尾部加上了 *"_数字"* 的形式，类中用例的运行顺序，也是依据用例名称来进行的

## 保存图像
> 在我们运行用例之后，我们可以选择将图片存在excel中


```python=
@xlrp.SysName("系统1")
def single(a, b):
    with xlrp.ModelName("模块")：
        with xlrp.StepName("用例"):
            print(a, b)

@xlrp.SysName("测试")
Class ExcelData:
    @xlrp.ModelName("模块1")
    @xlrp.StepName("用例1")
    def xl_pr():
        print(123)
    
    @xlrp.ModelName("模块2")
    @xlrp.StepName("用例2")
    def xl_pr2():
        print(456)

# plot_save_excel有两个参数：
# file_path: 需要保存进入的excel文件
# width_list: 图片的大小，默认是(700, 700, 700)
# width_list 的图像大小，默认第三个参数，会在原基础上X2，为保证图像美观，请保持三个数字一致
runner = Runner()
runner.run(single).plot_save_excel('./test.xlsx')
runner.run_class(ExcelData()).plot_save_excel('./test.xlsx')
```

## 默认保存(生成报告)
> 默认生成，会生成一个.xlrp_cache文件夹以及log、plot、report三个子文件夹，存放在当前调用文件同级目录下，excel文件包含两个sheet页面，一个是使用xlrp运行的所有用例以及他们的运行结果，第二个sheet为统计图标，一个饼图、一个柱状图、一个折线图，分别代表，系统用例运行总通过率、系统模块用例通过率、系统模块及模块用例运行耗时


```python=
runner = Runner()
runner.run(single).save_default()
runner.run_class(ExcelTest()).save_default()
```
![](http://39.98.138.157:9900/upload_0460a995f94011a171c1cfa7c5087e91.png)
![](http://39.98.138.157:9900/upload_58c83feb1177b1696be4796996106d9f.png)
![](http://39.98.138.157:9900/upload_d5a4042e2a3897fb1b27172b8a1982a7.png)

## 多进程运行
> 在多进程运行的时候，为了使文件能正常保存，不至于覆盖，在Runner运行类中，增加了file_mark参数，此参数为设置文件的命名规则，自定义的方式能让自己更好理解文件的位置等信息，相比其他ID类的不明意义的标识更有辨识性

使用进程池的方式添加多个进程运行用例：

```python=
from XLRP.xlrp import *
from multiprocessing import Process, Pool


@SysName("测试模块")
@xl_ddt
class ExcelTest:
    @ModelName('模块1')
    @xl_data([(1, 2, '步骤1'), (2, 3, '步骤2'), (5, 5, '步骤3')])
    def xl_pr(self, a, b, step):
        with StepName(step):
            assert a == b

    @xl_data([(1, 2, '步骤1'), (2, 3, '步骤2'), (5, 5, '步骤3')])
    @ModelName('模块2')
    def xl_pr2(self, a, b, step):
        with StepName(step):
            assert a > b/a

    @ModelName("模块3")
    @StepName("步骤")
    def xl_pr3(self):
        print(1/ 0)

    @ModelName("模块4")
    @StepName("步骤")
    def xl_pr4(self):
        print(666)

    @ModelName("模块5")
    @StepName("步骤")
    def xl_pr5(self):
        return False

def run(mark):
    runner = Runner(file_mark=mark)
    runner.run_class(ExcelTest()).save_default()
    

if __name__ == '__main__':
    file_names = ['测试1', '测试2', '测试3', '测试4']
    pool = Pool(4)
    for task in file_names:
        pool.apply_async(run, (task, ))
    pool.close()
    pool.join()
```

