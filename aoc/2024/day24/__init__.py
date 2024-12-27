from collections import deque
from collections.abc import Callable, Iterable
from operator import and_, or_, xor
from typing import cast, Any, Literal, TypeAlias


BinaryFunction: TypeAlias = Callable[[Any, Any], Any]
GateName: TypeAlias = Literal["AND", "OR", "XOR"]
Wire: TypeAlias = str
Gate: TypeAlias = tuple[Wire, tuple[GateName, Wire, Wire]]
Wiring: TypeAlias = "tuple[GateName, Wiring | Wire, Wiring | Wire]"
GATE_FUNCTIONS: dict[GateName, BinaryFunction] = {
    "AND": and_, "OR": or_, "XOR": xor,
}


def parse_input(lines: Iterable[str]) -> tuple[dict[Wire, int], list[Gate]]:
    """
    Parse the input, and return a collection of wires and gates.
    """
    line_iter = iter(lines)

    # Collect wires until the first blank line
    wires: dict[Wire, int] = {}
    for line in line_iter:
        if not line:
            break
        wire, signal = line.split(": ")
        wires[wire] = int(signal)

    # Collect gates until the end of the input
    gates: list[Gate] = []
    for line in line_iter:
        connections, out_wire = line.split(" -> ")
        in_wire_a, gate_name, in_wire_b = connections.split()
        gates.append((
            out_wire,
            (cast(GateName, gate_name), in_wire_a, in_wire_b),
        ))

    return wires, gates


def aoc2024_day24_part1(lines: Iterable[str]) -> int:
    wires, gates = parse_input(lines)
    gates = deque(gates)

    z_wires = set(wire for wire, _ in gates if wire.startswith("z"))
    z_wires_left = z_wires.copy()
    # Until every Z wire has an output
    while z_wires_left:
        gate_item = out_wire, (gate_name, *connections) = gates.popleft()
        # Get the values of the incoming signals for this gate
        try:
            gate_inputs = tuple(wires[conn] for conn in connections)
        except KeyError:
            # If some of the signals are undetermined, skip this gate
            gates.append(gate_item)
            continue

        # Calculate what the output signal should be
        wires[out_wire] = GATE_FUNCTIONS[gate_name](*gate_inputs)
        # If this is a Z wire, remove it from the remaining Z wires
        if out_wire.startswith("z"):
            z_wires_left.remove(out_wire)

    # Get the bits of the Z wires as a binary number
    z_bits = "".join(
        str(wires[wire])
        for wire in sorted(z_wires, reverse=True)
    )
    return int(z_bits, base=2)


def aoc2024_day24_part2(lines: Iterable[str]) -> str:
    # NOTE I did not solve 2024 Day 24 Part 2 with code; I did it by
    # manually checking for and fixing errors in the adder circuit,
    # which was honestly easier than doing it with code. This code
    # should be able to find the errors for any puzzle input, but it
    # does not work generally.
    import itertools as it

    wires, gates = parse_input(lines)
    gates = dict(gates)

    x_wires = sorted(wire for wire in wires if wire.startswith("x"))
    y_wires = sorted(wire for wire in wires if wire.startswith("y"))
    z_wires = sorted(wire for wire, _ in gates.items() if wire.startswith("z"))
    # There should by as many X wires as Y wires...
    assert len(x_wires) == len(y_wires)
    # ...and one more Z wire than X/Y wires
    assert len(z_wires) == len(x_wires) + 1

    # List of wire swaps that should happen
    wire_swaps: list[tuple[Wire, Wire]] = []

    def fix_wire(wire: Wire, expected: Wire):
        """
        Swap `wire` and `expected` if they do not match.
        """
        if wire != expected:
            wire_swaps.append((wire, expected))
            gates[wire], gates[expected] = gates[expected], gates[wire]

    def find_wiring(wiring: Wiring) -> Wire | None:
        """
        Find the name of the wire that matches the given wiring. If one
        could not be found, `None` is returned.
        """
        gate_name, *connection_wirings = wiring
        # Try finding the wires corresponding to the connection wirings
        connections: set[Wire] = set()
        for connection in connection_wirings:
            if isinstance(connection, Wire):
                wire = connection
            else:
                wire = find_wiring(connection)
                # If no wire corresponds to this connection wiring
                if wire is None:
                    # The input wiring cannot be found
                    return None
            connections.add(wire)
        # Find the wire that matches the input wiring
        return next((
            wire
            for wire, (name, *conns) in gates.items()
            if name == gate_name
            and set(conns) == connections
        ), None)

    def fix_wiring(wire: Wire, wiring: Wiring):
        """
        Swap the wires such that the wiring of `wire` conforms to
        `wiring`.
        """
        correct_wire = find_wiring(wiring)
        # If there exists a wire with this exact wiring
        if correct_wire is not None:
            # We only need to swap the input wire with the correct wire
            fix_wire(wire, correct_wire)
            return

        wiring_gate_name, *wiring_connections = wiring
        wire_gate_name, *wire_connections = gates[wire]
        # FIXME This seems to catch some errors, but I don't know why,
        # and I don't know how to fix them once I find them.
        if wiring_gate_name != wire_gate_name:
            raise RuntimeError("gate names don't match")

        wiring_map = {
            connection: (
                connection
                if isinstance(connection, Wire)
                else find_wiring(connection)
            )
            for connection in wiring_connections
        }
        shared_wires = set(wire_connections) & set(wiring_map.values())
        # For each group of connected wires that aren't already shared
        # between the input wire and input wiring
        for (subwiring, wiring_conn), wire_conn in zip(
            filter(lambda sw: sw[1] not in shared_wires, wiring_map.items()),
            filter(lambda w: w not in shared_wires, wire_connections),
        ):
            # FIXME If this connection of the input wire isn't in the
            # collection of gates, it's an X/Y wire. I don't know how to
            # fix this, either.
            if wire_conn not in gates:
                raise RuntimeError("wiring too complex")
            # Fix this input wire connection
            if wiring_conn is None:
                fix_wiring(wire_conn, cast(Wiring, subwiring))
            else:
                fix_wire(wire_conn, wiring_conn)

    # Fix wiring for the least significant digit
    fix_wiring(z_wires[0], ("XOR", x_wires[0], y_wires[0]))

    carry_wire: Wire | None = None
    # For each digit after the least significant digit
    for (x_prev, y_prev, _), (x_curr, y_curr, z_curr) in it.pairwise(
        zip(x_wires, y_wires, z_wires)
    ):
        carry_wiring: Wiring
        # If this is the first digit with a carry
        if carry_wire is None:
            # The carry will happen if the sum is 2
            carry_wiring = ("AND", x_prev, y_prev)
        else:
            # Otherwise, the carry will happen if...
            carry_wiring = (
                "OR",
                # ...the sum is at least 2...
                ("AND", x_prev, y_prev),
                # ...or the sum is 1, and there was a previous carry
                (
                    "AND",
                    ("XOR", x_prev, y_prev),
                    carry_wire,
                ),
            )

        # This Z wire should combine the X wire, Y wire, and carry; it
        # should be 1 if an odd number of those are 1
        fix_wiring(z_curr, (
            "XOR",
            ("XOR", x_curr, y_curr),
            carry_wiring,
        ))
        carry_wire = find_wiring(carry_wiring)
        assert carry_wire is not None

    # Return the swapped wires, sorted and separated by commas
    return ",".join(sorted(set(it.chain(*wire_swaps))))


parts = (aoc2024_day24_part1, aoc2024_day24_part2)
