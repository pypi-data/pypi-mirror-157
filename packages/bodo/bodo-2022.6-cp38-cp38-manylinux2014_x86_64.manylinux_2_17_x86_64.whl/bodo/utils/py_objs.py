from numba.core import cgutils, types
from numba.extending import NativeValue, box, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    pauo__syq = f'class {class_name}(types.Opaque):\n'
    pauo__syq += f'    def __init__(self):\n'
    pauo__syq += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    pauo__syq += f'    def __reduce__(self):\n'
    pauo__syq += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    krqhj__kgjw = {}
    exec(pauo__syq, {'types': types, 'models': models}, krqhj__kgjw)
    yvyyg__cxym = krqhj__kgjw[class_name]
    setattr(module, class_name, yvyyg__cxym)
    class_instance = yvyyg__cxym()
    setattr(types, types_name, class_instance)
    pauo__syq = f'class {model_name}(models.StructModel):\n'
    pauo__syq += f'    def __init__(self, dmm, fe_type):\n'
    pauo__syq += f'        members = [\n'
    pauo__syq += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    pauo__syq += f"            ('pyobj', types.pyobject),\n"
    pauo__syq += f'        ]\n'
    pauo__syq += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(pauo__syq, {'types': types, 'models': models, types_name:
        class_instance}, krqhj__kgjw)
    wiajd__qqh = krqhj__kgjw[model_name]
    setattr(module, model_name, wiajd__qqh)
    register_model(yvyyg__cxym)(wiajd__qqh)
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(yvyyg__cxym)(unbox_py_obj)
    box(yvyyg__cxym)(box_py_obj)
    return yvyyg__cxym


def box_py_obj(typ, val, c):
    juam__pjmxw = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = juam__pjmxw.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    juam__pjmxw = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    juam__pjmxw.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    juam__pjmxw.pyobj = obj
    return NativeValue(juam__pjmxw._getvalue())
