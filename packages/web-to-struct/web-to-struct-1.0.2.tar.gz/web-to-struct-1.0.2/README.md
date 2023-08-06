# web-to-struct
A tool for data structuring, mainly for web data.
将数据格式化的小工具，主要处理web数据。

## 安装
`pip install web-to-struct`

## 环境
`>= python3.6`

## 使用
### DEMO
```python
import requests
import json
from web_to_struct import Parser

if __name__ == '__main__':
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    }
    r = requests.get("https://copymanga.org/recommend", headers=headers)

    config = {
        "name": "data",
        "map": [
            {"function": "string-to-element"},
            {"function": "css", "kwargs": {"patterns": ["#comic > .row > .exemptComicItem"]}},
        ],
        "children": [{
            "name": "title",
            "map": [
                {"function": "css", "kwargs": {"patterns": ["p[title]"]}},
            ]
        }, {
            "name": "img",
            "map": [
                {"function": "css", "kwargs": {"patterns": [".exemptComicItem-img > a > img"]}},
                {"function": "attr", "kwargs": {"attr_name": "data-web_to_struct"}},
            ]
        }, {
            "name": "comic_id",
            "map": [
                {"function": "css", "kwargs": {"patterns": [".exemptComicItem-img > a"]}},
                {"function": "attr", "kwargs": {"attr_name": "href"}},
                {"function": "regex", "kwargs": {"pattern": r"comic/(.*?)$"}},
            ]
        }, {
            "name": "author",
            "map": [
                {"function": "css", "kwargs": {"patterns": [".exemptComicItem-txt > span.exemptComicItem-txt-span > a[href^=\"/author\"]"]}},
            ],
        }]
    }
    parser = Parser()
    resp = parser.parse(r.text, config)
    print(json.dumps(resp, ensure_ascii=False, indent=2))
```
returns
```jsonc
{
  "data": [
    {
      "title": "見到你之後該說什麼呢",
      "img": "https://mirror277.mangafuna.xyz:12001/comic/jiandaonizhihougaishuoshenmene/cover/e54e3f14-8425-11eb-869d-00163e0ca5bd.jpg!kb_w_item",
      "comic_id": "jiandaonizhihougaishuoshenmene",
      "author": "ねむようこ"
    } //,...
  ]
}
```

### `Config`参数
```jsonc
{
  "name": "",
  "map": [
    { "function": "", "kwargs": {} } // 内置函数，上一个的输出作为下一个的输入
  ],
  "children": [{}] // optional 子节点，结构同本结构。
}
```

### 内置函数 Functions
| Function 函数名 | Accepted Returns 可接受的上一个函数的返回类型 | Extra Args 额外的参数 | Returns 返回类型 | Description 描述 |
| --- | --- | --- | --- | --- |
| string-to-element | `Union[str, bytes]` | `feature: str = "html5lib"` | Element | - |
| css | Element | `patterns: Union[str, List[str]]` | [Element, None] | - |
| index | `Union[Dict, Tuple, List]` | `pattern: str  # eg."[1].x"` | Any | - |
| text | Element | - | String | get pure strings inside the current elements |
| html | Element | - | String | get HTML strings inside the current element |
| attr | Element | `attr_name: str` | str | get attribute value of the current element |
| regex | str | `pattern: str` | `Union[str, tuple, None]` | regex match result |
| tuple-to-string | `Tuple` | `pattern: str` | String | use $1,$2,... to replace tuple elements, eg. "hello $1, $2" for tuple ("a", "b") returns "hello a, b" |
| json-parse | str | - | `Union[Dict, List]` | parse json string to dict |

### 其他行为
 - 返回值如果是list，且有children，则处理为返回值叉乘children
 
## 参考
 - 部分内置函数参考了[Yealico](https://yealico.wordpress.com/site-rule-wiki/)
