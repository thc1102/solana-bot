from typing import Dict


async def model_to_dict(model_obj) -> Dict:
    """
    将模型对象转换为字典
    """
    model_dict = model_obj.__dict__
    # 删除模型对象中的'_state'键，因为它不是有效的模型字段
    model_dict.pop('_state', None)
    return model_dict


async def dict_to_model(model_class, data_dict: Dict):
    """
    将字典转换为模型对象
    """
    # 创建模型对象并使用传入的字典数据进行初始化
    model_obj = model_class(**data_dict)
    return model_obj
