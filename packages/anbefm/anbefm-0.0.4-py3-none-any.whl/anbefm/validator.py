from typing import Any, List, Dict, Tuple, Callable

class LengthValidator():
    def __init__(self, min_length = 6, max_length = 100, error_message: str = '') -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.error_message = error_message

    def __call__(self, key_name: str, data: str) -> str:
        if len(data) < self.min_length or len(data) > self.max_length:
            return self.error_message or f'{key_name}长度不符合'


class ValidatorField():
    '''
    校验字段
    ValidatorField(
        required: '用户名必填',
        ftype: str,
        custom_validators: [
            LengthValidator(error_message='用户名长度在6~12个字符！')
        ]
    )
    '''
    def __init__(self, required: str = '', ftype: Any = None, custom_validators: List[Callable] = []) -> None:
        self.required = required
        self.ftype = ftype
        self.custom_validators = custom_validators

    def __call__(self, key_name: str, data: Dict) -> List[str]:
        errs = []
        exist = key_name in data

        # 必填校验
        if self.required and not exist:
            errs.append(self.required)

        # 自定义校验
        if exist:
            for v in self.custom_validators:
                errmsg = v(key_name, data[key_name])
                errmsg and errs.append(errmsg)

        return errs


class Validator():
    '''
    校验器
    Validator({
        user_name: ValidatorField()
    })
    '''
    def __init__(self, fields: Dict[str, ValidatorField]) -> None:
        self.fields = fields

    def valide(self, data: Dict) -> List[str]:
        if type(data) != dict:
            return ['类型错误']

        errs = []

        for v in self.fields:
            if v in data:
                vf = self.fields[v]
                errs.extend(vf(v, data))

        return errs
