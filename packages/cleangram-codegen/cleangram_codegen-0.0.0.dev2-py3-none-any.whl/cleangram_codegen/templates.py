import abc
from dataclasses import dataclass as dc, field
from textwrap import wrap
from typing import Literal, List, Set

from . import comps, const
from .comps import TELEGRAM_PATH, TELEGRAM_OBJECT
from .enums import PackageType, CategoryType
from .models import Api, Component


@dc
class Template(abc.ABC):
    api: Api

    def __str__(self):
        return ""


@dc
class VersionTemplate(Template):
    def __str__(self):
        return f"""
import importlib.metadata

__version__ = importlib.metadata.version("cleangram")
__bot_api__ = "{self.api.version}"
"""


@dc
class PackageTemplate(Template):
    package: PackageType
    import_section: str = ""
    declaration_section: str = ""
    arguments_section: str = ""
    methods_section: str = ""
    typing_imports: List[str] = field(default_factory=list)
    object_imports: List[Component] = field(default_factory=list)
    type_checking_imports: List[Component] = field(default_factory=list)

    def __call__(
            self,
            var: Literal[
                "import",
                "declaration",
                "arguments",
                "methods"
            ],
            val: str,
            tc: int,
            nl: int = 0
    ):
        section: str = getattr(self, f"{var}_section")
        new_val = section + (tc * '\t') + val + (nl * '\n')
        setattr(self, f"{var}_section", new_val)

    def i(self, val: str = "", tc=0, nl=1):
        self("import", val, tc, nl)

    def d(self, val: str = "", tc=0, nl=1):
        self("declaration", val, tc, nl)

    def a(self, val: str = "", tc=1, nl=1):
        self("arguments", val, tc, nl)

    def m(self, val: str = "", tc=1, nl=1):
        self("methods", val, tc, nl)

    def __str__(self):
        if self.type_checking_imports:
            self.typing_imports.append("TYPE_CHECKING")

        if self.typing_imports:
            for tp in self.typing_imports:
                self.i(f"from typing import {tp}")

        for obj in self.object_imports:
            self.write_import(obj)

        if self.type_checking_imports:
            self.i("if TYPE_CHECKING:")
            for obj in self.type_checking_imports:
                self.write_import(obj, tc=1)

        return "\n".join([
            self.import_section,
            self.declaration_section,
            self.arguments_section,
            self.methods_section
        ]).replace("\t", "    ")

    def __post_init__(self):
        self.is_core = self.package == PackageType.CORE
        self.is_aio = self.package == PackageType.AIO
        self.is_sync = self.package == PackageType.SYNC
        self.await_ = "await " if self.is_aio else ""
        self.async_ = "async " if self.is_aio else ""

    def write_import(self, *objects: Component, tc: int = 0):
        for obj in objects:
            if self.is_core or obj.is_adjusted:
                self.i(f"from .{obj.module} import {obj.camel}", tc=tc)
            else:
                self.i(f"from ...core import {obj.camel}", tc=tc)


@dc
class ComponentTemplate(PackageTemplate, abc.ABC):
    com: Component = None

    def header(self): ...

    @abc.abstractmethod
    def declaration(self): ...

    def description(self):
        self.a('"' * 3)
        for p in self.com.desc:
            for pp in wrap(p.text):
                self.a(pp)
            if self.is_core and self.com.subclasses:
                self.a()
                for sub in self.com.subclasses:
                    self.a(f":class:`cleangram.{sub.camel}`", tc=2)
        self.a()
        self.a(f"Reference: https://core.telegram.org/bots/api{self.com.anchor}")
        self.a('"' * 3)

    def arguments(self):
        if self.is_core:
            if self.com.has_field:
                self.i("from pydantic import Field")
            for arg in self.com.args:
                self.a(f"{arg.field}: {arg.annotation}{arg.field_value}")
                if arg.desc:
                    desc = '\n\t'.join(wrap(arg.desc.text))
                    self.a(f'"""{desc}"""\n')

    @abc.abstractmethod
    def methods(self): ...

    def __post_init__(self):
        super(ComponentTemplate, self).__post_init__()
        self.header()
        self.declaration()
        self.description()
        self.arguments()
        self.methods()
        for lst in [self.type_checking_imports, self.object_imports]:
            if self.com in lst:
                lst.remove(self.com)


@dc
class ObjectTemplate(ComponentTemplate):
    def header(self):
        super(ObjectTemplate, self).header()
        if self.is_core:
            self.i("from __future__ import annotations")

    def declaration(self):
        extends = []
        if self.is_core:
            self.object_imports.append(self.com.parent)
            # self.i(f"from .{self.com.parent.module} import {self.com.parent.camel}")
            extends.append(self.com.parent.camel)
            if self.com.is_adjusted:
                self.i("import abc")
                extends.append("abc.ABC")
        else:
            self.i(f"from ...core import {self.com.camel} as _{self.com.camel}")
            extends.append(f"_{self.com.camel}")
        self.d(f"class {self.com.camel}({','.join(extends)}):", nl=0)

    def arguments(self):
        super(ObjectTemplate, self).arguments()
        if self.is_core:
            self.typing_imports.extend(self.com.args_typing)
            self.type_checking_imports.extend(self.com.args_objects)
            # if self.com.args_objects:
            #     self.i("from typing import TYPE_CHECKING")
            #     self.i("if TYPE_CHECKING:")
            #     for tp in self.com.args_objects:
            #         self.i(f"from .{tp.module} import {tp.camel}", 1)
        elif self.com.is_adjusted:
            self.i("from __future__ import annotations")
            self.typing_imports.extend(self.com.adjusted_typing)
            self.type_checking_imports.extend(self.com.adjusted_objects)
            # self.i("from typing import TYPE_CHECKING")
            # self.i("if TYPE_CHECKING:")
            # for tp in self.com.adjusted_objects:
            #     self.i(f"from .{tp.module} import {tp.camel}", 1)
            if self.com.is_aliased:
                for path in self.api.paths:
                    if path.name in const.ALIASED_OBJECTS[self.com.name]:
                        self.type_checking_imports.extend(path.used_objects)
                        # for c in path.used_objects:
                        #     if c == self.com:
                        #         continue
                        #     if c.is_adjusted:
                        #         self.i(f"from .{c.module} import {c.camel}", 1)
                        #     else:
                        #         self.i(f"from ...core import {c.camel}", 1)
            for arg in self.com.args:
                if any([o.is_adjusted for o in arg.com_types]):
                    self.a(f"{arg}:{arg.annotation}{arg.field_value}")

    def methods(self):
        if self.com.is_aliased:
            self.alias()
        if self.is_core:
            self.adjusts()

            if self.com.name == "Update":
                self.i("from functools import lru_cache")
                self.typing_imports.append("Tuple")
                self.m("def __hash__(self): return hash(self.update_id)")

                self.m("@lru_cache()")
                self.m("def get_event_type(self) -> Tuple[TelegramObject, str]:")
                for e in self.com.args[1:]:
                    self.m(f"\tif self.{e.name}: return self.{e.name}, '{e.name}'")
                self.m("\traise NameError(\"Event Not Found\")")

                self.m("@property")
                self.m("def event(self) -> TelegramObject: return self.event_type[0]")

                self.m("event_type = property(get_event_type)")

    def alias(self):
        if self.com.is_adjusted:
            for path in self.api.paths:
                if aliased_path := const.ALIASED_OBJECTS[self.com.name].get(path.name, None):
                    if not self.is_core:
                        self.typing_imports.extend(path.used_typing)
                    for name, params in aliased_path.items():
                        self.write_answer(path, name, params)

    def write_answer(self, path: Component, name: str, params: dict):
        if self.is_core:
            self.m("@abc.abstractmethod")
        signature = ["self"]
        for a in path.args:
            if a.name not in params.keys():
                signature.append(f"{a}{'' if self.is_core else ':'+a.annotation}{a.method_value}")
        result = '' if self.is_core else f" -> {path.result.annotation}"
        self.m(f"{self.async_}def {name}({','.join(signature)}){result}:")
        if self.is_core:
            self.m("...", 2)
        else:
            declaration = [
                f"{a}=self.{params[a.name]}" if a.name in params.keys() else f"{a}={a}"
                for a in path.args
            ]
            self.m(f"return {self.await_}self.bot.{path.snake}({','.join(declaration)})", 2)

    def adjusts(self):
        if self.com.is_adjusted:
            self.i("from ..bot.bot import Bot")
            self.m("def adjust(self, bot: Bot):")
            if self.com.name == "Update":
                self.m("self.event.adjust(bot)", 2)
                return
            for arg in self.com.args:
                for tp in arg.com_types:
                    if tp.is_adjusted:
                        if arg.array == 2:
                            self.m(f"\tfor i in self.{arg}:")
                            self.m(f"\t\tfor j in i: j.adjust(bot)")
                        elif arg.array:
                            self.m(f"\tfor i in self.{arg}: i.adjust(bot)")
                        elif arg.union:
                            self.m(f"\tif isinstance(self.{arg}, {tp.camel}): self.{arg}.adjust(bot)")
                        elif arg.optional:
                            self.m(f"\tif self.{arg}: self.{arg}.adjust(bot)")
                        else:
                            self.m(f"\tself.{arg}.adjust(bot)")


@dc
class PathTemplate(ComponentTemplate):
    def declaration(self):
        extends = []
        if self.is_core:
            self.i(f"from .{self.com.parent.module} import {self.com.parent.camel}")
            extends.append(self.com.parent.camel)
            if self.com.is_adjusted:
                self.i("import abc")
                extends.append("abc.ABC")
        else:
            self.i(f"from ...core.paths.{self.com.module} import {self.com.camel} as _{self.com.camel}")
            extends.append(f"_{self.com.camel}")
        if (
                (self.is_core and ~self.com.is_adjusted) or
                (~self.is_core and self.com.is_adjusted)
        ):
            self.typing_imports.extend(self.com.result_typing)
            self.i("from ...core.objects.response import Response")
            for tp in self.com.result_objects:
                self.i(f"from ..objects import {tp.camel}")
            extends.append(f"response=Response[{self.com.result.annotation}]")
        self.d(f"class {self.com.camel}({','.join(extends)}):", nl=0)

    def arguments(self):
        super(PathTemplate, self).arguments()
        if self.is_core:
            self.typing_imports.extend(self.com.args_typing)
            for obj in self.com.args_objects:
                self.i(f"from ..objects import {obj.camel}")

    def methods(self):
        if self.is_core:
            if self.com.is_adjusted:
                self.adjust()
            if self.com.is_prepared:
                self.prepare()

    def adjust(self):
        self.typing_imports.extend(self.com.result_typing)
        self.import_objects(self.com.result_objects)
        self.i("from ..bot.bot import Bot")
        self.m(f"def adjust(self, bot: Bot, result: {self.com.result.annotation}):")
        res = self.com.result
        if res.array:
            self.m(f"\tfor r in result: r.adjust(bot)")
        elif res.union:
            self.i("from ..objects import TelegramObject")
            self.m(f"\tif isinstance(result, TelegramObject): result.adjust(bot)")
        else:
            self.m("\tresult.adjust(bot)")

    def prepare(self):
        self.i(f"from ..bot.bot import Bot")
        self.m(f"def prepare(self, bot: Bot):")
        if self.com.name == "sendMediaGroup":
            self.m("for m in self.media:", 2)
            self.m(f"m.parse_mode = bot.config.preset.parse_mode(m.parse_mode)", 3)
            self.m("m.media = self.attach(m.media)", 3)
            self.m("if hasattr(m.media, 'thumb'): m.thumb = self.attach(m.thumb)", 3)
        else:
            for a in self.com.args:
                if self.api.input_file in a.com_types:
                    if "attach://" in a.desc.text:
                        self.m(f"self.{a} = self.attach(self.{a})", 2)
                    else:
                        self.m(f"self.attach(self.{a}, '{a}')", 2)
                elif a.name in const.PRESETS:
                    self.m(f"self.{a} = bot.config.preset.{a}(self.{a})", 2)

    def import_objects(self, objects: Set[Component]):
        for obj in objects:
            self.i(f"from ..objects import {obj.camel}")


@dc
class InitComponentsTemplate(PackageTemplate):
    ct: CategoryType = None

    def __post_init__(self):
        super(InitComponentsTemplate, self).__post_init__()
        coms = []
        if self.ct == CategoryType.OBJECT:
            coms = self.api.objects.copy()
            coms.extend([
                TELEGRAM_OBJECT,
                comps.TELEGRAM_RESPONSE,
                comps.TELEGRAM_T,
                comps.TELEGRAM_REQUEST
            ])
        elif self.ct == CategoryType.PATH:
            coms = self.api.paths.copy()
            coms.append(TELEGRAM_PATH)

        coms.sort(key=str)

        for com in coms:
            if self.is_core or com.is_adjusted:
                self.i(f"from .{com.module} import {com.camel}")
            else:
                self.i(f"from ...core import {com.camel}")

        self.d("__all__ = [")
        for com in coms:
            self.d(f'{com.camel!r},', 1)
        self.d("]")

        if self.ct == CategoryType.OBJECT:
            for o in self.api.objects:
                if imports := (o.used_objects if self.is_core else o.adjusted_objects):
                    refs = ','.join([f"{i}={i}" for i in imports])
                    self.d(f"{o.camel}.update_forward_refs({refs})")


@dc
class BotTemplate(PackageTemplate):
    bot_objects: List[Component] = None

    def __post_init__(self):
        super(BotTemplate, self).__post_init__()
        self.header()
        self.declaration()
        if self.is_core:
            self.core_methods()
        else:
            self.base_methods()
        self.methods()

    def header(self):
        self.i("from typing import List, Union, Optional")
        if self.is_core:
            self.i("from typing import TYPE_CHECKING, Any, Type")
            self.i("from __future__ import annotations")
            self.i("import abc")
            self.i("if TYPE_CHECKING:")
            self.i("from ..http import Http", 1)
            self.i("from ...util import BotConfig", 1)
            self.i("from ..objects import User", 1)
        else:
            self.i(f"from ..paths import ({','.join(map(str, self.api.paths))})")
            self.i(f"from ..objects import ({','.join(map(str, self.bot_objects))})")
            self.i(f"from ..objects import T")
        self.i("from ..paths import TelegramPath", int(self.is_core))

    def declaration(self):
        parent = "BaseBot"
        if self.is_core:
            parent = "abc.ABC"

        else:
            self.d(f"from ...core.bot.base import {parent}")
        self.d(f"class Bot({parent}):", nl=0)
        self.a('"'*3)
        self.a("Client instance for work with Telegram Bot API")
        self.a('"'*3)

        if self.is_core:
            self.i("from ..http import Http")
            self.a("__http__: Type[Http]")
        else:
            self.i(f"from ..http import HttpX")
            self.a(f"__http__ = HttpX")

    def methods(self):
        for h in self.api.headers:
            if h.paths:
                self.m(f"# {h.name}", nl=2)
            for path in h.paths:
                signature = self.get_signature(path)
                result = path.result.annotation
                if self.is_core:
                    result = "Any"
                    self.m(f"@abc.abstractmethod")
                self.m(f"{self.async_}def {path.snake}({signature}) -> {result}:")
                self.method_description(path)
                self.method_declaration(path)

    def core_methods(self):
        for name, tp in {
            "token": "str",
            "config": "BotConfig",
            "me": "User",
            "id": "int",
            "http": "Http",
        }.items():
            self.m("@property")
            self.m("@abc.abstractmethod")
            self.m(f"def {name}(self) -> {tp}: ...")

        signature = ["self", "path: TelegramPath", "http_timeout: Optional[float] = None"]
        self.m("@abc.abstractmethod")
        self.m(f"def __call__({','.join(signature)}): ...")

        self.m("@abc.abstractmethod")
        self.m(f"def update_me(self): ...")

        self.m("@abc.abstractmethod")
        self.m(f"def cleanup(self): ...")

    def base_methods(self):
        self.m(f"{self.async_}def __call__(self, path: TelegramPath, http_timeout: Optional[float] = None) -> T:")
        self.m(f"return {self.await_}self.config.http(self, path, http_timeout)", 2)

        self.m(f"{self.async_}def update_me(self): self._me = {self.await_}self.get_me()")
        a = 'a' if self.is_aio else ''

        self.m(f"{self.async_}def __{a}enter__(self):")
        self.m(f"{self.await_}self.update_me()", 2)
        self.m(f"return self", 2)

        self.m(f"{self.async_}def __{a}exit__(self, exc_type, exc_val, exc_tb):")
        self.m(f"{self.await_}self.http.close()", 2)

        self.m(f"{self.async_}def cleanup(self): {self.await_}self.http.close()")

    def get_signature(self, path: Component):
        signature = ["self"]
        for a in path.args:
            ann = 'Any' if a.com_types and self.is_core else a.annotation
            signature.append(f"{a}:{ann}{a.method_value}")
        signature.append("http_timeout: Optional[float] = None")
        return ','.join(signature)

    def method_description(self, path: Component):
        self.m('"'*3, 2)
        for p in path.desc:
            for pp in wrap(p.text):
                self.m(pp, 2)
            self.m()
        for arg in path.args:
            desc = f":param {arg.field}: {arg.desc.text}"
            wrapped_desc = '\n\t\t'.join(wrap(desc, subsequent_indent="\t", width=66))
            self.m(wrapped_desc, 2)
        self.m(f":param http_timeout: (float) ", 2, 2)
        self.m(f":returns: {path.result.annotation}", 2, 2)
        self.m(f"Reference: https://core.telegram.org/bots/api{path.anchor}", 2)
        self.m('"'*3, 2)

    def method_declaration(self, path: Component):
        if self.is_core:
            self.m("...", 2)
        else:
            args = ','.join([f"{a}={a}" for a in path.args])
            self.m(f"return {self.await_}self({path.camel}({args}), http_timeout=http_timeout)", 2)
