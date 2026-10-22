"""Generate the ED-4 placement-only perfboard draft in KiCad.

Run this with KiCad's bundled Python interpreter so the pcbnew module and the
installed KiCad footprint libraries are available. The electrical topology is
the proposed ED-3 buffered-reference circuit. ED-4 remains a mechanical and
placement prototype until ED-3 has been electrically validated.
"""

from pathlib import Path

import pcbnew


PROJECT_NAME = "ED4_Perfboard_Prototype"
OUTPUT_DIR = Path(__file__).resolve().parent
BOARD_PATH = OUTPUT_DIR / f"{PROJECT_NAME}.kicad_pcb"
KICAD_FOOTPRINT_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")

MM = pcbnew.FromMM
PITCH = 2.54
BOARD_X = 20.0
BOARD_Y = 20.0
BOARD_W = 89.0
BOARD_H = 52.0
GRID_X = BOARD_X + (BOARD_W - 34 * PITCH) / 2
GRID_Y = BOARD_Y + (BOARD_H - 19 * PITCH) / 2


def point(x_mm: float, y_mm: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(MM(x_mm), MM(y_mm))


def grid(column: int, row: int) -> pcbnew.VECTOR2I:
    return point(GRID_X + column * PITCH, GRID_Y + row * PITCH)


def add_line(board, start, end, layer, width=0.3):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(start)
    shape.SetEnd(end)
    shape.SetLayer(layer)
    shape.SetWidth(MM(width))
    board.Add(shape)


def add_text(board, text, position, size=1.3, layer=pcbnew.F_SilkS, thickness=0.22):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(position)
    item.SetLayer(layer)
    item.SetTextSize(point(size, size))
    item.SetTextThickness(MM(thickness))
    board.Add(item)
    return item


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def load_footprint(board, library, name, reference, value, location, nets, rotation=0):
    library_path = KICAD_FOOTPRINT_ROOT / f"{library}.pretty"
    footprint = pcbnew.FootprintLoad(str(library_path), name)
    if footprint is None:
        raise RuntimeError(f"Could not load {library}:{name}")

    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetPosition(location)
    footprint.SetOrientationDegrees(rotation)
    board.Add(footprint)
    footprint.Reference().SetVisible(False)
    footprint.Value().SetVisible(False)

    for pad in footprint.Pads():
        number = str(pad.GetNumber())
        if number in nets:
            pad.SetNet(nets[number])

    return footprint


def add_test_point(board, reference, value, location, net):
    return load_footprint(
        board,
        "TestPoint",
        "TestPoint_THTPad_D2.0mm_Drill1.0mm",
        reference,
        value,
        location,
        {"1": net},
    )


def add_perfboard_grid(board, occupied_positions):
    """Add independent 2.54 mm copper pads wherever a component pad is absent."""
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference("GRID1")
    footprint.SetValue("89x52 mm perfboard, 2.54 mm pitch")
    footprint.SetPosition(point(0, 0))
    footprint.Reference().SetVisible(False)
    footprint.Value().SetVisible(False)

    for column in range(35):
        for row in range(20):
            location = grid(column, row)
            if any(
                abs(location.x - occupied.x) < MM(0.25)
                and abs(location.y - occupied.y) < MM(0.25)
                for occupied in occupied_positions
            ):
                continue

            pad = pcbnew.PAD(footprint)
            pad.SetNumber("")
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            pad.SetSize(point(1.8, 1.8))
            pad.SetDrillSize(point(1.0, 1.0))
            pad.SetLayerSet(pad.PTHMask())
            pad.SetPosition(location)
            footprint.Add(pad)

    board.Add(footprint)


def main():
    board = pcbnew.BOARD()

    title = board.GetTitleBlock()
    title.SetTitle("ED-4 QRNG perfboard prototype")
    title.SetDate("2026-10-22")
    title.SetCompany("Trishan Biswas")
    title.SetComment(0, "Placement draft based on the unverified ED-3 topology")
    title.SetComment(1, "89 x 52 mm perfboard, 2.54 mm hole pitch")

    nets = {
        name: add_net(board, name)
        for name in (
            "+5V",
            "+3V3",
            "GND",
            "VREF_RAW",
            "VREF_BUFFERED",
            "SOURCE_NODE",
            "SIGNAL_INPUT",
            "FEEDBACK",
            "AMP_OUT",
            "A0",
        )
    }

    # Board outline.
    corners = [
        point(BOARD_X, BOARD_Y),
        point(BOARD_X + BOARD_W, BOARD_Y),
        point(BOARD_X + BOARD_W, BOARD_Y + BOARD_H),
        point(BOARD_X, BOARD_Y + BOARD_H),
    ]
    for index in range(4):
        add_line(board, corners[index], corners[(index + 1) % 4], pcbnew.Edge_Cuts, 0.5)

    footprints = []

    # Four-wire Arduino harness: 5 V, 3.3 V, ground and protected A0 output.
    footprints.append(
        load_footprint(
            board,
            "Connector_PinHeader_2.54mm",
            "PinHeader_1x04_P2.54mm_Vertical",
            "J1",
            "ARDUINO",
            grid(1, 3),
            {"1": nets["+5V"], "2": nets["+3V3"], "3": nets["GND"], "4": nets["A0"]},
        )
    )

    # Midpoint reference and decoupling.
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
            "R1",
            "10 kOhm",
            grid(4, 2),
            {"1": nets["+5V"], "2": nets["VREF_RAW"]},
        )
    )
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
            "R2",
            "10 kOhm",
            grid(4, 7),
            {"1": nets["VREF_RAW"], "2": nets["GND"]},
        )
    )
    footprints.append(
        load_footprint(
            board,
            "Capacitor_THT",
            "CP_Radial_D5.0mm_P2.50mm",
            "CREF",
            "10 uF",
            grid(10, 3),
            {"1": nets["VREF_RAW"], "2": nets["GND"]},
            90,
        )
    )

    # LM358: unit A buffers VREF, unit B is the signal gain stage.
    footprints.append(
        load_footprint(
            board,
            "Package_DIP",
            "DIP-8_W7.62mm",
            "U1",
            "LM358N",
            grid(14, 6),
            {
                "1": nets["VREF_BUFFERED"],
                "2": nets["VREF_BUFFERED"],
                "3": nets["VREF_RAW"],
                "4": nets["GND"],
                "5": nets["SIGNAL_INPUT"],
                "6": nets["FEEDBACK"],
                "7": nets["AMP_OUT"],
                "8": nets["+5V"],
            },
        )
    )
    footprints.append(
        load_footprint(
            board,
            "Capacitor_THT",
            "C_Disc_D5.0mm_W2.5mm_P2.50mm",
            "CDEC",
            "100 nF",
            grid(17, 3),
            {"1": nets["+5V"], "2": nets["GND"]},
            90,
        )
    )

    # Reverse-biased green LED source and AC coupling.
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal",
            "RLED",
            "10 MOhm",
            grid(23, 2),
            {"1": nets["+3V3"], "2": nets["SOURCE_NODE"]},
        )
    )
    source_led = load_footprint(
        board,
        "LED_THT",
        "LED_D5.0mm",
        "D1",
        "GREEN SOURCE LED",
        grid(29, 5),
        {"1": nets["SOURCE_NODE"], "2": nets["GND"]},
        90,
    )
    source_led.Models()[0].m_Filename = (
        "${KICAD10_3DMODEL_DIR}/LED_THT.3dshapes/LED_D5.0mm_Green.step"
    )
    footprints.append(source_led)
    footprints.append(
        load_footprint(
            board,
            "Capacitor_THT",
            "C_Disc_D5.0mm_W2.5mm_P2.50mm",
            "CIN",
            "100 nF",
            grid(24, 7),
            {"1": nets["SOURCE_NODE"], "2": nets["SIGNAL_INPUT"]},
            90,
        )
    )

    # Bias, gain and protected output components.
    resistor = "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            resistor,
            "RBIAS",
            "330 kOhm",
            grid(23, 10),
            {"1": nets["SIGNAL_INPUT"], "2": nets["VREF_BUFFERED"]},
        )
    )
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            resistor,
            "RF",
            "330 kOhm",
            grid(23, 13),
            {"1": nets["AMP_OUT"], "2": nets["FEEDBACK"]},
        )
    )
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            resistor,
            "RG",
            "4.4 kOhm",
            grid(23, 16),
            {"1": nets["FEEDBACK"], "2": nets["VREF_BUFFERED"]},
        )
    )
    footprints.append(
        load_footprint(
            board,
            "Resistor_THT",
            resistor,
            "ROUT",
            "690 Ohm",
            grid(4, 15),
            {"1": nets["AMP_OUT"], "2": nets["A0"]},
        )
    )

    # Accessible bring-up points. These are deliberate because ED-4 must be
    # checked electrically before any ADC dataset is treated as meaningful.
    test_points = [
        ("TP1", "VREF RAW", 11, 11, "VREF_RAW"),
        ("TP2", "VREF BUFFERED", 11, 14, "VREF_BUFFERED"),
        ("TP3", "SOURCE", 31, 9, "SOURCE_NODE"),
        ("TP4", "SIGNAL INPUT", 20, 11, "SIGNAL_INPUT"),
        ("TP5", "AMP OUTPUT", 20, 14, "AMP_OUT"),
        ("TP6", "A0", 11, 17, "A0"),
        ("TP7", "GND", 2, 17, "GND"),
    ]
    for reference, value, column, row, net_name in test_points:
        footprints.append(add_test_point(board, reference, value, grid(column, row), nets[net_name]))

    occupied = [pad.GetPosition() for footprint in footprints for pad in footprint.Pads()]
    add_perfboard_grid(board, occupied)

    # Compact labels are placed manually so the documentation render remains
    # readable on a dense 89 by 52 mm board.
    labels = [
        ("J1", 24.0, 26.0, 0.8),
        ("R1", 36.5, 24.3, 0.8),
        ("R2", 36.5, 36.8, 0.8),
        ("CREF", 48.0, 24.5, 0.8),
        ("CDEC", 66.0, 24.5, 0.8),
        ("U1 LM358N", 60.5, 33.0, 0.85),
        ("RLED", 84.8, 24.3, 0.8),
        ("D1", 96.3, 29.0, 0.8),
        ("CIN", 83.5, 35.3, 0.8),
        ("RBIAS", 84.8, 43.6, 0.8),
        ("RF", 84.8, 51.2, 0.8),
        ("RG", 84.8, 58.8, 0.8),
        ("ROUT", 36.5, 56.3, 0.8),
        ("TP1", 49.3, 48.6, 0.7),
        ("TP2", 49.3, 56.2, 0.7),
        ("TP3", 100.1, 43.5, 0.7),
        ("TP4", 72.1, 48.6, 0.7),
        ("TP5", 72.1, 56.2, 0.7),
        ("TP6", 49.3, 63.8, 0.7),
        ("TP7", 26.4, 63.8, 0.7),
        ("ED-4 DRAFT", 64.5, 68.5, 0.85),
    ]
    for label, x_mm, y_mm, size in labels:
        add_text(board, label, point(x_mm, y_mm), size)

    add_text(board, "5V", point(27.0, 29.5), 0.7)
    add_text(board, "3V3", point(27.0, 32.0), 0.7)
    add_text(board, "GND", point(27.0, 34.6), 0.7)
    add_text(board, "A0", point(27.0, 37.1), 0.7)

    # Dashed-looking zone dividers made from short segments on User.Drawings.
    for column in (12, 21):
        x = GRID_X + column * PITCH
        for row in range(0, 19, 2):
            y1 = GRID_Y + row * PITCH
            y2 = min(y1 + PITCH, GRID_Y + 19 * PITCH)
            add_line(board, point(x, y1), point(x, y2), pcbnew.Dwgs_User, 0.25)

    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(BOARD_PATH)


if __name__ == "__main__":
    main()
