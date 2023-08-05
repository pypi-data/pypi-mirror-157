from enum import Enum
from typing import List, Dict, Optional, Tuple, Union, Any, NewType

from .m_dao import MDao

# 数据库类型定义
VARCHAR = NewType('VARCHAR', str)
DATETIME = NewType('DATETIME', str)
INT = NewType('INT', int)
TINYINT = NewType('TINYINT', int)

# 字段查询时方式
class MPredicate(Enum):
    EQUAL = 1
    IN = 2
    LIKE = 3
    REGEXP = 4
    BETWEEN = 5

class MExpression(Enum):
    OR = 1
    AND = 2

class MBaseT():
    ...


class MBaseSelectExprT():
    '''
    TODO: 查询sql中字段(select_expr)部分
    '''
    def get_select_expr(self):
        pass


class MBaseWhereT():
    '''
    查询sql中的where部分
    '''
    field_names = []
    query_fields = {}

    def get_where_params(self, mt):
        '''
        mt: { filedName: value }
        return: [
            [filedName, Predicate, value, Expression],
            ['user_name', LIKE, 'abc', 'or'],
            ['id', =, 'abc', 'and'],
        ]
        '''
        fields = self.query_fields
        params = []

        for field_name in self.field_names:
            if hasattr(mt, field_name) and field_name in fields:
                v = getattr(mt, field_name)
                predicate = fields[field_name]
                exp = MExpression.OR

                if type(predicate) == tuple:
                    exp = predicate[1]
                    predicate = predicate[0]

                params.append((field_name, predicate, v, exp))

        return params

    def parse_where_sql(self, params):
        '''
        params: [
            ['id', =, '123', MExpression.AND],
            ['user_name', LIKE, 'abc', MExpression.OR],
            ['keyword', LIKE, '111', MExpression.OR],
        ]

        return: (id=123) and (user_name like 'abc' or keyword like '111')
        '''
        andlist = []
        orlist = []

        for field_name, predicate, v, exp in params:
            explist = andlist if exp == MExpression.AND else orlist

            if predicate == MPredicate.LIKE:
                explist.append(f'{field_name} like "%{str(v)}%"')

            elif predicate == MPredicate.EQUAL:
                explist.append(f'{field_name} = \'{str(v)}\'')

            elif predicate == MPredicate.IN:
                if type(v) != list:
                    v = [v]

                v = ', '.join([f'\'{str(vitm)}\'' for vitm in v])
                explist.append(f'{field_name} in ({v})')

            elif v == None:
                explist.append(f'{field_name} is null')

        return ' and '.join([
            f"({' and '.join(andlist) if len(andlist) > 0 else '1=1'})", 
            f"({' or '.join(orlist) if len(orlist) > 0 else '1=1'})"]
        )

class MBaseOrderByT():
    '''
    查询sql中的order by部分
    '''
    field_names = []

    def get_order_by_str(self, mt: MBaseT):
        order_params = []
        order_by = getattr(mt, '_order_by', {})

        for field_name in self.field_names:
            order_type = getattr(order_by, field_name, None)

            if order_type in ['asc', 'desc']:
                order_params.append(f'{field_name} {order_type}')

        return ','.join(order_params)


def normallize_insert_value(inst, k, v):
    assert isinstance(inst, MBaseT)

    ann = inst.__annotations__
    typ = ann.get(k)

    if typ == VARCHAR:
        return f'\'{v}\''
    elif typ == DATETIME:
        return 'null' if not v else f'\'{v}\''
    elif typ in [INT, TINYINT]:
        return str(v)
    elif v == None:
        return 'null'

    return f'\'{str(v)}\''


class MBase(MBaseWhereT, MBaseOrderByT):
    db_config = None
    table_name = None
    query_fields = {}
    field_names = []

    def __init__(self):
        self._db = MDao(self.db_config)

    async def list(self, mt: Any, limit=True) -> Optional[List[Any]]:
        params = self.get_where_params(mt)

        if limit and len(params) < 1:
            return []

        order_by_str = self.get_order_by_str(mt)

        sql = f'''
        select * from {self.table_name} where {self.parse_where_sql(params) or ' 1=1'} {(' order by ' + order_by_str) if order_by_str else ''};
        '''

        return await self._db.query(sql)

    async def insert(self, mt: Any):
        return await self.insert_b([mt])

    async def insert_b(self, mts: List[Any]):
        sql = ''

        for mt in mts:
            ks = ', '.join([field_name for field_name in self.field_names if hasattr(mt, field_name)])
            vs = ', '.join([normallize_insert_value(mt, field_name, getattr(mt, field_name)) for field_name in self.field_names if hasattr(mt, field_name)])

            sql += f'''
            insert into {self.table_name} ({ks}) values ({vs});
            '''

        return await self._db.dml(sql)

    async def update(self, mt: Any, where_mt: Any):
        return await self.update_b([(mt, where_mt)])

    async def update_b(self, args: List[Tuple[Any, Any]]): # mt: Any, where_mt: Any
        sql = ''

        for mt, where_mt in args:
            ks = ', '.join([f'{field_name} = {normallize_insert_value(mt, field_name, getattr(mt, field_name))}' for field_name in self.field_names if hasattr(mt, field_name)])

            params = self.get_where_params(where_mt)

            where_str = '1 = 1'

            if len(params) > 0:
                where_str = self.parse_where_sql(params)

            sql += f'''
            update {self.table_name}
            set {ks}
            where {where_str};
            '''

        return await self._db.dml(sql)

    async def delete(self, mt: Any):
        params = self.get_where_params(mt)

        if len(params) < 1:
            return

        sql = f'''
        delete from {self.table_name} where {self.parse_where_sql(params)};
        '''

        return await self._db.dml(sql)