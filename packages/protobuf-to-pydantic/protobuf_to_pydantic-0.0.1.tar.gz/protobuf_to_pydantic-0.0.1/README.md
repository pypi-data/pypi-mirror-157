# protobuf_to_pydantic
Convert Protobuf-generated Python objects to Pydantic.BaseModel objects with parameter checksum

> NOTE: Only support proto3

# 1.installation
```bash
pip install protobuf_to_pydantic
```

# 2.Quick Start
## 2.1gen runtime obj
`protobuf_to_pydantic` can generate the corresponding `pydantic.BaseModel` object at runtime based on the `Message` object.

For example, the `User Message` in the following Protobuf file:
```protobuf
syntax = "proto3";
package user;

enum SexType {
  man = 0;
  women = 1;
}

message UserMessage {
  string uid=1;
  int32 age=2;
  float height=3;
  SexType sex=4;
  bool is_adult=5;
  string user_name=6;
}
```
`protobuf to pydantic` can read the corresponding `Python` object at runtime and convert it to the corresponding `pydantic.Base Model`:
```Python
from typing import Type
from protobuf_to_pydantic import msg_to_pydantic_model
from pydantic import BaseModel

# import protobuf gen python obj
from example.python_example_proto_code.example_proto.demo import demo_pb2


UserModel: Type[BaseModel] = msg_to_pydantic_model(demo_pb2.UserMessage)
print(
    {
        k: v.field_info
        for k, v in UserModel.__fields__.items()
    }
)

# output
# {
#   'uid': FieldInfo(default='', extra={}), 
#   'age': FieldInfo(default=0, extra={}), 
#   'height': FieldInfo(default=0.0, extra={}), 
#   'sex': FieldInfo(default=0, extra={}),
#   'is_adult': FieldInfo(default=False, extra={}), 
#   'user_name': FieldInfo(default='', extra={})
#  }
```
## 2.2.validate
The message generated according to protobuf carries very little information, and there is not enough information to make the generated `pydantic.Base Model` with parameter verification function.

At present, `protobuf to pydantic` obtains other information of Message in three ways, so that the generated `pydantic.Base Model` object has the function of parameter verification.


### 2.2.1.Text Comment
使用者可以在protobuf文件中为每个字段编写符合`protobuf_to_pydantic`要求的注释来为`protobuf_to_pydantic`提供参数校验信息，比如下面这个例子
```protobuf
syntax = "proto3";
package user;

enum SexType {
  man = 0;
  women = 1;
}

// user info
message UserMessage {
  // p2p: {"miss_default": true, "example": "10086"}
  // p2p: {"title": "UID"}
  string uid=1; // p2p: {"description": "user union id"}
  // p2p: {"example": 18, "title": "use age", "ge": 0}
  int32 age=2;
  // p2p: {"ge": 0, "le": 2.5}
  float height=3;
  SexType sex=4;
  bool is_adult=5;
  // p2p: {"description": "user name"}
  // p2p: {"default": "", "min_length": 1, "max_length": "10", "example": "so1n"}
  string user_name=6;
}
```
在这个例子中，每个可以被`protobuf_to_pydantic`使用的注释都是以`p2p:`开头，并在后面跟着一个完整的Json字符串，这个字符串里面的都是对应字段的校验信息。
比如`UserMessage`中的uid附带了如下4个信息：
- miss_default: 表示生成的字段不带有默认值
- example: 表示生成的字段的示例值为10086
- title: 表示字段的名称为UID
- description: 表示字段的文档描述为`user union id`

> Note: 目前只支持单行注释且一个完整的Json数据不能换行。

当拥有这些信息后，`protobuf_to_pydantic`在把Message生成对应的`Pydantic.BaseModel`对象时都会为每个字段带上对应的信息，如下:
```python
from typing import Type
from protobuf_to_pydantic import msg_to_pydantic_model
from pydantic import BaseModel

# import protobuf gen python obj
from example.python_example_proto_code.example_proto.demo import demo_pb2

UserModel: Type[BaseModel] = msg_to_pydantic_model(demo_pb2.UserMessage, parse_msg_desc_method=demo_pb2)
print(
    {
        k: v.field_info
        for k, v in UserModel.__fields__.items()
    }
)
# output
# {
#   'uid': FieldInfo(default=PydanticUndefined, title='UID', description='user union id', extra={'example': '10086'}), 
#   'age': FieldInfo(default=0, title='use age', ge=0, extra={'example': 18}), 
#   'height': FieldInfo(default=0.0, ge=0, le=2, extra={}), 
#   'sex': FieldInfo(default=0, extra={}), 
#   'is_adult': FieldInfo(default=False, extra={}), 
#   'user_name': FieldInfo(default='', description='user name', min_length=1, max_length=10, extra={'example': 'so1n'})
# }

```

### 2.2.1.By pyi file
由于`Python`中负责把protobuf文件专为`Python`代码时并不会把Message的注释带到生成的`Python`代码中，所以在上面的示例通过把Message对象所属的模块传入`parse_msg_desc_method`中，
使得`protobuf_to_pydantic`可以通过读取Message对应的pyi文件的注释来获取Message对象的附加信息。
```python
from typing import Type
from protobuf_to_pydantic import msg_to_pydantic_model
from pydantic import BaseModel

# import protobuf gen python obj
from example.python_example_proto_code.example_proto.demo import demo_pb2

UserModel: Type[BaseModel] = msg_to_pydantic_model(demo_pb2.UserMessage, parse_msg_desc_method=demo_pb2)
print(
    {
        k: v.field_info
        for k, v in UserModel.__fields__.items()
    }
)
# output
# {
#   'uid': FieldInfo(default=PydanticUndefined, title='UID', description='user union id', extra={'example': '10086'}), 
#   'age': FieldInfo(default=0, title='use age', ge=0, extra={'example': 18}), 
#   'height': FieldInfo(default=0.0, ge=0, le=2, extra={}), 
#   'sex': FieldInfo(default=0, extra={}), 
#   'is_adult': FieldInfo(default=False, extra={}), 
#   'user_name': FieldInfo(default='', description='user name', min_length=1, max_length=10, extra={'example': 'so1n'})
# }
```

> 注：该功能需要在通过Protobuf文件生成对应的`Python`代码时有使用[mypy-protobuf](https://github.com/nipunn1313/mypy-protobuf)插件，且指定的pyi文件输出路径与生成的`Python`代码路径时，才能生效

### 2.2.2.By Protobuf file

> NOTE: 需要提前安装lark库

如果生成Message的原始Protobuf文件存在与项目中， 那么可以设置`parse_msg_desc_method`的值为Message生成时指定的根目录路径，
这样`protobuf_to_pydantic`就可以通过Protobuf生成对应`Python`对象时指定的路径来获取到Message对象的protobuf文件路径，再通过解析protobuf文件获取到Message的附带信息。

比如`protobuf_to_pydantic`的项目结构如下:
```bash
.protobuf_to_pydantic/
├── example/
│ ├── python_example_proto_code/
│ └── example_proto/
├── protobuf_to_pydantic/
└── / 
```
其中protobuf文件存放在`example/example_proto`文件中，然后在`example`目录下通过如下命令生成protobuf对应的`Python`代码文件:
```bash
python -m grpc_tools.protoc
  --python_out=./python_example_proto_code \
  --grpc_python_out=./python_example_proto_code \
  -I. \
```
那么此时需要填写的路径就是`./protobuf_to_pydantic/example`。
```python
from typing import Type
from protobuf_to_pydantic import msg_to_pydantic_model
from pydantic import BaseModel

# import protobuf gen python obj
from example.python_example_proto_code.example_proto.demo import demo_pb2

UserModel: Type[BaseModel] = msg_to_pydantic_model(
    demo_pb2.UserMessage, parse_msg_desc_method="./protobuf_to_pydantic/example"
)
print(
    {
        k: v.field_info
        for k, v in UserModel.__fields__.items()
    }
)
# output
# {
#   'uid': FieldInfo(default=PydanticUndefined, title='UID', description='user union id', extra={'example': '10086'}), 
#   'age': FieldInfo(default=0, title='use age', ge=0, extra={'example': 18}), 
#   'height': FieldInfo(default=0.0, ge=0, le=2, extra={}), 
#   'sex': FieldInfo(default=0, extra={}), 
#   'is_adult': FieldInfo(default=False, extra={}), 
#   'user_name': FieldInfo(default='', description='user name', min_length=1, max_length=10, extra={'example': 'so1n'})
# }
```

### 2.2.2.Protobuf Field Option(PGV)

### 2.2.3.By PGV
> Note 正在开发中...

这是最推荐的方式，该方式参考了[protoc-gen-validate](https://github.com/envoyproxy/protoc-gen-validate)项目，大多数Protobuf文件API参考了[protoc-gen-validate](https://github.com/envoyproxy/protoc-gen-validate)项目

### 2.2.4.其它参数支持
`protobuf_to_pydantic`除了支持`FieldInfo`的参数外，还支持下面几种参数:
- miss_default：默认情况下，生成对应`pydantic.BaseModel`对象中每个字段的默认值与Message中每个字段的默认值是一样的。不过可以通过设置`miss_default`为`true`来取消默认值的设置，需要注意的是在设置`miss_default`为`true`的情况下，`default`参数将失效。
- enable: 默认情况下， `pydantic.BaseModel`会把Message中的每个字段都进行转换，如果有些字段不想被转换，可以设置`enable`为`false`

> Note `FieldInfo`支持的参数见:https://pydantic-docs.helpmanual.io/usage/types/#constrained-types


## 2.3.gen python code
In addition to generating the corresponding `pydantic.Base Model` object at runtime, `protobuf to pydantic` supports converting the runtime `pydantic.Base Model` object to `Python` code text (only applicable to `protobuf to pydantic` generated `pydantic.Base Model` object),

Among them, `protobuf_to_pydantic.pydantic_model_to_py_code` is used to generate code text, `protobuf_to_pydantic.pydantic_model_to_py_file` is used to generate code files, and the example of `protobuf_to_pydantic.pydantic_model_to_py_file` is as follows:
```Python
from protobuf_to_pydantic import msg_to_pydantic_model, pydantic_model_to_py_file

# import protobuf gen python obj
from example.python_example_proto_code.example_proto.demo import demo_pb2

# gen code: url: https://github.com/so1n/protobuf_to_pydantic/blob/master/example/demo_gen_code.py
pydantic_model_to_py_file(
    "./demo_gen_code.py",
    msg_to_pydantic_model(demo_pb2.NestedMessage),
)

# gen code: url: https://github.com/so1n/protobuf_to_pydantic/blob/master/example/demo_gen_code_by_pyi.py 
pydantic_model_to_py_file(
    "./demo_gen_code_by_pyi.py",
    msg_to_pydantic_model(demo_pb2.NestedMessage, parse_msg_desc_method=demo_pb2),
)

# gen code: url: https://github.com/so1n/protobuf_to_pydantic/blob/master/example/demo_gen_code_by_protobuf_field.py
pydantic_model_to_py_file(
    "./demo_gen_code_by_protobuf_field.py",
    msg_to_pydantic_model(
        demo_pb2.NestedMessage, parse_msg_desc_method="/home/so1n/github/protobuf_to_pydantic/example"
    ),
)
```
The specific generated code can be viewed through the corresponding url. It should be noted that if `proto buf to pydantic` checks that the current environment is installed with `isort` and `autoflake`, it will format the code through them by default.
