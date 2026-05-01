import importlib
import pkgutil

# 自动扫描 tools 文件夹下所有模块，注册工具
definitions = []
executors = {}
labels = {}

for module_info in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f".{module_info.name}", package=__name__)
    if hasattr(module, "definition") and hasattr(module, "execute"):
        name = module.definition["function"]["name"]
        definitions.append(module.definition)
        executors[name] = module.execute
        if hasattr(module, "label"):
            labels[name] = module.label
