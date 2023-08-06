from typing import Dict, List
from .events import Event, EpsilonEvent, StateEvent
from .exc import TransitionsImplementationError
from abc import ABC, abstractmethod


class StateMachineInterface(ABC):
    @property
    def name(self):
        raise NotImplementedError

    @name.setter
    def name(self, value):
        raise NotImplementedError

    @property
    def state(self):
        raise NotImplementedError

    @property
    def events(self):
        raise NotImplementedError

    @property
    def parent(self):
        raise NotImplementedError

    @parent.setter
    def parent(self, parent: "StateMachineInterface"):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def execute(self, event: Event):
        raise NotImplementedError

    def add_event(self, event, transitions: dict) -> "StateMachineInterface":
        raise NotImplementedError

    def add_machine(self, machine: "StateMachineInterface"):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError


class Moore(StateMachineInterface, dict):
    """
    Moore state machine. Moore state machine of the package consists of states which are actually the functions 
    that are to be executed once the machine got into the corresponding state.
    """
    def __init__(self, name: str, init_state: str = None):
        super().__init__()
        self.__state = init_state
        self.__events = {}
        self.__parent = None
        self.__name = name
        self.__extra_response = dict()

    @property
    def name(self) -> str:
        """Name of a Moore state-machine. Should be unique in case it is included in a nested machine."""
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def state(self) -> str:
        """Current machine's state."""
        return self.__state

    @property
    def events(self) -> List[Event]:
        """List of all events the machine is sensitive to."""
        return self.__events

    @property
    def parent(self) -> 'Moore':
        """Parent state machine if the current machine is nested into anouther one."""
        return self.__parent

    @parent.setter
    def parent(self, parent):
        self.__parent = parent

    def reset(self):
        """Reset to initial state including all nested machines if any."""
        self.__state = None
        if len(self):
            for child in self.values():
                child.reset()

    def __match(self, event_states):
        machines = {machine.name: machine.state for machine in self.values()}
        result = False
        if type(event_states) is tuple:
            name, state = event_states
            if name in machines:
                return machines[name] == state
        elif type(event_states) is dict:
            func, states = next(iter(event_states.items()))
            if func == "or":
                result = any(map(lambda state: self.__match(state), states))
            elif func == "and":
                result = all(map(lambda state: self.__match(state), states))
            elif func == "not":
                result = not self.__match(states)

        return result

    def __handle_child_state(self):
        for state_event in filter(
            lambda event: issubclass(event, StateEvent), self.__events
        ):
            if self.__match(state_event.states):
                r = self.execute(state_event())
                self.__extra_response.update(r)

    def execute(self, event: Event):
        """
        Execute an :class:`Event`. If current machine is nested into anouther one it triggers that machine
        and reports about its new state.
        """
        response = None
        if type(event) in self.__events and self.__state in self.__events[type(event)]:
            response = dict()
            next_state = self.__events[type(event)][self.__state]
            self.__state = next_state
            response.update({(self, next_state): getattr(self, next_state)(event)})
            if self.__parent:
                self.__parent.__handle_child_state()
            epsilon_response = self.execute(EpsilonEvent(event))
            if epsilon_response:
                response.update(epsilon_response)

        if len(self):
            response = response or dict()
            children_responses = dict()
            for machine in self.values():
                r = machine.execute(event)
                if r:
                    children_responses.update(r)

            response.update(children_responses)

        if response:
            response.update(self.__extra_response)
        else:
            response = self.__extra_response if self.__extra_response else None

        self.__extra_response = dict()

        return response

    def add_event(self, event: Event, transitions: Dict[str, str]):
        """
        Add a new :class:`Event`, so the machine becomes sensitive to that new event. 
        Parameter `transitions` defines the table of transitions
        """
        if issubclass(event, StateEvent):
            event.is_valid()
        for from_state, to_state in transitions.items():
            if not (
                from_state is None
                or isinstance(from_state, str)
                and hasattr(self, from_state)
            ):
                raise TransitionsImplementationError(from_state)
            if not (
                to_state is None
                or isinstance(to_state, str)
                and hasattr(self, to_state)
            ):
                raise TransitionsImplementationError(to_state)

        self.__events.update({event: transitions})
        return self

    def remove_event(self, event):
        """Remove an added event. Since you have removed the event the Moore machine is nor more sensitive to it."""
        self.__events.pop(event)
        return self

    def append(self, machine: 'Moore'):
        """An alias to :meth:`add_machine`"""
        self.add_machine(machine)

    def add_machine(self, machine: 'Moore'):
        """
        Append a machine into current one. If the machine has some extra machine nested 
        it will propogate all events to all of them.
        """
        machine.parent = self
        super().update({machine.name: machine})
        return self

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        """Represent machine as a dict"""
        return {
            "transition_table": {
                event.__name__: transitions
                for event, transitions in self.__events.items()
            },
            "parent": id(self.__parent) if self.__parent else None,
            "id": id(self),
            "nested_machines": list(self),
            "state": self.__state,
            "name": self.__name,
        }

    def __repr__(self):
        return f"({self.__name}, {self.__state})"

    def __eq__(self, other):
        return self.__events == other.events

    def __hash__(self):
        return hash(id(self))
