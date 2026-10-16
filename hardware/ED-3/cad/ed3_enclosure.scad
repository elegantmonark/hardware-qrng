/*
ED-3 parametric perfboard enclosure
Author: Trishan Biswas
Created: 16 October 2026

The enclosure holds one 89 mm by 52 mm perfboard and routes the five-wire
Arduino harness through a single side opening. Dimensions are in millimetres.

Set part to "base", "lid", "assembled" or "layout" before rendering.
The default layout places both printable parts on the build plane.
*/

$fn = 64;

part = "layout";
// Numeric override for command-line exports where shell quoting is awkward:
// 0 = base, 1 = lid, 2 = assembled preview, 3 = print layout.
part_id = -1;

// Measured board envelope.
board_length = 89;
board_width = 52;
board_thickness = 1.6;

// Enclosure sizing.
board_side_clearance = 8;
internal_height = 65;       // 2.56 inches from floor to lid underside.
wall = 2.4;
floor_thickness = 3;
lid_top_thickness = 3;
outer_corner_radius = 6;

// Board support and restraint.
support_height = 8;
support_rail_width = 3;
corner_guide_thickness = 2;
corner_guide_length = 12;
corner_guide_above_board = 4;

// Lid fit. Increase this if the first print is too tight.
lid_clearance_per_side = 0.35;
lid_lip_depth = 6;
lid_lip_wall = 1.8;

// Five-wire Arduino harness: 5 V, 3.3 V, GND, A0 and D7.
cable_slot_width = 26;
cable_slot_height = 12;
cable_slot_floor = floor_thickness + support_height - 1;

// Derived dimensions.
inner_length = board_length + 2 * board_side_clearance;
inner_width = board_width + 2 * board_side_clearance;
outer_length = inner_length + 2 * wall;
outer_width = inner_width + 2 * wall;
base_height = floor_thickness + internal_height;

board_x = wall + board_side_clearance;
board_y = wall + board_side_clearance;
board_z = floor_thickness + support_height;

module rounded_rectangle(size_x, size_y, radius) {
    hull() {
        translate([radius, radius]) circle(r = radius);
        translate([size_x - radius, radius]) circle(r = radius);
        translate([radius, size_y - radius]) circle(r = radius);
        translate([size_x - radius, size_y - radius]) circle(r = radius);
    }
}

module rounded_prism(size_x, size_y, height, radius) {
    linear_extrude(height = height)
        rounded_rectangle(size_x, size_y, radius);
}

module base_shell() {
    difference() {
        rounded_prism(
            outer_length,
            outer_width,
            base_height,
            outer_corner_radius
        );

        // Main internal cavity. Extending the cut above the body leaves an
        // open top while retaining the specified floor thickness.
        translate([wall, wall, floor_thickness])
            rounded_prism(
                inner_length,
                inner_width,
                internal_height + 1,
                max(outer_corner_radius - wall, 1)
            );

        // One bundle opening on the Arduino-facing short wall. It is wide
        // enough for five individual Dupont-style leads or a sleeved bundle.
        translate([
            outer_length - wall - 1,
            (outer_width - cable_slot_width) / 2,
            cable_slot_floor
        ])
            cube([
                wall + 2,
                cable_slot_width,
                cable_slot_height
            ]);

        // Two shallow thumb notches make the friction-fit lid easier to lift.
        translate([-1, outer_width / 2, base_height])
            rotate([0, 90, 0])
                cylinder(h = wall + 2, r = 8);
        translate([outer_length - wall - 1, outer_width / 2, base_height])
            rotate([0, 90, 0])
                cylinder(h = wall + 2, r = 8);
    }
}

module support_rails() {
    // Two rails support the long edges without relying on mounting-hole
    // positions. They also leave an air gap beneath the perfboard.
    for (rail_y = [
        board_y + 2,
        board_y + board_width - support_rail_width - 2
    ]) {
        translate([
            board_x + 3,
            rail_y,
            floor_thickness - 0.1
        ])
            cube([
                board_length - 6,
                support_rail_width,
                support_height + 0.1
            ]);
    }
}

module corner_guide(x_side, y_side) {
    guide_height = support_height + board_thickness + corner_guide_above_board;
    x0 = x_side == 0
        ? board_x - corner_guide_thickness
        : board_x + board_length;
    y0 = y_side == 0
        ? board_y - corner_guide_thickness
        : board_y + board_width;
    x_arm = x_side == 0
        ? board_x - corner_guide_thickness
        : board_x + board_length - corner_guide_length;
    y_arm = y_side == 0
        ? board_y - corner_guide_thickness
        : board_y + board_width - corner_guide_length;

    // The L-shaped guides stop lateral movement while leaving the board free
    // to lift out during development.
    translate([x0, y_arm, floor_thickness - 0.1])
        cube([
            corner_guide_thickness,
            corner_guide_length + corner_guide_thickness,
            guide_height + 0.1
        ]);

    translate([x_arm, y0, floor_thickness - 0.1])
        cube([
            corner_guide_length + corner_guide_thickness,
            corner_guide_thickness,
            guide_height + 0.1
        ]);
}

module base() {
    union() {
        base_shell();
        support_rails();
        for (x_side = [0, 1])
            for (y_side = [0, 1])
                corner_guide(x_side, y_side);
    }
}

module lid() {
    lip_outer_length = inner_length - 2 * lid_clearance_per_side;
    lip_outer_width = inner_width - 2 * lid_clearance_per_side;
    lip_radius = max(outer_corner_radius - wall - lid_clearance_per_side, 1);

    union() {
        // Print this outer face directly on the build plate. The locating lip
        // rises above it and faces into the enclosure after assembly.
        rounded_prism(
            outer_length,
            outer_width,
            lid_top_thickness,
            outer_corner_radius
        );

        translate([
            wall + lid_clearance_per_side,
            wall + lid_clearance_per_side,
            lid_top_thickness - 0.1
        ])
            difference() {
                rounded_prism(
                    lip_outer_length,
                    lip_outer_width,
                    lid_lip_depth + 0.1,
                    lip_radius
                );
                translate([lid_lip_wall, lid_lip_wall, -0.1])
                    rounded_prism(
                        lip_outer_length - 2 * lid_lip_wall,
                        lip_outer_width - 2 * lid_lip_wall,
                        lid_lip_depth + 0.3,
                        max(lip_radius - lid_lip_wall, 0.8)
                    );
            }
    }
}

module board_preview() {
    color([0.12, 0.48, 0.22, 0.65])
        translate([board_x, board_y, board_z])
            cube([board_length, board_width, board_thickness]);
}

module assembled_preview() {
    color([0.82, 0.84, 0.88]) base();
    board_preview();

    // The lid is shown transparent and flipped into its assembled position.
    color([0.65, 0.72, 0.82, 0.35])
        translate([0, outer_width, base_height + lid_top_thickness])
            rotate([180, 0, 0])
                lid();
}

selected_part = part_id == 0 ? "base"
    : part_id == 1 ? "lid"
    : part_id == 2 ? "assembled"
    : part_id == 3 ? "layout"
    : part;

if (selected_part == "base") {
    base();
} else if (selected_part == "lid") {
    lid();
} else if (selected_part == "assembled") {
    assembled_preview();
} else {
    base();
    translate([outer_length + 15, 0, 0]) lid();
}
