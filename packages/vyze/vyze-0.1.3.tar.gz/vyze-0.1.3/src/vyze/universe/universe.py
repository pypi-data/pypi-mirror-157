from typing import Union

import requests
import yaml

from ..system.resource import FormatType

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Field:
    """
    Represents a VYZE field.
    """

    def __init__(self, relation, origin, target):
        self._relation = relation
        self._origin = origin
        self._target = target

    @property
    def type(self):
        return None

    @property
    def relation(self) -> 'Model':
        return self._relation

    @property
    def origin(self) -> 'Model':
        return self._origin

    @property
    def target(self) -> 'Model':
        return self._target

    def __str__(self):
        return str(self._relation)

    def __repr__(self):
        return f'Field {str(self._relation)}'


class Model:
    """
    Represents a VYZE model.
    """

    def __init__(self, universe, name, base, target):
        self.universe = universe
        self._name = name
        self._base = base
        self._target = target

        self._description = None
        self._object_id = None
        self._type = None

        self._abstracts = dict()
        self._specials = dict()

        self._fields = dict()
        self._field = None

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def object_id(self) -> str | None:
        return self._object_id

    @property
    def type(self) -> str | None:
        return self._type

    @property
    def abstracts(self) -> dict[str, 'Model']:
        return self._abstracts

    @property
    def specials(self) -> dict[str, 'Model']:
        return self._specials

    @property
    def fields(self) -> list[Field]:
        return list(self._fields.values())

    @property
    def field_names(self) -> list[str]:
        return [str(f) for f in self._fields.values()]

    @property
    def fq_name(self) -> str:
        """
        Returns:
            The fully qualified name of the model of the form `base.name/target`.
        """
        return f'{self._base}.{self._name}/{self._target}'

    @property
    def scoped_name(self) -> str:
        """
        Returns:
            The name of the model usually only valid in its target universe.
        """
        return simplify_object_ident(self.fq_name, self._target)

    def get_field(self, field) -> Field | None:
        ident = get_full_object_ident(field, self._base)
        return self._fields.get(ident)

    def get_type(self) -> FormatType | None:
        if self.name == '@string':
            return FormatType.STRING
        if self.name == '@integer':
            return FormatType.INTEGER
        if self.name == '@float':
            return FormatType.FLOAT
        if self.name == '@boolean':
            return FormatType.BOOLEAN
        if self.name == '@data':
            return FormatType.RAW
        if len(self.abstracts) == 0:
            return None
        for abstract in self.abstracts.values():
            abstract_model = self.universe.get_model(abstract)
            if not abstract_model:
                continue
            abstract_type = abstract_model.get_type()
            if abstract_type:
                return abstract_type

    def __str__(self):
        return simplify_object_ident(f'{self._base}.{self._name}/{self._target}', self._target)

    def __repr__(self):
        return f'Model {str(self)}'


class Universe:
    """
    Represents a VYZE universe.
    """

    def __init__(self, name):
        self._name = name

        self._description = None
        self._bases = None
        self._dependencies = None

        self._models = dict()

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def bases(self):
        return self._bases

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def models(self) -> list[Model]:
        return list(self._models.values())

    def get_model(self, model) -> Model | None:
        ident = get_full_object_ident(model, self.name)
        return self._models.get(ident)

    def resolve(self, name) -> str | None:
        model = self.get_model(name)
        if not model:
            raise RuntimeError(f'model not found: {name}')
        if not model.object_id:
            raise RuntimeError(f'missing object object: {name}')
        return model.object_id

    def _add_model_def(self, object_def):
        name, base, target = parse_object_def(object_def, self.name)
        model = Model(self, name, base, target)
        self._models[model.fq_name] = model
        return model

    def _add_abstraction_def(self, abstraction_def):
        split_abs = abstraction_def.split(':')

        abstract = self.get_model(split_abs[0])
        if not abstract:
            raise RuntimeError(f'missing abstract: {split_abs[0]}')

        special = self.get_model(split_abs[1])
        if not special:
            raise RuntimeError(f'missing special: {split_abs[1]}')

        abstract.specials[special.fq_name] = special
        special.abstracts[abstract.fq_name] = abstract

    def _add_relation_def(self, relation_def):
        split_rel = relation_def.split(':')

        relation = self.get_model(split_rel[0])
        if not relation:
            raise RuntimeError(f'missing relation: {split_rel[0]}')

        origin = self.get_model(split_rel[1])
        if not origin:
            raise RuntimeError(f'missing origin: {split_rel[1]}')

        target = self.get_model(split_rel[2])
        if not target:
            raise RuntimeError(f'missing target: {split_rel[2]}')

        field = Field(relation, origin, target)

        relation._field = field
        origin._fields[relation.fq_name] = field

    def __getitem__(self, item):
        return self.resolve(item)

    def __repr__(self):
        return f'Universe {self.name}'


def load_universe_from_api(universe_name, url='https://api.vyze.io/app/'):
    """
    Loads a universe, its models, fields and values from the VYZE API.

    Args:
        universe_name: Name of the universe.
        url: URL of the VYZE API.

    Returns:
        A universe object if successful or `None` otherwise.
    """

    resp = requests.get(f'{url}universe/resolve/{universe_name}')
    if resp.status_code != 200:
        return None
    universe_id = resp.json()
    resp = requests.get(f'{url}universe/{universe_id}/export?o=1')
    if resp.status_code != 200:
        return None
    universe_def = resp.content
    return load_universe(universe_def)


def load_universe_from_file(filepath):
    """
    Loads a universe, its models, fields and values from a definition file.

    Args:
        filepath: Path of the definition file.

    Returns:
        A universe object if successful or `None` otherwise.
    """

    with open(filepath) as f:
        contents = f.read()
        return load_universe(contents)


def load_universe(universe_def: Union[bytes, str]) -> Union[Universe, None]:
    """
    Parses and loads a universe from the given universe definition.

    Args:
        universe_def: Universe definition in YAML format.

    Returns:
        A universe object if successful or `None` otherwise.
    """

    def_struct = yaml.load(universe_def, Loader=Loader)
    universe = Universe(def_struct['name'])
    universe._description = def_struct['description']
    universe._bases = def_struct['bases']
    universe._dependencies = def_struct['dependencies']

    for object_def in def_struct['objects']:
        universe._add_model_def(object_def)

    for info in def_struct['info']:
        mapping = info['mapping']
        model = universe.get_model(mapping)
        if not model:
            continue
        model._description = info['description']
        model._type = info['type']
        model._object_id = info.get('object')

    for abstraction_def in def_struct['abstractions']:
        universe._add_abstraction_def(abstraction_def)

    for relation_def in def_struct['relations']:
        universe._add_relation_def(relation_def)

    universe.loaded = True

    return universe


def get_full_object_ident(name, universe_scope=None):
    """
    Returns

    Args:
        name: Model identifier of any form.
        universe_scope: Universe name of the universe serving as scope.

    Returns:
        A fully qualified model identifier of the form `base_universe.model_name/target_universe`.
    """
    name, base, target = parse_object_def(name, universe_scope)
    return f'{base}.{name}/{target}'


def simplify_object_ident(name, universe_scope=None):
    """
        Creates a simplified, scoped name for the given model name.

        - `model_name`, if the model entirely resides in this universe
        - `base_universe.model_name/`, if the model was copied from the universe `base_universe`
        - `base_universe.model_name`, if the model entirely resides in the universe `base_universe`
        - `base_universe.model_name/target_universe`, if the model was copied from the universe `base_universe` and resides in the universe `target_universe`
    Args:
        name: Model identifier of any form.
        universe_scope: Universe name of the universe serving as scope.

    Returns:
        A scoped model identifier.
    """

    name, base, target = parse_object_def(name, universe_scope)

    if universe_scope and target == universe_scope:
        if base == universe_scope:
            return name
        else:
            return f'{base}.{name}/'
    else:
        if target == base:
            return f'{base}.{name}'
        else:
            return f'{base}.{name}/{target}'


def parse_object_def(name, universe_scope=None):
    """
    Parses an object identifier. If the object identifier is scoped it usually requires a universe scope.

    Args:
        name: Model identifier of any form.
        universe_scope: Universe name of the universe serving as scope.

    Returns:
        A triple `name`, `base`, `target` representing the name, base and target of the identifier.
    """

    split_a = name.split('/')
    base_part = split_a[0]
    split_b = base_part.split('.')

    if len(split_b) == 1:
        if not universe_scope:
            raise RuntimeError('requires universe scope')
        base = universe_scope
        name = split_b[0]
    elif len(split_b) == 2:
        base = split_b[0]
        name = split_b[1]
    else:
        return None, None, None

    if len(split_a) == 1:
        target = base
    elif len(split_a) == 2:
        if split_a[1] == '':
            if not universe_scope:
                raise RuntimeError('requires universe scope')
            target = universe_scope
        else:
            target = split_a[1]
    else:
        return None, None, None

    return name, base, target
