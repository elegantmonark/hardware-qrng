"""Generate the native ED-4 KiCad schematic from installed KiCad symbols."""

from copy import deepcopy
import os
from pathlib import Path
import sys
from uuid import uuid4


KIUTILS_PATH = Path(os.environ["TEMP"]) / "ed4_kiutils"
sys.path.insert(0, str(KIUTILS_PATH))

from kiutils.items.common import (
    Effects,
    Font,
    Justify,
    PageSettings,
    Position,
    Property,
    Stroke,
    TitleBlock,
)
from kiutils.items.schitems import (
    Connection,
    HierarchicalSheetInstance,
    Junction,
    LocalLabel,
    SchematicSymbol,
    SymbolProjectInstance,
    SymbolProjectPath,
    Text,
)
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib


PROJECT_NAME = "ED4_Perfboard_Prototype"
OUTPUT_PATH = Path(__file__).resolve().parent / f"{PROJECT_NAME}.kicad_sch"
SYMBOL_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
ROOT_UUID = str(uuid4())


def uid():
    return str(uuid4())


def font_effect(size=1.27, hidden=False):
    return Effects(font=Font(width=size, height=size), hide=hidden)


def load_symbol(filename, name, nickname):
    library = SymbolLib.from_file(str(SYMBOL_ROOT / filename))
    symbol = deepcopy(next(item for item in library.symbols if item.entryName == name))
    symbol.libId = f"{nickname}:{name}"
    return symbol


def unit_pin_numbers(symbol, unit):
    numbers = []
    for child in symbol.units:
        if child.unitId in (0, unit) and (child.styleId in (None, 0, 1)):
            numbers.extend(str(pin.number) for pin in child.pins)
    numbers.extend(str(pin.number) for pin in symbol.pins)
    return sorted(set(numbers))


def make_properties(reference, value, footprint, x, y, angle=0):
    if reference.startswith(("R", "C", "D")):
        if angle % 180 == 0:
            reference_position = Position(x + 4.4, y - 1.4, 0)
            value_position = Position(x + 4.4, y + 1.4, 0)
        else:
            reference_position = Position(x, y - 3.0, 0)
            value_position = Position(x, y + 3.0, 0)
    else:
        reference_position = Position(x, y - 5.5, 0)
        value_position = Position(x, y + 5.5, 0)

    return [
        Property(
            key="Reference",
            value=reference,
            position=reference_position,
            effects=font_effect(1.0),
        ),
        Property(
            key="Value",
            value=value,
            position=value_position,
            effects=font_effect(1.0),
        ),
        Property(
            key="Footprint",
            value=footprint,
            position=Position(x, y, 0),
            effects=font_effect(hidden=True),
        ),
        Property(
            key="Datasheet",
            value="",
            position=Position(x, y, 0),
            effects=font_effect(hidden=True),
        ),
        Property(
            key="Description",
            value="ED-4 placement prototype component",
            position=Position(x, y, 0),
            effects=font_effect(hidden=True),
        ),
    ]


def rotated_pin_position(x, y, dx, dy, angle):
    angle %= 360
    if angle == 0:
        rx, ry = dx, -dy
    elif angle == 90:
        rx, ry = -dy, -dx
    elif angle == 180:
        rx, ry = -dx, dy
    elif angle == 270:
        rx, ry = dy, dx
    else:
        raise ValueError("Only right-angle rotations are used")
    return x + rx, y + ry


def pin_positions(symbol, unit, x, y, angle=0):
    positions = {}
    for child in symbol.units:
        if child.unitId in (0, unit) and (child.styleId in (None, 0, 1)):
            for pin in child.pins:
                positions[str(pin.number)] = rotated_pin_position(
                    x, y, pin.position.X, pin.position.Y, angle
                )
    for pin in symbol.pins:
        positions[str(pin.number)] = rotated_pin_position(
            x, y, pin.position.X, pin.position.Y, angle
        )
    return positions


def add_instance(
    schematic,
    symbol,
    reference,
    value,
    footprint,
    x,
    y,
    unit,
    pin_nets=None,
    angle=0,
    pin_source=None,
    on_board=True,
    hide_reference=False,
    hide_value=False,
):
    # KiCad's default schematic connection grid is 1.27 mm.
    x = round(x / 1.27) * 1.27
    y = round(y / 1.27) * 1.27
    instance_uuid = uid()
    source = pin_source if pin_source is not None else symbol
    positions = pin_positions(source, unit, x, y, angle)
    pin_ids = {number: uid() for number in unit_pin_numbers(source, unit)}

    properties = make_properties(reference, value, footprint, x, y, angle)
    properties[0].effects.hide = hide_reference
    properties[1].effects.hide = hide_value

    instance = SchematicSymbol(
        position=Position(x, y, angle),
        unit=unit,
        inBom=True,
        onBoard=on_board,
        dnp=False,
        uuid=instance_uuid,
        properties=properties,
        pins=pin_ids,
        instances=[
            SymbolProjectInstance(
                name=PROJECT_NAME,
                paths=[
                    SymbolProjectPath(
                        sheetInstancePath=f"/{ROOT_UUID}",
                        reference=reference,
                        unit=unit,
                    )
                ],
            )
        ],
    )
    instance.libId = symbol.libId
    schematic.schematicSymbols.append(instance)

    if pin_nets is not None:
        for number, net_name in pin_nets.items():
            px, py = positions[str(number)]
            schematic.labels.append(
                LocalLabel(
                    text=net_name,
                    position=Position(round(px, 3), round(py, 3), 0),
                    effects=font_effect(0.9),
                    uuid=uid(),
                )
            )

    return positions


def add_wire(schematic, *points):
    """Add orthogonal two-point wire segments through the supplied points."""
    rounded = [(round(x, 3), round(y, 3)) for x, y in points]
    for start, end in zip(rounded, rounded[1:]):
        if start == end:
            continue
        schematic.graphicalItems.append(
            Connection(
                type="wire",
                points=[Position(*start), Position(*end)],
                stroke=Stroke(width=0, type="default"),
                uuid=uid(),
            )
        )


def add_label(schematic, text, x, y, angle=0, justify=None):
    effects = font_effect(0.9)
    if justify is not None:
        effects.justify = Justify(horizontally=justify)
    schematic.labels.append(
        LocalLabel(
            text=text,
            position=Position(round(x, 3), round(y, 3), angle),
            effects=effects,
            uuid=uid(),
        )
    )


def add_junction(schematic, x, y):
    schematic.junctions.append(
        Junction(position=Position(round(x, 3), round(y, 3)), uuid=uid())
    )


def add_note(schematic, text, x, y, size=1.27, bold=False):
    schematic.texts.append(
        Text(
            text=text,
            position=Position(x, y, 0),
            effects=Effects(font=Font(width=size, height=size, bold=bold)),
            uuid=uid(),
        )
    )


def build_label_only_reference():
    schematic = Schematic.create_new()
    schematic.uuid = ROOT_UUID
    schematic.paper = PageSettings(paperSize="A4")
    schematic.titleBlock = TitleBlock(
        title="ED-4 QRNG Perfboard Prototype",
        date="2026-10-21",
        revision="DRAFT",
        company="Trishan Biswas",
        comments={
            1: "Proposed ED-3 topology transferred to an 89 x 52 mm perfboard",
            2: "Prototype only - not electrically validated",
            3: "Arduino AREF remains disconnected",
        },
    )
    schematic.sheetInstances = [HierarchicalSheetInstance(instancePath="/", page="1")]

    r_symbol = load_symbol("Device.kicad_sym", "R", "Device")
    c_symbol = load_symbol("Device.kicad_sym", "C", "Device")
    cp_symbol = load_symbol("Device.kicad_sym", "C_Polarized", "Device")
    led_symbol = load_symbol("Device.kicad_sym", "LED", "Device")
    connector_symbol = load_symbol(
        "Connector_Generic.kicad_sym", "Conn_01x04", "Connector_Generic"
    )
    testpoint_symbol = load_symbol("Connector.kicad_sym", "TestPoint", "Connector")
    power_flag_symbol = load_symbol("power.kicad_sym", "PWR_FLAG", "power")
    lm2904_symbol = load_symbol(
        "Amplifier_Operational.kicad_sym", "LM2904", "Amplifier_Operational"
    )

    schematic.libSymbols = [
        r_symbol,
        c_symbol,
        cp_symbol,
        led_symbol,
        connector_symbol,
        testpoint_symbol,
        power_flag_symbol,
        lm2904_symbol,
    ]

    resistor_fp = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
    capacitor_fp = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"
    testpoint_fp = "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm"

    add_note(
        schematic,
        "ED-4 PERFBOARD PROTOTYPE - DRAFT, NOT ELECTRICALLY VALIDATED",
        145,
        18,
        1.8,
        True,
    )
    add_note(
        schematic,
        "Final permanent wiring must match the ED-3 circuit that passes bring-up and controlled testing.",
        145,
        23,
        1.05,
    )

    add_instance(
        schematic,
        connector_symbol,
        "J1",
        "ARDUINO",
        "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        35,
        48,
        1,
        {"1": "+5V", "2": "+3V3", "3": "GND", "4": "A0"},
    )
    add_note(schematic, "Arduino harness", 25, 35, 1.2, True)

    add_instance(schematic, r_symbol, "R1", "10 kOhm", resistor_fp, 70, 38, 1,
                 {"1": "+5V", "2": "VREF_RAW"}, 180)
    add_instance(schematic, r_symbol, "R2", "10 kOhm", resistor_fp, 70, 58, 1,
                 {"1": "VREF_RAW", "2": "GND"}, 180)
    add_instance(
        schematic,
        cp_symbol,
        "CREF",
        "10 uF",
        "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm",
        90,
        58,
        1,
        {"1": "VREF_RAW", "2": "GND"},
        180,
    )
    add_note(schematic, "Midpoint reference", 62, 30, 1.2, True)

    add_instance(
        schematic,
        lm2904_symbol,
        "U1",
        "LM358N",
        "Package_DIP:DIP-8_W7.62mm",
        125,
        42,
        1,
        {"1": "VREF_BUFFERED", "2": "VREF_BUFFERED", "3": "VREF_RAW"},
    )
    add_note(schematic, "U1A: VREF buffer", 113, 30, 1.2, True)

    add_instance(schematic, r_symbol, "RLED", "10 MOhm", resistor_fp, 165, 38, 1,
                 {"1": "+3V3", "2": "SOURCE_NODE"}, 180)
    add_instance(
        schematic,
        led_symbol,
        "D1",
        "GREEN SOURCE LED",
        "LED_THT:LED_D5.0mm",
        165,
        58,
        1,
        {"1": "SOURCE_NODE", "2": "GND"},
    )
    add_instance(schematic, c_symbol, "CIN", "100 nF", capacitor_fp, 190, 48, 1,
                 {"1": "SOURCE_NODE", "2": "SIGNAL_INPUT"}, 90)
    add_note(schematic, "Experimental LED source", 153, 30, 1.2, True)

    add_instance(
        schematic,
        lm2904_symbol,
        "U1",
        "LM358N",
        "Package_DIP:DIP-8_W7.62mm",
        225,
        48,
        2,
        {"5": "SIGNAL_INPUT", "6": "FEEDBACK", "7": "AMP_OUT"},
    )
    add_note(schematic, "U1B: signal gain", 213, 30, 1.2, True)

    add_instance(schematic, r_symbol, "RBIAS", "330 kOhm", resistor_fp, 205, 88, 1,
                 {"1": "SIGNAL_INPUT", "2": "VREF_BUFFERED"}, 180)
    add_instance(schematic, r_symbol, "RF", "330 kOhm", resistor_fp, 230, 88, 1,
                 {"1": "AMP_OUT", "2": "FEEDBACK"}, 180)
    add_instance(schematic, r_symbol, "RG", "4.4 kOhm", resistor_fp, 255, 88, 1,
                 {"1": "FEEDBACK", "2": "VREF_BUFFERED"}, 180)
    add_instance(schematic, r_symbol, "ROUT", "690 Ohm", resistor_fp, 260, 48, 1,
                 {"1": "AMP_OUT", "2": "A0"}, 90)
    add_note(schematic, "Bias, feedback and A0 protection", 205, 72, 1.2, True)

    add_instance(
        schematic,
        lm2904_symbol,
        "U1",
        "LM358N",
        "Package_DIP:DIP-8_W7.62mm",
        125,
        92,
        3,
        {"4": "GND", "8": "+5V"},
    )
    add_instance(schematic, c_symbol, "CDEC", "100 nF", capacitor_fp, 150, 92, 1,
                 {"1": "+5V", "2": "GND"}, 180)
    add_instance(
        schematic,
        power_flag_symbol,
        "#FLG01",
        "PWR_FLAG",
        "",
        102,
        87,
        1,
        {"1": "+5V"},
        on_board=False,
    )
    add_instance(
        schematic,
        power_flag_symbol,
        "#FLG02",
        "PWR_FLAG",
        "",
        102,
        97,
        1,
        {"1": "GND"},
        on_board=False,
    )
    add_note(schematic, "U1 power and decoupling", 112, 75, 1.2, True)

    test_points = [
        ("TP1", "VREF_RAW", 45),
        ("TP2", "VREF_BUFFERED", 75),
        ("TP3", "SOURCE_NODE", 110),
        ("TP4", "SIGNAL_INPUT", 145),
        ("TP5", "AMP_OUT", 180),
        ("TP6", "A0", 215),
        ("TP7", "GND", 245),
    ]
    for reference, net_name, x in test_points:
        add_instance(
            schematic,
            testpoint_symbol,
            reference,
            net_name,
            testpoint_fp,
            x,
            125,
            1,
            {"1": net_name},
        )
    add_note(schematic, "Bring-up test points", 25, 113, 1.2, True)

    add_note(
        schematic,
        "Nominal signal gain: 1 + 330 kOhm / 4.4 kOhm = 76. Check output headroom and stability before connecting A0.",
        145,
        145,
        1.0,
    )
    add_note(
        schematic,
        "D1 is intentionally reverse biased: cathode at SOURCE_NODE, anode at GND. This does not by itself establish a quantum-noise mechanism.",
        145,
        151,
        1.0,
    )
    add_note(
        schematic,
        "Arduino AREF remains disconnected. Disconnect power before changing the assembly.",
        145,
        157,
        1.0,
    )

    schematic.to_file(str(OUTPUT_PATH), encoding="utf-8")
    print(OUTPUT_PATH)


def main():
    """Generate the clean, connected ED-4 engineering schematic."""
    schematic = Schematic.create_new()
    schematic.uuid = ROOT_UUID
    schematic.paper = PageSettings(paperSize="A4")
    schematic.titleBlock = TitleBlock(
        title="ED-4 QRNG Perfboard Prototype",
        date="2026-10-22",
        revision="DRAFT 2",
        company="Trishan Biswas",
        comments={
            1: "Connected engineering schematic for the ED-4 perfboard layout",
            2: "Verify component values and staged measurements before assembly",
            3: "Arduino AREF remains disconnected",
        },
    )
    schematic.sheetInstances = [
        HierarchicalSheetInstance(instancePath="/", page="1")
    ]

    r_symbol = load_symbol("Device.kicad_sym", "R", "Device")
    c_symbol = load_symbol("Device.kicad_sym", "C", "Device")
    cp_symbol = load_symbol("Device.kicad_sym", "C_Polarized", "Device")
    led_symbol = load_symbol("Device.kicad_sym", "LED", "Device")
    connector_symbol = load_symbol(
        "Connector_Generic.kicad_sym", "Conn_01x04", "Connector_Generic"
    )
    testpoint_symbol = load_symbol(
        "Connector.kicad_sym", "TestPoint", "Connector"
    )
    power_flag_symbol = load_symbol("power.kicad_sym", "PWR_FLAG", "power")
    lm2904_symbol = load_symbol(
        "Amplifier_Operational.kicad_sym", "LM2904", "Amplifier_Operational"
    )

    schematic.libSymbols = [
        r_symbol,
        c_symbol,
        cp_symbol,
        led_symbol,
        connector_symbol,
        testpoint_symbol,
        power_flag_symbol,
        lm2904_symbol,
    ]

    resistor_fp = (
        "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_"
        "P10.16mm_Horizontal"
    )
    capacitor_fp = "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm"
    testpoint_fp = "TestPoint:TestPoint_THTPad_D2.0mm_Drill1.0mm"

    add_note(
        schematic,
        "ED-4 QRNG PERFBOARD PROTOTYPE",
        145,
        16,
        1.8,
        True,
    )
    add_note(
        schematic,
        "Buffered reference, reverse-biased LED source and AC-coupled gain stage",
        145,
        21,
        1.0,
    )

    # Arduino power and ADC harness.
    add_note(schematic, "ARDUINO INTERFACE", 34, 29, 1.15, True)
    j1 = add_instance(
        schematic,
        connector_symbol,
        "J1",
        "ARDUINO",
        "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        40.64,
        45.72,
        1,
    )
    for number, net_name in {
        "1": "+5V",
        "2": "+3V3",
        "3": "GND",
        "4": "A0",
    }.items():
        px, py = j1[number]
        add_wire(schematic, (px - 6.35, py), (px, py))
        add_label(schematic, net_name, px - 6.35, py, justify="right")

    # Midpoint reference and U1A voltage follower.
    add_note(schematic, "MIDPOINT REFERENCE AND BUFFER", 95, 29, 1.15, True)
    r1 = add_instance(
        schematic,
        r_symbol,
        "R1",
        "10 kOhm",
        resistor_fp,
        69.85,
        40.64,
        1,
    )
    r2 = add_instance(
        schematic,
        r_symbol,
        "R2",
        "10 kOhm",
        resistor_fp,
        69.85,
        52.07,
        1,
    )
    cref = add_instance(
        schematic,
        cp_symbol,
        "CREF",
        "10 uF",
        "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm",
        85.09,
        52.07,
        1,
    )
    u1a = add_instance(
        schematic,
        lm2904_symbol,
        "U1",
        "LM358N",
        "Package_DIP:DIP-8_W7.62mm",
        110.49,
        50.80,
        1,
    )

    vref_y = u1a["3"][1]
    add_wire(schematic, r1["1"], (r1["1"][0], r1["1"][1] - 3.81))
    add_label(
        schematic,
        "+5V",
        r1["1"][0],
        r1["1"][1] - 3.81,
        justify="right",
    )
    add_wire(
        schematic,
        r1["2"],
        (r1["2"][0], vref_y),
        u1a["3"],
    )
    add_wire(schematic, r2["1"], (r2["1"][0], vref_y))
    add_wire(schematic, cref["1"], (cref["1"][0], vref_y))
    add_junction(schematic, r2["1"][0], vref_y)
    add_junction(schematic, cref["1"][0], vref_y)
    add_label(schematic, "VREF_RAW", 91.44, vref_y)

    ground_y = max(r2["2"][1], cref["2"][1])
    add_wire(
        schematic,
        r2["2"],
        cref["2"],
        (cref["2"][0] + 7.62, ground_y),
    )
    add_junction(schematic, cref["2"][0], ground_y)
    add_label(schematic, "GND", cref["2"][0] + 7.62, ground_y)

    follower_right = u1a["1"][0] + 6.35
    follower_bottom = u1a["2"][1] + 7.62
    add_wire(
        schematic,
        u1a["1"],
        (follower_right, u1a["1"][1]),
        (follower_right, follower_bottom),
        (u1a["2"][0] - 5.08, follower_bottom),
        (u1a["2"][0] - 5.08, u1a["2"][1]),
        u1a["2"],
    )
    add_label(
        schematic,
        "VREF_BUFFERED",
        follower_right,
        u1a["1"][1],
    )

    # LM358 power pins and local supply decoupling.
    add_note(schematic, "OP AMP POWER", 169, 29, 1.15, True)
    u1c = add_instance(
        schematic,
        lm2904_symbol,
        "U1",
        "LM358N",
        "Package_DIP:DIP-8_W7.62mm",
        160.02,
        48.26,
        3,
    )
    cdec = add_instance(
        schematic,
        c_symbol,
        "CDEC",
        "100 nF",
        capacitor_fp,
        184.15,
        48.26,
        1,
    )
    add_wire(schematic, u1c["8"], (u1c["8"][0], u1c["8"][1] - 5.08))
    add_label(schematic, "+5V", u1c["8"][0], u1c["8"][1] - 5.08)
    add_wire(schematic, u1c["4"], (u1c["4"][0], u1c["4"][1] + 5.08))
    add_label(schematic, "GND", u1c["4"][0], u1c["4"][1] + 5.08)
    add_wire(schematic, cdec["1"], (cdec["1"][0], cdec["1"][1] - 5.08))
    add_label(schematic, "+5V", cdec["1"][0], cdec["1"][1] - 5.08)
    add_wire(schematic, cdec["2"], (cdec["2"][0], cdec["2"][1] + 5.08))
    add_label(schematic, "GND", cdec["2"][0], cdec["2"][1] + 5.08)

    for reference, net_name, x, y in (
        ("#FLG01", "+5V", 207.01, 40.64),
        ("#FLG02", "GND", 220.98, 40.64),
    ):
        flag = add_instance(
            schematic,
            power_flag_symbol,
            reference,
            "PWR_FLAG",
            "",
            x,
            y,
            1,
            on_board=False,
            hide_reference=True,
            hide_value=True,
        )
        add_label(schematic, net_name, flag["1"][0], flag["1"][1])

    # Reverse-biased LED source and AC coupling.
    add_note(schematic, "LED ENTROPY SOURCE AND AC COUPLING", 75, 84, 1.15, True)
    source_y = 101.60
    rled = add_instance(
        schematic,
        r_symbol,
        "RLED",
        "10 MOhm",
        resistor_fp,
        55.88,
        source_y,
        1,
        angle=90,
    )
    d1 = add_instance(
        schematic,
        led_symbol,
        "D1",
        "GREEN LED",
        "LED_THT:LED_D5.0mm",
        66.04,
        source_y + 3.81,
        1,
        angle=270,
    )
    cin = add_instance(
        schematic,
        c_symbol,
        "CIN",
        "100 nF",
        capacitor_fp,
        85.09,
        source_y,
        1,
        angle=90,
    )
    add_wire(schematic, (rled["1"][0] - 7.62, source_y), rled["1"])
    add_label(
        schematic,
        "+3V3",
        rled["1"][0] - 7.62,
        source_y,
        justify="right",
    )
    add_wire(schematic, rled["2"], cin["1"])
    add_wire(schematic, d1["1"], (d1["1"][0], source_y))
    add_junction(schematic, d1["1"][0], source_y)
    add_label(schematic, "SOURCE_NODE", 68.58, source_y)
    add_wire(schematic, d1["2"], (d1["2"][0], d1["2"][1] + 6.35))
    add_label(schematic, "GND", d1["2"][0], d1["2"][1] + 6.35)

    # U1B non-inverting gain stage, bias network and protected ADC output.
    add_note(schematic, "SIGNAL GAIN AND ADC OUTPUT", 164, 84, 1.15, True)
    u1b = add_instance(
        schematic,
        lm2904_symbol,
        "U1",
        "LM358N",
        "Package_DIP:DIP-8_W7.62mm",
        158.75,
        source_y,
        2,
    )
    rbias = add_instance(
        schematic,
        r_symbol,
        "RBIAS",
        "330 kOhm",
        resistor_fp,
        99.06,
        116.84,
        1,
    )
    rg = add_instance(
        schematic,
        r_symbol,
        "RG",
        "4.4 kOhm",
        resistor_fp,
        140.97,
        121.92,
        1,
        angle=270,
    )
    rf = add_instance(
        schematic,
        r_symbol,
        "RF",
        "330 kOhm",
        resistor_fp,
        175.26,
        121.92,
        1,
        angle=270,
    )
    rout = add_instance(
        schematic,
        r_symbol,
        "ROUT",
        "690 Ohm",
        resistor_fp,
        195.58,
        source_y,
        1,
        angle=90,
    )

    signal_corner_x = 139.70
    add_wire(
        schematic,
        cin["2"],
        (signal_corner_x, cin["2"][1]),
        (signal_corner_x, u1b["5"][1]),
        u1b["5"],
    )
    add_label(schematic, "SIGNAL_INPUT", 113.03, cin["2"][1])
    add_wire(
        schematic,
        (rbias["1"][0], cin["2"][1]),
        rbias["1"],
    )
    add_junction(schematic, rbias["1"][0], cin["2"][1])
    add_wire(
        schematic,
        rbias["2"],
        (rbias["2"][0], rbias["2"][1] + 5.08),
    )
    add_label(
        schematic,
        "VREF_BUFFERED",
        rbias["2"][0],
        rbias["2"][1] + 5.08,
    )

    feedback_y = rf["2"][1]
    add_wire(
        schematic,
        u1b["6"],
        (u1b["6"][0], feedback_y),
        rg["1"],
    )
    add_wire(schematic, (u1b["6"][0], feedback_y), rf["2"])
    add_junction(schematic, u1b["6"][0], feedback_y)
    add_label(schematic, "FEEDBACK", 153.67, feedback_y)
    add_wire(
        schematic,
        rg["2"],
        (rg["2"][0] - 6.35, rg["2"][1]),
    )
    add_label(
        schematic,
        "VREF_BUFFERED",
        rg["2"][0] - 6.35,
        rg["2"][1],
        justify="right",
    )

    output_branch_x = 182.88
    add_wire(schematic, u1b["7"], rout["1"])
    add_wire(
        schematic,
        (output_branch_x, source_y),
        (output_branch_x, feedback_y),
        rf["1"],
    )
    add_junction(schematic, output_branch_x, source_y)
    add_label(schematic, "AMP_OUT", 175.26, source_y)
    add_wire(
        schematic,
        rout["2"],
        (rout["2"][0] + 7.62, rout["2"][1]),
    )
    add_label(schematic, "A0", rout["2"][0] + 7.62, rout["2"][1])

    # Label-connected test points form a compact bring-up row.
    add_note(schematic, "BRING-UP TEST POINTS", 40, 140, 1.05, True)
    test_points = [
        ("TP1", "VREF_RAW", 52.07),
        ("TP2", "VREF_BUFFERED", 82.55),
        ("TP3", "SOURCE_NODE", 116.84),
        ("TP4", "SIGNAL_INPUT", 149.86),
        ("TP5", "AMP_OUT", 179.07),
        ("TP6", "A0", 203.20),
        ("TP7", "GND", 226.06),
    ]
    for reference, net_name, x in test_points:
        add_instance(
            schematic,
            testpoint_symbol,
            reference,
            net_name,
            testpoint_fp,
            x,
            148.59,
            1,
            {"1": net_name},
            hide_value=True,
        )

    add_note(
        schematic,
        "Nominal U1B gain about VREF: 1 + 330 kOhm / 4.4 kOhm = 76.",
        145,
        163,
        0.95,
    )
    add_note(
        schematic,
        "D1 cathode connects to SOURCE_NODE; its anode connects to GND.",
        145,
        168,
        0.95,
    )
    add_note(
        schematic,
        "Arduino AREF is intentionally disconnected. Verify rails before connecting A0.",
        145,
        173,
        0.95,
    )

    schematic.to_file(str(OUTPUT_PATH), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
