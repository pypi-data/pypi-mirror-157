import matplotlib.pyplot as plt
import numpy as np
from functools import reduce
from pathlib import Path
import json
import math
import random
from typing import *


def random_color() -> list:
    """
    随机生成十六进制颜色值
    :return:
    """
    color = ['#' + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])]
    return color

class DrawPlot(object):
    def __init__(self, sys_name, file_mark, save_path=None):
        self.sys_name = sys_name
        self.sava_path = save_path
        # self.red = '#e60000'
        # self.green = '#2eb82e'
        # self.blue = '#1a52ff'
        self.red = '#fd5a3e'
        self.green = '#97cc64'
        self.blue = '#ffd050'
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 替换全局sans-serif字体(黑体)
        plt.rcParams['axes.unicode_minus'] = False  # 解决坐标轴负号显示问题
        self.file_mark = file_mark

    def draw_pie(self, title=None, color: list = None, show_plot: bool = False, **kwargs) -> str:
        """
        绘制饼图的方法，传入任意键值对参数，值都为int类型，如 成功=10 或者 success=10
        :param title: 图像标题，不填写为默认值
        :param color: 颜色列表，对应后面的数据，不填写默认绿色、红色、蓝色轮换
        :param show_plot: 是否立即显示图像，默认False
        :param kwargs: 键值对，值为int类型
        :return: 如果设置保存地址则返回图片路径，否则返回None
        """
        if color is None:
            color = [self.green, self.red, self.blue]
        # pie_label = list(kwargs.keys())
        # pie_val = list(kwargs.values())
        pie_data = [x for x in list(kwargs.items()) if x[1] > 0]
        pie_label = [x[0] for x in pie_data]
        pie_val = [x[1] for x in pie_data]
        plt.pie(pie_val, labels=pie_label, colors=color, autopct='%.0f%%', textprops={"fontsize": 12})
        plt.axis("equal")
        if title is None:
            title = f"{self.sys_name}总用例通过率{self.file_mark}"
        plt.title(title)
        pic_path = None
        if self.sava_path is not None:
            pic_path = self.sava_path + '/' + title + '.png'
            plt.savefig(pic_path)
        if show_plot is not False:
            plt.show()
        plt.close()
        return pic_path

    def draw_bar(self, title=None, color: list = None, show_plot: bool = False, labels: list = None, **kwargs) -> str:
        """
        绘制柱状图的方法
        :param title: 图像的title名称，填写则保存图片也以此为准
        :param color: 颜色，列表形式，如果颜色数量与小柱状的数量不对应，则循环获取颜色
        :param show_plot: 布尔值，是否立即显示图像，默认False
        :param labels: 列表，当传入数据的是列表形式，则需要填写labels，对应数据的标签
        :param kwargs: 测试数据，键值对方式传入，模块:数据，数据可以是字典或者列表，如果是嵌套列表，需要填写labels参数
        :return: 填写保存路径则返回图片保存路径，否则返回None
        """
        # 数据形式：
        # {"模块1": {"success": 10, "failed": 6, "skip": 8}, "模块2": {"success": 20, "failed": 8, "skip": 6}}
        # {"模块1": [10, 6, 8], "模块2": [20, 8, 6]}, labels=["成功", "失败", "跳过"]
        bar_width = 0.1
        if color is None:
            color = [self.green, self.red, self.blue]
        model_labels = list(kwargs.keys())
        x = np.arange(len(model_labels))
        if type(kwargs[model_labels[0]]) is dict:
            cases = list(kwargs.values())
            labels = [list(x.keys()) for x in list(kwargs.values())][0]
        elif type(kwargs[model_labels[0]]) is list or tuple:
            if labels is None:
                raise ValueError("输入未包含labels，列表形式请传入等量的labels")
            cases = [dict(zip(labels, x)) for x in list(kwargs.values())]
        else:
            raise ValueError("输入类型只能是字典、列表、元组")
        if len(cases) > 1:
            case_count = list(zip(*[list(z.values()) for z in cases]))
        else:
            case_count = list(cases[0].values())
        # print(cases)
        add_width = 0
        color_index = 0
        # print("case_count: ", case_count)
        y_max = np.array(case_count).max()
        # print('y_max: ', y_max)
        plt.ylim(0, y_max + 1)
        for index, item in enumerate(case_count):
            rects = plt.bar(x + bar_width * add_width, item, width=bar_width, color=color[color_index],
                            label=labels[index])
            for rect in rects:
                height = rect.get_height()
                plt.text(rect.get_x() + rect.get_width() / 2, height, str(height), ha="center", va="bottom", size=13)
            add_width += 1
            if color_index == len(color) - 1:
                color_index = 0
            else:
                color_index += 1
        if title is None:
            title = f"{self.sys_name}模块用例通过数{self.file_mark}"
        plt.title(title)
        plt.xticks(x + bar_width * (add_width - 1) / 2, model_labels)
        pic_path = None
        plt.legend(loc='best')
        if self.sava_path is not None:
            pic_path = self.sava_path + "/" + title + ".png"
            plt.savefig(pic_path)
        if show_plot is not False:
            plt.show()
        plt.close()
        return pic_path

    def allure_data(self, result_path) -> Tuple[dict, list, dict]:
        """
        获取allure报告中用例运行数据，allure中应有模块、和用例，即json文件中，需呀有name值代表模块，steps代表各个用例
        :param result_path: 报告数据文件保存文件夹路径
        :return: model_pass_rate 模块通过率字典dict{list[list]}形式，每个小list代表一个用例运行数据，可直接解包成为柱状图的数据
                 status_name 用例的状态类型，可用在柱状图的labels中
                 model_runtime 每个模块的运行时间dict{dict}，内部的字典代表各个用例运行耗时，可直接解包用作折线图的数据
        """
        json_files = Path(result_path).glob('*.json')       # 获取路径下所有的json文件
        cases = []
        pass_rate = []
        run_time_consum = []
        case_titles = []
        for json_path in json_files:                # 获取所有文件，只取第一个key有"name"的值
            with open(json_path, 'r', encoding='utf8') as f:
                data = json.loads(f.read())         # 转换字典形式
                if "name" in list(data.keys()):
                    cases.append(data)
        model_list = [x["name"] for x in cases]         # 获取所有的"name"，即为模块名称
        steps = [x["steps"] for x in cases]             # 获取所有的步骤，列表的形式
        for step in steps:                              # 循环所有步骤
            status = [x["status"] for x in step]        # 获取步骤中的status值，即为用例结果
            pass_rate.append(status)                    # 添加到列表中备用
            run_time = [round((x['stop']-x['start'])/1000, 3) for x in step]        # 获取step的运行时间，保留3位小数
            run_time_consum.append(run_time)            # 在run_time_consum列表中暂存
            case_title = [x['name'] for x in step]      # 获取所有steps的"name"，即为用例的名称
            case_titles.append(case_title)              # 暂存在case_titles中
        dc_list = []
        for stu in pass_rate:                   # 所有的状态，获取其在列表中出现的次数
            dc = {}
            for item in stu:
                dc[item] = dc.get(item, 0) + 1  # 字典获取值，如果没有值，则默认第一个值为0
            dc_list.append(dc)              # 暂存在dc_list列表中
        # 获取所有的状态名称，进行重复过滤
        status_name = list(
            set(reduce(lambda x, y: list(x.keys()) + list(y.keys()) if type(x) is dict else x + list(y.keys()),
                       dc_list)))
        all_status = []
        for dc_item in dc_list:         # 循环所有状态列表，多个数据修改成数量一样的状态
            status_model = []
            for key in status_name:
                status_model.append(dc_item.get(key, 0))
            all_status.append(status_model)
        model_pass_rate = dict(zip(model_list, all_status))     # 模块通过率，组合成字典的形式，作为数据返回
        case_runtime = [dict(zip(*x)) for x in list(zip(case_titles, run_time_consum))]
        model_runtime = dict(zip(model_list, case_runtime))     # 模块运行时间，包含每个用例运行时间
        return model_pass_rate, status_name, model_runtime

    def draw_plot(self, show_plot: bool = False, **kwargs):
        """
        绘制模块和用例耗时的折线图
        :param show_plot: 是否立即显示图像
        :param kwargs: 耗时的数据大致数据形式为- {"模块1": {“用例1”: 2.54, "用例2": 1.2}, "模块2": {"用例1": 3.12}}
        :return: 当设置了save_path，返回保存的文件路径，否则返回None
        """
        # models = list(kwargs.keys())
        models = [x for x in list(kwargs.keys()) if type(kwargs[x]) is dict]
        model_length = len(models)
        case_labels = [list(x.keys()) for x in list(kwargs.values()) if type(x) is dict]
        case_runtime_list = [list(x.values()) for x in list(kwargs.values()) if type(x) is dict]
        enum_case_time = list(zip(case_labels, case_runtime_list))
        fig = plt.figure(figsize=(10, 10))
        grid = plt.GridSpec(math.ceil(model_length/2 + 1), 2, wspace=0.2)       # math进一法取整，设置grid栅栏分布
        # 模块运行总时间折线图
        ax = fig.add_subplot(grid[0, 0:2])
        sum_runtime = [round(np.array(x).sum(), 3) for x in case_runtime_list]        # 同级各个模块用例耗时总和
        y_max = math.ceil(np.array(sum_runtime).max())                                 # 获取最大值
        ax.set_ylim(0, y_max + 1)             # 设置y轴值
        ax.plot(models, sum_runtime, 'o-', color=self.red)                  # 绘制折线图
        for x, y in zip(models, sum_runtime):                               # 折线图折点添加文字
            ax.text(x, y+0.1, y, ha="center", va="bottom", size=12)
        ax.set_title(f"{self.sys_name}系统模块运行耗时")
        ax.set_xlabel("模块")
        ax.set_ylabel("运行时间(s)")
        # 各个模块用例运行时间
        plot_row = 1
        plot_col = 0
        for index, case in enumerate(enum_case_time):
            case_y = math.ceil(np.array(case[1]).max())                            # 获取所有用例的耗时最大值
            ax = fig.add_subplot(grid[plot_row, plot_col])
            ax.set_ylim(0, case_y + 1)
            ax.plot(['\n'.join(c) for c in case[0]], case[1], 'o-', color=self.red)
            for x, y in zip(case[0], case[1]):
                ax.text(x, y+0.1, y, ha="center", va="bottom", size=12)
            ax.set_title(f"{models[index]}-模块用例运行时间")
            ax.set_xlabel("用例")
            ax.set_ylabel("运行时间(s)")
            if plot_col == 1:
                plot_col = 0
                plot_row += 1
            else:
                plot_col += 1
        pic_path = None
        if self.sava_path is not None:
            pic_path = self.sava_path + '/' + f'{self.sys_name}用例耗时{self.file_mark}.png'
            plt.savefig(pic_path)
        if show_plot is not False:
            plt.show()
        plt.close()
        return pic_path