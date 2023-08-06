# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['net_inspect', 'net_inspect.plugins']

package_data = \
{'': ['*']}

install_requires = \
['ntc_templates_elinpf>=3.1.0,<4.0.0',
 'python-Levenshtein-wheels>=0.13.2,<0.14.0',
 'rich>=12.4.1,<13.0.0',
 'textfsm>=1.1.2,<2.0.0']

setup_kwargs = {
    'name': 'net-inspect',
    'version': '0.2.0',
    'description': '基于已收集的网络设备信息进行的结构化数据分析框架',
    'long_description': "# net_inspect 介绍\n\n`net_inspect`是网络设备数据结构化分析框架\n\n\n## 安装方法\n\n### PyPI\n\n```bash\npip install net_inspect\n```\n\n### Poetry\n\n```bash\ngit clone https://github.com/Elinpf/net_inspect\ncd net_inspect\npoetry install\n```\n\n## 插件介绍\n\n`net_inspect`采用了插件模块的框架，分别是`Input`, `Parse`, `Analysis`, `Output` 模块。\n\n通过编写模块插件，实现快速定制的能力。\n\n### InputPlugin\n\nInput插件的功能是将**已经获得的设备检查命令的日志**转化为命令与命令输出的对应关系。如果是通过直接对设备进行操作获取的日志，可以使用`console`这个插件进行处理。如果是用的第三方平台进行的自动化收集，那么就需要自行编写Input插件实现命令与输出的对应。\n\n### ParsePlugin\n\nParse插件的功能是将每条命令的输出进行解析并且结构化。提取出关键信息并以`List[dict]`的方式进行存储。\n\n现有的`Parse`解析模块使用的是[ntc-templates-elinpf](https://github.com/Elinpf/ntc-templates)这个库，是`ntc-templates`库的分支，由于主仓更新频率很慢且不会增加国内常用的设备厂家，所以我Fork后进行了修改。\n\n\n### AnalysisPlugin\n\nAnalysis插件的功能是将解析的信息进行分析，对分析的内容进行告警分级。例如电源是否异常。这个工作是在分析模块中进行的。\n\n### OutputPlugin\n\n输出模块可能是最需要自定义编写的地方。将解析和分析的结果按照自己想要的格式展现出来。\n\n## 使用方法\n\n`net_inspect`有三种使用方式\n\n1. 作为三方库提供API\n2. CLI命令行操作 (TODO)\n3. 本地Web界面操作 (TODO)\n\n\n### 使用库\n\n示例:\n\n```python\nfrom net_inspect import NetInspect, OutputPluginAbstract, PluginError\nfrom rich.table import Table\nfrom rich.console import Console\n\n\nclass Output(OutputPluginAbstract):\n    def main(self):\n        if not self.params.output_params.get('company'):\n            raise PluginError('name or age is missing')\n\n        console = Console()\n\n        table = Table(title=self.params.output_params.get(\n            'company'), show_lines=False)\n        table.add_column('name', justify='center')\n        table.add_column('ip', justify='center')\n        table.add_column('model', justify='center')\n        table.add_column('version', justify='center')\n        table.add_column('power', justify='center')\n\n        for device in self.params.devices:\n            if device.vendor.PLATFORM == 'huawei_vrp':\n                data = [device.info.name, device.info.ip]\n                ps = device.parse_result('display version')\n                data.append(ps[0].get('model'))\n                data.append(ps[0].get('vrp_version'))\n                power_analysis = device.analysis_result.get('Power Status')\n                power_desc = []\n                for alarm in power_analysis:\n                    if alarm.is_focus:\n                        power_desc.append(alarm.message)\n                data.append('\\n'.join(power_desc) if power_desc else 'Normal')\n\n                table.add_row(*data)\n                table.row_styles = ['green']\n\n        console.print(table)\n\n\nnet = NetInspect()\n# net.set_log_level('DEBUG')\nnet.set_plugins('smartone', Output)\ncluster = net.run('log_files', 'output',\n                  output_plugin_params={'company': 'Company Name'})\n```",
    'author': 'Elin',
    'author_email': '365433079@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Elinpf/net_inspect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
