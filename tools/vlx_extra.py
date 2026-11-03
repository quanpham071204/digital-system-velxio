"""Read and evaluate the combinational/sequential netlist in a Velxio .vlx file.

This module is intentionally separate from ``vlx.py`` (the circuit builder).
It evaluates connectivity from wire endpoint equivalence, independent of the
direction in which a wire was serialized.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict


class NetlistError(ValueError):
    """Malformed or electrically ambiguous netlist."""


class UnknownValue(NetlistError):
    """A queried net has no known driver in the supplied state."""


def _pin(component_id, pin_name):
    return (str(component_id), str(pin_name))


class _UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, item):
        if item not in self.parent:
            self.parent[item] = item
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left, right):
        a, b = self.find(left), self.find(right)
        if a != b:
            self.parent[b] = a


class Circuit:
    """Load a .vlx path or parsed Velxio JSON payload.

    ``inputs`` maps slide-switch component ids or their names (case-insensitive)
    to 0/1 values. ``state`` maps flip-flop ids to either 0/1 (Q) or a mapping
    with ``Q`` and/or ``Qbar``. Missing switch values use the component's saved
    ``properties.value``. Missing FF state raises :class:`UnknownValue`.
    """

    def __init__(self, source, inputs=None, state=None):
        if isinstance(source, (str, os.PathLike)):
            with open(source, encoding="utf-8") as stream:
                self.data = json.load(stream)
        else:
            self.data = source
        if not isinstance(self.data, dict) or self.data.get("format") != "velxio-project":
            raise NetlistError("Expected a velxio-project JSON payload")

        self.components = {}
        for component in self.data.get("components", []):
            cid = str(component["id"])
            if cid in self.components:
                raise NetlistError(f"Duplicate component id: {cid}")
            self.components[cid] = component
        self.inputs = {str(k).casefold(): self._bit(v, f"input {k}") for k, v in (inputs or {}).items()}
        self.state = dict(state or {})
        self.uf = _UnionFind()
        self._wired_pins = set()
        for wire in self.data.get("wires", []):
            start, end = wire.get("start", {}), wire.get("end", {})
            a = _pin(start.get("componentId"), start.get("pinName"))
            b = _pin(end.get("componentId"), end.get("pinName"))
            if a[0] not in self.components or b[0] not in self.components:
                raise NetlistError(f"Wire references missing component: {a} -> {b}")
            self._wired_pins.update((a, b))
            self.uf.union(a, b)
        self._switch_values = self._resolve_switches()
        self._drivers = defaultdict(list)
        self._index_drivers()

    @staticmethod
    def _bit(value, where):
        if value not in (0, 1, False, True):
            raise NetlistError(f"{where} must be 0 or 1, got {value!r}")
        return int(value)

    def _resolve_switches(self):
        by_name = {}
        for cid, comp in self.components.items():
            if comp.get("metadataId") == "slide-switch":
                props = comp.get("properties", {})
                name = props.get("name", cid)
                by_name[cid.casefold()] = cid
                by_name[str(name).casefold()] = cid
                if cid.casefold().startswith("sw") and len(cid) > 2:
                    by_name[cid[2:].casefold()] = cid
        values = {}
        for cid in by_name.values():
            if cid in values:
                continue
            comp = self.components[cid]
            props = comp.get("properties", {})
            default = props.get("value")
            supplied = [self.inputs[key] for key, target in by_name.items()
                        if target == cid and key in self.inputs]
            if len(set(supplied)) > 1:
                raise NetlistError(f"Conflicting input aliases for switch {cid}")
            if supplied:
                values[cid] = supplied[0]
            elif default in (0, 1, False, True):
                values[cid] = int(default)
            else:
                raise UnknownValue(f"No input value for switch {cid}")
        unknown = set(self.inputs) - set(by_name)
        if unknown:
            raise NetlistError(f"Unknown switch input name/id: {', '.join(sorted(unknown))}")
        return values

    @staticmethod
    def _output_pins(comp):
        kind = comp.get("metadataId", "")
        if kind.startswith("flip-flop-"):
            return ("Q", "Qbar")
        if kind.startswith("logic-gate-"):
            return ("Y",)
        if kind.startswith("ic-74hc"):
            count = 6 if kind == "ic-74hc04" else 4
            return tuple(f"{n}Y" for n in range(1, count + 1))
        return ()

    def _index_drivers(self):
        for cid, comp in self.components.items():
            kind = comp.get("metadataId", "")
            if kind == "signal-generator":
                self._drivers[self.uf.find(_pin(cid, "SIG"))].append((cid, "SIG"))
                self._drivers[self.uf.find(_pin(cid, "GND"))].append((cid, "GND"))
            elif kind == "slide-switch":
                self._drivers[self.uf.find(_pin(cid, "2"))].append((cid, "2"))
            else:
                for pin in self._output_pins(comp):
                    self._drivers[self.uf.find(_pin(cid, pin))].append((cid, pin))
        for net, drivers in self._drivers.items():
            if len(drivers) > 1:
                raise NetlistError(f"Multiple drivers on net {net}: {drivers}")

    def _read_state(self, cid, pin):
        if cid not in self.state:
            raise UnknownValue(f"No state supplied for flip-flop {cid}")
        state = self.state[cid]
        if isinstance(state, dict):
            if pin not in state:
                if pin == "Qbar" and "Q" in state:
                    return 1 - self._bit(state["Q"], f"state {cid}.Q")
                if pin == "Q" and "Qbar" in state:
                    return 1 - self._bit(state["Qbar"], f"state {cid}.Qbar")
                raise UnknownValue(f"No {pin} state supplied for flip-flop {cid}")
            return self._bit(state[pin], f"state {cid}.{pin}")
        q = self._bit(state, f"state {cid}")
        return q if pin == "Q" else 1 - q

    def _component_output(self, cid, pin, active):
        comp = self.components[cid]
        kind = comp.get("metadataId", "")
        if kind == "signal-generator":
            props = comp.get("properties", {})
            waveform = props.get("waveform")
            if waveform != "dc":
                raise UnknownValue(f"Only DC signal-generator values are supported ({cid})")
            if pin == "GND":
                return 0
            offset = props.get("offset")
            amplitude = props.get("amplitude", 0)
            if amplitude != 0 or offset not in (0, 5):
                raise UnknownValue(f"Unsupported DC level for signal-generator {cid}: {offset}")
            return int(offset == 5)
        if kind == "slide-switch":
            value = self._switch_values[cid]
            selected = "3" if value else "1"
            if (cid, selected) in self._wired_pins:
                if self.uf.find(_pin(cid, selected)) == self.uf.find(_pin(cid, "2")):
                    raise NetlistError(f"Switch {cid} pin {selected} is wired directly to output pin 2")
                return self.read((cid, selected), active)
            if value:
                raise UnknownValue(f"Switch {cid}=1 has no source wired to pin 3")
            # In the project's usual wiring, pin 1 is unused and a real
            # pull-down resistor connects output pin 2 to GND. Never short
            # resistor pins together; validate the two sides independently.
            out_net = self.uf.find(_pin(cid, "2"))
            for rid, resistor in self.components.items():
                if resistor.get("metadataId") != "resistor":
                    continue
                if self.uf.find(_pin(rid, "1")) != out_net:
                    continue
                if (rid, "1") not in self._wired_pins or (rid, "2") not in self._wired_pins:
                    continue
                try:
                    if self.read((rid, "2"), active) == 0:
                        return 0
                except UnknownValue:
                    continue
            raise UnknownValue(f"Switch {cid}=0 has neither pin 1 source nor a resistor pull-down to GND")
        key = (cid, pin)
        if key in active:
            raise NetlistError(f"Combinational loop at {key}")
        nested = active | {key}
        if kind.startswith("flip-flop-"):
            return self._read_state(cid, pin)
        if kind.startswith("ic-74hc"):
            number = int(kind.removeprefix("ic-74hc"))
            gate = {"00": "nand", "02": "nor", "04": "not", "08": "and", "32": "or", "86": "xor"}.get(f"{number:02d}")
            if gate is None:
                raise UnknownValue(f"Unsupported IC kind: {kind}")
            n = pin[:-1]
            inputs = [self.read((cid, n + "A"), nested)]
            if gate != "not":
                inputs.append(self.read((cid, n + "B"), nested))
            return self._logic(gate, inputs)
        if kind.startswith("logic-gate-"):
            gate = kind.removeprefix("logic-gate-")
            arity = 1 if gate == "not" else 3 if gate.endswith("-3") else 2
            inputs = [self.read((cid, p), nested) for p in ("A", "B", "C")[:arity]]
            return self._logic(gate, inputs)
        raise UnknownValue(f"Unsupported driver {cid}.{pin} ({kind})")

    @staticmethod
    def _logic(gate, values):
        if gate == "not" and len(values) == 1:
            return 1 - values[0]
        if gate in ("and", "and-3"):
            return int(all(values))
        if gate in ("or", "or-3"):
            return int(any(values))
        if gate == "nand":
            return 1 - int(all(values))
        if gate == "nor":
            return 1 - int(any(values))
        if gate == "xor" and len(values) == 2:
            return values[0] ^ values[1]
        raise UnknownValue(f"Unsupported gate or arity: {gate} ({len(values)} inputs)")

    def read(self, pin, _active=None):
        """Read a pin/net value (pin is ``(component_id, pin_name)``)."""
        key = _pin(*pin)
        if key[0] not in self.components:
            raise NetlistError(f"Unknown component {key[0]}")
        active = set() if _active is None else _active
        driver_list = self._drivers.get(self.uf.find(key), [])
        if not driver_list:
            raise UnknownValue(f"Undriven net at {key}")
        cid, driver_pin = driver_list[0]
        return self._component_output(cid, driver_pin, active)

    def leds(self):
        """Return ``{led_component_id: 0/1}`` by reading its ``r_led_*`` pin 1."""
        results = {}
        for cid, comp in self.components.items():
            if comp.get("metadataId") != "led":
                continue
            resistor = "r_" + cid
            if resistor not in self.components:
                raise UnknownValue(f"LED {cid} has no series resistor {resistor}")
            results[cid] = self.read((resistor, "1"))
        return results

    def next_state(self):
        """Compute every FF's next Q from the same current input/state snapshot."""
        pending = {}
        for cid, comp in self.components.items():
            kind = comp.get("metadataId", "")
            if not kind.startswith("flip-flop-"):
                continue
            pending[cid] = self._next_ff_value(cid, kind.removeprefix("flip-flop-"))
        return pending

    def _next_ff_value(self, cid, ff_kind):
        if ff_kind == "d":
            return self.read((cid, "D"))
        if ff_kind == "t":
            return self._read_state(cid, "Q") ^ self.read((cid, "T"))
        if ff_kind == "jk":
            q = self._read_state(cid, "Q")
            j, k = self.read((cid, "J")), self.read((cid, "K"))
            return (j & (1 - q)) | ((1 - k) & q)
        raise UnknownValue(f"Unsupported flip-flop kind: {ff_kind}")

    def step(self, previous_inputs):
        """Apply rising-edge updates and return the simultaneous new FF states.

        ``previous_inputs`` supplies the switch values from the prior instant.
        State changes are computed from the current state and committed only
        after every flip-flop has been evaluated.
        """
        previous = Circuit(self.data, previous_inputs, self.state)
        pending = {}
        for cid, comp in self.components.items():
            kind = comp.get("metadataId", "")
            if not kind.startswith("flip-flop-"):
                continue
            q = self._read_state(cid, "Q")
            old_clk = previous.read((cid, "CLK"))
            current_clk = self.read((cid, "CLK"))
            if old_clk == 0 and current_clk == 1:
                pending[cid] = self._next_ff_value(cid, kind.removeprefix("flip-flop-"))
            else:
                pending[cid] = q
        self.state = pending
        return dict(pending)


def load(path, inputs=None, state=None):
    """Convenience constructor equivalent to ``Circuit(path, inputs, state)``."""
    return Circuit(path, inputs=inputs, state=state)


def evaluate(path, inputs=None, state=None):
    """Load a netlist and return its LED values."""
    return load(path, inputs=inputs, state=state).leds()


def route_for_demo(project):
    """Route project ground leads below the switches for clean demo clicking."""
    for wire in project.wires:
        end = wire.get("end", {})
        start = wire.get("start", {})
        if (end.get("componentId"), end.get("pinName")) == project.gnd and start.get("componentId") != "src":
            wire["waypoints"] = [{"x": 350, "y": 820}, {"x": 80, "y": 820}]
    return project
