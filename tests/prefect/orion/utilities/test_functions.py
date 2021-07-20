import datetime
import pendulum
from enum import Enum
import json
from prefect.orion.utilities import functions
from typing import List, Dict, Any, Tuple, Union


class TestFunctionToSchema:
    def test_simple_function_with_no_arguments(self):
        def f():
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "properties": {},
            "title": "Parameters",
            "type": "object",
        }

    def test_function_with_one_required_argument(self):
        def f(x):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {"x": {"title": "x"}},
            "required": ["x"],
        }

    def test_function_with_one_optional_argument(self):
        def f(x=42):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {"x": {"title": "x", "default": 42}},
        }

    def test_function_with_one_optional_annotated_argument(self):
        def f(x: int = 42):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {"x": {"title": "x", "default": 42, "type": "integer"}},
        }

    def test_function_with_two_arguments(self):
        def f(x: int, y: float = 5.0):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {
                "x": {"title": "x", "type": "integer"},
                "y": {"title": "y", "default": 5.0, "type": "number"},
            },
            "required": ["x"],
        }

    def test_function_with_datetime_arguments(self):
        def f(
            x: datetime.datetime,
            y: pendulum.DateTime = pendulum.datetime(2025, 1, 1),
            z: datetime.timedelta = datetime.timedelta(seconds=5),
        ):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {
                "x": {"title": "x", "type": "string", "format": "date-time"},
                "y": {
                    "title": "y",
                    "default": "2025-01-01T00:00:00+00:00",
                    "type": "string",
                    "format": "date-time",
                },
                "z": {
                    "title": "z",
                    "default": 5.0,
                    "type": "number",
                    "format": "time-delta",
                },
            },
            "required": ["x"],
        }

    def test_function_with_enum_argument(self):
        class Color(Enum):
            RED = "RED"
            GREEN = "GREEN"
            BLUE = "BLUE"

        def f(x: Color = "RED"):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {
                "x": {
                    "title": "x",
                    "default": "RED",
                    "allOf": [{"$ref": "#/definitions/Color"}],
                }
            },
            "definitions": {
                "Color": {
                    "title": "Color",
                    "description": "An enumeration.",
                    "enum": ["RED", "GREEN", "BLUE"],
                }
            },
        }

    def test_function_with_generic_arguments(self):
        def f(
            a: List[str],
            b: Dict[str, Any],
            c: Any,
            d: Tuple[int, float],
            e: Union[str, bytes, int],
        ):
            pass

        schema = functions.parameter_schema(f)
        assert schema == {
            "title": "Parameters",
            "type": "object",
            "properties": {
                "a": {"title": "a", "type": "array", "items": {"type": "string"}},
                "b": {"title": "b", "type": "object"},
                "c": {"title": "c"},
                "d": {
                    "title": "d",
                    "type": "array",
                    "items": [{"type": "integer"}, {"type": "number"}],
                },
                "e": {
                    "title": "e",
                    "anyOf": [
                        {"type": "string"},
                        {"type": "string", "format": "binary"},
                        {"type": "integer"},
                    ],
                },
            },
            "required": ["a", "b", "c", "d", "e"],
        }


class TestMethodToSchema:
    def test_methods_with_no_arguments(self):
        class Foo:
            def f(self):
                pass

            @classmethod
            def g(cls):
                pass

            @staticmethod
            def h():
                pass

        for method in [Foo().f, Foo.g, Foo.h]:
            schema = functions.parameter_schema(method)
            assert schema == {
                "properties": {},
                "title": "Parameters",
                "type": "object",
            }

    def test_methods_with_enum_arguments(self):
        class Color(Enum):
            RED = "RED"
            GREEN = "GREEN"
            BLUE = "BLUE"

        class Foo:
            def f(self, color: Color = "RED"):
                pass

            @classmethod
            def g(cls, color: Color = "RED"):
                pass

            @staticmethod
            def h(color: Color = "RED"):
                pass

        for method in [Foo().f, Foo.g, Foo.h]:
            schema = functions.parameter_schema(method)
            assert schema == {
                "title": "Parameters",
                "type": "object",
                "properties": {
                    "color": {
                        "title": "color",
                        "default": "RED",
                        "allOf": [{"$ref": "#/definitions/Color"}],
                    }
                },
                "definitions": {
                    "Color": {
                        "title": "Color",
                        "description": "An enumeration.",
                        "enum": ["RED", "GREEN", "BLUE"],
                    }
                },
            }

    def test_methods_with_complex_arguments(self):
        class Foo:
            def f(self, x: datetime.datetime, y: int = 42, z: bool = None):
                pass

            @classmethod
            def g(cls, x: datetime.datetime, y: int = 42, z: bool = None):
                pass

            @staticmethod
            def h(x: datetime.datetime, y: int = 42, z: bool = None):
                pass

        for method in [Foo().f, Foo.g, Foo.h]:
            schema = functions.parameter_schema(method)
            assert schema == {
                "title": "Parameters",
                "type": "object",
                "properties": {
                    "x": {"title": "x", "type": "string", "format": "date-time"},
                    "y": {"title": "y", "default": 42, "type": "integer"},
                    "z": {"title": "z", "type": "boolean"},
                },
                "required": ["x"],
            }
