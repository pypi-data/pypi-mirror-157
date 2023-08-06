导入 ast
导入 posixpath
导入 os
从 汉化通用 导入 _反向注入

导入 flask
导入 jinja2
from jinja2 import Environment as BaseEnvironment
从 jinja2.runtime 导入 LoopContext
从 jinja2.utils 导入 Cycler

# 利用猴子补丁汉化模板过滤器、判断器等
类 〇循环器(Cycler):
    套路 重置(分身):
        分身.reset()
    
    套路 下一个(分身):
        返回 分身.next()

    @property
    套路 当前(分身):
        返回 分身.current
    
    @property
    套路 项々(分身):
        返回 分身.items
    
    @property
    套路 位置(分身):
        返回 分身.pos

_反向注入(〇循环器, Cycler)

套路 生成乱数假文(n=5, html=真, 最少=20, 最多=100):
    """为模板生成一些乱数假文"""
    返回 jinja2.utils.generate_lorem_ipsum(n=n, html=html, min=最少, max=最多)

套路 __初始化模板环境(self, app, **options):
    if "loader" not in options:
        options["loader"] = app.create_global_jinja_loader()
    BaseEnvironment.__init__(self, **options)
    self.app = app
    self.filters = jinja2.filters.FILTERS = {
        "abs": abs,
        "绝对值": abs,
        "attr": jinja2.filters.do_attr,
        "属性": jinja2.filters.do_attr,
        "batch": jinja2.filters.do_batch,
        "分批": jinja2.filters.do_batch,
        "capitalize": jinja2.filters.do_capitalize,
        "首字母大写": jinja2.filters.do_capitalize,
        "center": jinja2.filters.do_center,
        "居中": jinja2.filters.do_center,
        "count": len,
        "计数": len,
        "d": jinja2.filters.do_default,
        "default": jinja2.filters.do_default,
        "默认值": jinja2.filters.do_default,
        "dictsort": jinja2.filters.do_dictsort,
        "字典排序": jinja2.filters.do_dictsort,
        "e": jinja2.filters.escape,
        "escape": jinja2.filters.escape,
        "转义": jinja2.filters.escape,
        "filesizeformat": jinja2.filters.do_filesizeformat,
        "文件大小格式化": jinja2.filters.do_filesizeformat,
        "first": jinja2.filters.do_first,
        "第一个": jinja2.filters.do_first,
        "float": jinja2.filters.do_float,
        "浮点型": jinja2.filters.do_float,
        "forceescape": jinja2.filters.do_forceescape,
        "强制转义": jinja2.filters.do_forceescape,
        "format": jinja2.filters.do_format,
        "格式化": jinja2.filters.do_format,
        "groupby": jinja2.filters.do_groupby,
        "分组": jinja2.filters.do_groupby,
        "indent": jinja2.filters.do_indent,
        "缩进": jinja2.filters.do_indent,
        "int": jinja2.filters.do_int,
        "整型": jinja2.filters.do_int,
        "join": jinja2.filters.do_join,
        "连接": jinja2.filters.do_join,
        "last": jinja2.filters.do_last,
        "最后一个": jinja2.filters.do_last,
        "length": len,
        "长度": len,
        "list": jinja2.filters.do_list,
        "列表型": jinja2.filters.do_list,
        "lower": jinja2.filters.do_lower,
        "小写": jinja2.filters.do_lower,
        "items": jinja2.filters.do_items,
        "项々": jinja2.filters.do_items,
        "map": jinja2.filters.do_map,
        "映射": jinja2.filters.do_map,
        "min": jinja2.filters.do_min,
        "最小值": jinja2.filters.do_min,
        "max": jinja2.filters.do_max,
        "最大值": jinja2.filters.do_max,
        "pprint": jinja2.filters.do_pprint,
        "美化打印": jinja2.filters.do_pprint,
        "random": jinja2.filters.do_random,
        "随机": jinja2.filters.do_random,
        "reject": jinja2.filters.do_reject,
        "拒收": jinja2.filters.do_reject,
        "rejectattr": jinja2.filters.do_rejectattr,
        "拒收属性": jinja2.filters.do_rejectattr,
        "replace": jinja2.filters.do_replace,
        "替换": jinja2.filters.do_replace,
        "reverse": jinja2.filters.do_reverse,
        "反转": jinja2.filters.do_reverse,
        "round": jinja2.filters.do_round,
        "舍入": jinja2.filters.do_round,
        "safe": jinja2.filters.do_mark_safe,
        "安全": jinja2.filters.do_mark_safe,
        "select": jinja2.filters.do_select,
        "选择": jinja2.filters.do_select,
        "selectattr": jinja2.filters.do_selectattr,
        "选择属性": jinja2.filters.do_selectattr,
        "slice": jinja2.filters.do_slice,
        "切片": jinja2.filters.do_slice,
        "sort": jinja2.filters.do_sort,
        "排序": jinja2.filters.do_sort,
        "string": jinja2.filters.soft_str,
        "字符串": jinja2.filters.soft_str,
        "striptags": jinja2.filters.do_striptags,
        "去除标签": jinja2.filters.do_striptags,
        "sum": jinja2.filters.do_sum,
        "和": jinja2.filters.do_sum,
        "title": jinja2.filters.do_title,
        "标题": jinja2.filters.do_title,
        "trim": jinja2.filters.do_trim,
        "修剪": jinja2.filters.do_trim,
        "truncate": jinja2.filters.do_truncate,
        "截断": jinja2.filters.do_truncate,
        "unique": jinja2.filters.do_unique,
        "去重": jinja2.filters.do_unique,
        "upper": jinja2.filters.do_upper,
        "大写": jinja2.filters.do_upper,
        "urlencode": jinja2.filters.do_urlencode,
        "url编码": jinja2.filters.do_urlencode,
        "urlize": jinja2.filters.do_urlize,
        "url化": jinja2.filters.do_urlize,
        "wordcount": jinja2.filters.do_wordcount,
        "字数": jinja2.filters.do_wordcount,
        "wordwrap": jinja2.filters.do_wordwrap,
        "自动换行": jinja2.filters.do_wordwrap,
        "xmlattr": jinja2.filters.do_xmlattr,
        "xml属性": jinja2.filters.do_xmlattr,
        "tojson": jinja2.filters.do_tojson,
        "转json": jinja2.filters.do_tojson,
    }
    self.tests = jinja2.tests.TESTS = { # 判断，如果 x 是 y
        "odd": jinja2.tests.test_odd,
        "奇数": jinja2.tests.test_odd,
        "even": jinja2.tests.test_even,
        "偶数": jinja2.tests.test_even,
        "divisibleby": jinja2.tests.test_divisibleby,
        "可整除": jinja2.tests.test_divisibleby,
        "defined": jinja2.tests.test_defined,
        "已定义": jinja2.tests.test_defined,
        "undefined": jinja2.tests.test_undefined,
        "未定义": jinja2.tests.test_undefined,
        "filter": jinja2.tests.test_filter,
        "过滤器": jinja2.tests.test_filter,
        "test": jinja2.tests.test_test,
        "判断器": jinja2.tests.test_test,
        "none": jinja2.tests.test_none,
        "空": jinja2.tests.test_none,
        "boolean": jinja2.tests.test_boolean,
        "布尔值": jinja2.tests.test_boolean,
        "false": jinja2.tests.test_false,
        "假": jinja2.tests.test_false,
        "true": jinja2.tests.test_true,
        "真": jinja2.tests.test_true,
        "integer": jinja2.tests.test_integer,
        "整数": jinja2.tests.test_integer,
        "float": jinja2.tests.test_float,
        "浮点数": jinja2.tests.test_float,
        "lower": jinja2.tests.test_lower,
        "小写": jinja2.tests.test_lower,
        "upper": jinja2.tests.test_upper,
        "大写": jinja2.tests.test_upper,
        "string": jinja2.tests.test_string,
        "字符串": jinja2.tests.test_string,
        "mapping": jinja2.tests.test_mapping,
        "映射": jinja2.tests.test_mapping,
        "number": jinja2.tests.test_number,
        "数字": jinja2.tests.test_number,
        "sequence": jinja2.tests.test_sequence,
        "序列": jinja2.tests.test_sequence,
        "iterable": jinja2.tests.test_iterable,
        "可迭代对象": jinja2.tests.test_iterable,
        "callable": callable,
        "可调用对象": callable,
        "sameas": jinja2.tests.test_sameas,
        "等同": jinja2.tests.test_sameas,
        "escaped": jinja2.tests.test_escaped,
        "已转义": jinja2.tests.test_escaped,
        "in": jinja2.tests.test_in,
        "在": jinja2.tests.test_in,
        "==": jinja2.tests.operator.eq,
        "eq": jinja2.tests.operator.eq,
        "等于": jinja2.tests.operator.eq,
        "equalto": jinja2.tests.operator.eq,
        "!=": jinja2.tests.operator.ne,
        "ne": jinja2.tests.operator.ne,
        "不等于": jinja2.tests.operator.ne,
        ">": jinja2.tests.operator.gt,
        "gt": jinja2.tests.operator.gt,
        "大于": jinja2.tests.operator.gt,
        "greaterthan": jinja2.tests.operator.gt,
        "ge": jinja2.tests.operator.ge,
        "大于等于": jinja2.tests.operator.ge,
        ">=": jinja2.tests.operator.ge,
        "<": jinja2.tests.operator.lt,
        "lt": jinja2.tests.operator.lt,
        "小于": jinja2.tests.operator.lt,
        "lessthan": jinja2.tests.operator.lt,
        "<=": jinja2.tests.operator.le,
        "le": jinja2.tests.operator.le,
        "小于等于": jinja2.tests.operator.le,
    }
    self.globals = jinja2.defaults.DEFAULT_NAMESPACE = {
        "range": range,
        "范围": range,
        "dict": dict,
        "字典型": dict,
        "lipsum": jinja2.utils.generate_lorem_ipsum,
        "乱数假文": 生成乱数假文,
        "cycler": jinja2.utils.Cycler,
        "循环器": jinja2.utils.Cycler,
        "joiner": jinja2.utils.Joiner,
        "连接符": jinja2.utils.Joiner,
        "namespace": jinja2.utils.Namespace,
        "名称空间": jinja2.utils.Namespace,
    }

flask.templating.Environment.__init__ = __初始化模板环境


# 利用猴子补丁使 jinja2 支持中文关键词  TODO __init__ 中有 raw 正则需要中文化

__模板关键词中英字典 = {
    '如果' : 'if',
    '或如' : 'elif',
    '否则' : 'else',
    '结束如果' : 'endif',
    '取' : 'for',
    '于' : 'in',
    '结束取循环' : 'endfor',
    '另' : 'else',
    '循环' : 'loop',
    '团块' : 'block',
    '结束团块' : 'endblock',
    '继承' : 'extends',
    '包括' : 'include',
    '宏' : 'macro',
    '结束宏' : 'endmacro',
    '从' : 'from',
    '导入' : 'import',
    '为' : 'as',
    '设' : 'set',
    '作用域' : 'with',
    '结束作用域' : 'endwith',
    '非' : 'not',
    '且' : 'and',
    '或' : 'or',
    '是' : 'is',
    '调用' : 'call',
    '结束调用' : 'endcall',
    '过滤器' : 'filter',
    '结束过滤器' : 'endfilter',
    '真' : 'true',  # 这三个属于 tests？
    '假' : 'false',
    '空' : 'none',
    '属性名' : 'attribute', # 过滤器 join 的参数
    '使用上下文' : 'with context',
    '不用上下文' : 'without context',
    '父级' : 'super',
    '自身' : 'self',
    '自动转义' : 'autoescape',
    '结束自动转义' : 'endautoescape',
    '生肉' : 'raw',
    '结束生肉' : 'endraw',
}

套路 __jinja_Lexer_wrap(self, stream, name, filename):
    """This is called with the stream as returned by `tokenize` and wraps
    every token in a :class:`Token` and converts the value.
    """
    for lineno, token, value_str in stream:
        if token in jinja2.lexer.ignored_tokens:
            continue

        value: t.Any = value_str

        if token == jinja2.lexer.TOKEN_LINESTATEMENT_BEGIN:
            token = jinja2.lexer.TOKEN_BLOCK_BEGIN
        elif token == jinja2.lexer.TOKEN_LINESTATEMENT_END:
            token = jinja2.lexer.TOKEN_BLOCK_END
        # we are not interested in those tokens in the parser
        elif token in (jinja2.lexer.TOKEN_RAW_BEGIN, jinja2.lexer.TOKEN_RAW_END):
            continue
        elif token == jinja2.lexer.TOKEN_DATA:
            value = self._normalize_newlines(value_str)
        elif token == "keyword":
            token = value_str
        elif token == jinja2.lexer.TOKEN_NAME:
            value = value_str
            if value_str in __模板关键词中英字典:
                value = __模板关键词中英字典[value_str]
            if not value.isidentifier():
                raise jinja2.exceptions.TemplateSyntaxError(
                    "标识符中有无效字符", lineno, name, filename
                )
        elif token == jinja2.lexer.TOKEN_STRING:
            # try to unescape string
            try:
                value = (
                    self._normalize_newlines(value_str[1:-1])
                    .encode("ascii", "backslashreplace")
                    .decode("unicode-escape")
                )
            except Exception as e:
                msg = str(e).split(":")[-1].strip()
                raise jinja2.exceptions.TemplateSyntaxError(msg, lineno, name, filename) from e
        elif token == jinja2.lexer.TOKEN_INTEGER:
            value = int(value_str.replace("_", ""), 0)
        elif token == jinja2.lexer.TOKEN_FLOAT:
            # remove all "_" first to support more Python versions
            value = ast.literal_eval(value_str.replace("_", ""))
        elif token == jinja2.lexer.TOKEN_OPERATOR:
            token = jinja2.lexer.operators[value_str]

        yield jinja2.lexer.Token(lineno, token, value)

jinja2.lexer.Lexer.wrap = __jinja_Lexer_wrap


# 模板中 loop 的属性和方法的汉化

类 〇循环上下文(LoopContext):

    @属性
    套路 长度(分身):
        返回 分身.length
    
    @属性
    套路 深度(分身):
        返回 分身.depth

    @属性
    套路 索引(分身):
        返回 分身.index

    @属性
    套路 索引0(分身):
        返回 分身.index0
    
    @属性
    套路 反向索引(分身):
        返回 分身.revindex

    @属性
    套路 反向索引0(分身):
        返回 分身.revindex0
    
    @属性
    套路 是首次(分身):
        返回 分身.first
    
    @属性
    套路 是末次(分身):
        返回 分身.first
    
    @属性
    套路 上一元素(分身):
        返回 分身.previtem
    
    @属性
    套路 下一元素(分身):
        返回 分身.nextitem
    
    套路 取对应值(分身, *参数々):
        返回 分身.cycle(*参数々)
    
    套路 已改变(分身, *值々):
        返回 分身.changed(*值々)

_反向注入(〇循环上下文, LoopContext)