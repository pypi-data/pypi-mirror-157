from numba.core import cgutils, types
from numba.extending import NativeValue, box, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    ihwh__buy = f'class {class_name}(types.Opaque):\n'
    ihwh__buy += f'    def __init__(self):\n'
    ihwh__buy += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    ihwh__buy += f'    def __reduce__(self):\n'
    ihwh__buy += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    lnf__tpgu = {}
    exec(ihwh__buy, {'types': types, 'models': models}, lnf__tpgu)
    dqfp__zqvi = lnf__tpgu[class_name]
    setattr(module, class_name, dqfp__zqvi)
    class_instance = dqfp__zqvi()
    setattr(types, types_name, class_instance)
    ihwh__buy = f'class {model_name}(models.StructModel):\n'
    ihwh__buy += f'    def __init__(self, dmm, fe_type):\n'
    ihwh__buy += f'        members = [\n'
    ihwh__buy += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    ihwh__buy += f"            ('pyobj', types.pyobject),\n"
    ihwh__buy += f'        ]\n'
    ihwh__buy += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(ihwh__buy, {'types': types, 'models': models, types_name:
        class_instance}, lnf__tpgu)
    xzf__vcq = lnf__tpgu[model_name]
    setattr(module, model_name, xzf__vcq)
    register_model(dqfp__zqvi)(xzf__vcq)
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(dqfp__zqvi)(unbox_py_obj)
    box(dqfp__zqvi)(box_py_obj)
    return dqfp__zqvi


def box_py_obj(typ, val, c):
    gomqo__luua = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = gomqo__luua.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    gomqo__luua = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    gomqo__luua.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    gomqo__luua.pyobj = obj
    return NativeValue(gomqo__luua._getvalue())
