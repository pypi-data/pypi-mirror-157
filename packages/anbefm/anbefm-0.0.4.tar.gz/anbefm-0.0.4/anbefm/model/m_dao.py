from typing import List, Any
import aiomysql
from pymysql import converters
from pymysql.constants import FIELD_TYPE
from ..base.log import Log


charset='utf8'
conv = {
    **converters.conversions,
    # 使用pymysql提供的escape函数进行时间字段的转换
    **{
    FIELD_TYPE.TIMESTAMP: lambda x: converters.escape_item(converters.convert_mysql_timestamp(x), charset).replace("'", ''),
    FIELD_TYPE.DATETIME: lambda x: converters.escape_item(converters.convert_datetime(x), charset).replace("'", ''),
    FIELD_TYPE.TIME: lambda x: converters.escape_item(converters.convert_timedelta(x), charset).replace("'", ''),
    FIELD_TYPE.DATE: lambda x: converters.escape_item(converters.convert_date(x), charset).replace("'",''),
    FIELD_TYPE.DECIMAL: float,
    FIELD_TYPE.NEWDECIMAL: float,
    }
}

dlog = Log()

class MDao():
    def __init__(self, config:dict):
        self._conn = None
        self._config = config

    async def _ensure_connect(self):
        if self._conn is None:
            self._conn = await aiomysql.connect(conv=conv, **self._config)

    async def query(self, sql:str, params=None) -> List[dict]:
        dlog.print(sql, params)
        res = []
        await self._ensure_connect()
        async with self._conn.cursor(aiomysql.DictCursor) as c:
            await c.execute(sql, args=params)
            res = await c.fetchall()
            await self._conn.commit()

        return res

    async def dml(self, sql:str, params=None, many=False):
        dlog.print(sql, params)
        res = None
        await self._ensure_connect()
        async with self._conn.cursor() as c:
            try:
                if not many:
                    res = await c.execute(sql, args=params)
                else:
                    res = await c.executemany(sql, args=params)

                await self._conn.commit()
            except:
                await self._conn.rollback()
                raise

        dlog.print(res)
        return res

    def __del__(self):
        if self._conn:
            self._conn.close()
