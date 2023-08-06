from functools import wraps


FUNC_NAME = []
FUNC_PARAM = []
USE_FUNC = []
def xl_ddt(cls):
    @wraps(cls)
    def wrapper(*args, **kwargs):
        cls_instance = cls(*args, **kwargs)
        func_index = 1
        for func, params in zip(FUNC_NAME, FUNC_PARAM):
            if hasattr(cls_instance, func.__name__) is True:
                for param in params:
                    setattr(cls_instance, f'{func.__name__}_{func_index}', eval(f'cls_instance.{func.__name__}'))
                    USE_FUNC.append({f'{func.__name__}_{func_index}': param})
                    func_index += 1
        return cls_instance
    return wrapper

def xl_data(param_list):
    FUNC_PARAM.append(param_list)

    def wrapper(func):
        FUNC_NAME.append(func)

        @wraps(func)
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)
        return decorator
    return wrapper
