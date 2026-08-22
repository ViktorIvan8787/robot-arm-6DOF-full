#include "simulation_assets/rendering.hpp"

#include <raylib.h>
#include <raymath.h>
#include <algorithm>

namespace {
// Flip Z-Y coordinates as raylib uses y as up on default but robot kinematics use z as up
Vector3 flipZY(Vector3 dhPos) {return {dhPos.x, dhPos.z, dhPos.y};}
} // namespace



// ==================================== GRIPPER ==========================================

void drawGripper(Vector3 tip, Matrix tipTransform) // Credit to Claude Sonnet 5 AI for the design (used for visual implementation)
{
    // Extract the gripper's true forward (approach) and sideways axes
    // directly from the accumulated joint transform, so claws follow
    // every joint's rotation, including roll/yaw at the wrist.
    Vector3 origin {0.0f, 0.0f, 0.0f};
    Vector3 localForward {0.0f, 0.0f, 1.0f};
    Vector3 localSideways {1.0f, 0.0f, 0.0f};

    Vector3 approachDirection = Vector3Normalize(
        Vector3Subtract(Vector3Transform(localForward, tipTransform), Vector3Transform(origin, tipTransform))
        );
    Vector3 sideways = Vector3Normalize(
        Vector3Subtract(Vector3Transform(localSideways, tipTransform), Vector3Transform(origin, tipTransform))
        );

    constexpr float hubRadius = 0.013f;         // was 0.01f
    constexpr float hubLength = 0.010f;         // was 0.008f

    constexpr float clawSpread = 0.015f;        // was 0.012f
    constexpr float clawBackOffset = 0.006f;    // was 0.005f
    constexpr float clawStraightLength = 0.034f; // was 0.028f
    constexpr float clawTipLength = 0.017f;      // was 0.014f
    constexpr float clawBaseRadius = 0.006f;     // was 0.005f
    constexpr float clawTipRadius = 0.003f;      // was 0.0025f
    constexpr float clawInwardBend = 0.007f;     // was 0.006f

    const Color pulleyRed {150, 35, 35, 255};
    const Color darkGreen {20, 70, 35, 255};
    const Color mediumDarkGreen {45, 115, 65, 255};

    // Small mounting hub where the claws attach, sitting just behind the tip.
    Vector3 hubCenter = Vector3Subtract(tip, Vector3Scale(approachDirection, clawBackOffset));
    Vector3 hubBack = Vector3Subtract(hubCenter, Vector3Scale(approachDirection, hubLength));
    DrawCylinderEx(flipZY(hubBack), flipZY(hubCenter), hubRadius, hubRadius * 0.8f, 20, darkGreen);

    // Two claws: straight section from the hub, then a shorter tapered tip bent inward.
    for (float side : {1.0f, -1.0f}) {
        Vector3 sideOffset = Vector3Scale(sideways, clawSpread * side);

        Vector3 clawStart = Vector3Add(hubCenter, sideOffset);
        Vector3 clawBend = Vector3Add(
            Vector3Add(hubCenter, Vector3Scale(approachDirection, clawStraightLength)),
            sideOffset);
        Vector3 clawTip = Vector3Add(
            Vector3Add(hubCenter, Vector3Scale(approachDirection, clawStraightLength + clawTipLength)),
            Vector3Scale(sideways, (clawSpread - clawInwardBend) * side)); // bends toward centre

        DrawCylinderEx(flipZY(clawStart), flipZY(clawBend), clawBaseRadius, clawBaseRadius * 0.6f, 12, pulleyRed);
        DrawCylinderEx(flipZY(clawBend), flipZY(clawTip), clawBaseRadius * 0.6f, clawTipRadius, 10, pulleyRed);
    }
}


// ==================================== ROBOT DESIGN ==========================================
// CREDIT TO ANTHROPIC CLAUDE AI (Sonnet 5) USED FOR VISUAL ROBOT DESIGN

namespace {
 
// Simple Robot

// Draws a small rotation-indicator dot on a joint sphere's surface, derived
// from the joint's actual current transform so it visibly spins with the
// joint in real time.
void drawRotationDot(Vector3 jointCenter, Matrix jointTransform, float sphereRadius, Vector3 localDirection, Color color)
{
    Vector3 origin {0.0f, 0.0f, 0.0f};
    Vector3 dotDirection = Vector3Normalize(Vector3Subtract(
        Vector3Transform(localDirection, jointTransform),
        Vector3Transform(origin, jointTransform)));
    Vector3 dotPosition = Vector3Add(jointCenter, Vector3Scale(dotDirection, sphereRadius * 1.02f));
    DrawSphere(dotPosition, sphereRadius * 0.22f, color);
}

void drawSimpleRobot(
    const SimulationState& state,
    const robot_arm::JointPositions& positions,
    const robot_arm::JointTransforms& transforms)
{
    BeginMode3D(state.camera);

    // Same floor/grid/target as the detailed mode, for consistency.
    constexpr float floorExtent = 40 * 0.05f / 2.0f;
    const Color floorBase {200, 200, 202, 255};
    DrawCube(Vector3{0.0f, -0.01f, 0.0f}, floorExtent * 2.0f, 0.004f, floorExtent * 2.0f, floorBase);
    DrawGrid(40, 0.05f);

    Vector3 targetDraw = flipZY(state.targetPosition);
    constexpr float crosshairSize = 0.03f;
    DrawSphere(targetDraw, 0.005f, RED);
    DrawLine3D(Vector3Subtract(targetDraw, Vector3{crosshairSize, 0, 0}), Vector3Add(targetDraw, Vector3{crosshairSize, 0, 0}), RED);
    DrawLine3D(Vector3Subtract(targetDraw, Vector3{0, crosshairSize, 0}), Vector3Add(targetDraw, Vector3{0, crosshairSize, 0}), RED);
    DrawLine3D(Vector3Subtract(targetDraw, Vector3{0, 0, crosshairSize}), Vector3Add(targetDraw, Vector3{0, 0, crosshairSize}), RED);

    // Simple base: a single dark cylinder, no detailing.
    Vector3 baseBottom = flipZY(Vector3{0.0f, 0.0f, 0.0f});
    Vector3 baseTop = flipZY(Vector3{0.0f, 0.0f, 0.195f});
    DrawCylinderEx(baseBottom, baseTop, 0.03f, 0.022f, 20, DARKGRAY);

    constexpr float sphereRadius = 0.017f;
    for (std::size_t joint = 0; joint < robot_arm::kJointCount; ++joint) {
        Vector3 start = flipZY(positions[joint]);
        Vector3 end = flipZY(positions[joint + 1]);

        // Thin link, stick-figure style.
        DrawCylinderEx(start, end, 0.006f, 0.006f, 12, GRAY);

        // Joint sphere.
        DrawSphere(start, sphereRadius, DARKGRAY);

        // Two small rotation-indicator dots, 180 degrees apart around the
        // joint's own local Z (rotation) axis, so they visibly track its
        // spin without cluttering the sphere.
        drawRotationDot(start, transforms[joint], sphereRadius, Vector3{1.0f, 0.0f, 0.0f}, RED);
        drawRotationDot(start, transforms[joint], sphereRadius, Vector3{-1.0f, 0.0f, 0.0f}, Color{255, 150, 150, 255});
    }

    DrawSphere(flipZY(positions.back()), 0.01f, WHITE);
    drawGripper(positions.back(), transforms.back());

    for (std::size_t index = 0; index + 1 < state.pathwayPoints.size(); ++index) {
        DrawLine3D(flipZY(state.pathwayPoints[index]), flipZY(state.pathwayPoints[index + 1]), Fade(GRAY, 0.5f));
    }
    for (std::size_t index = 0; index < state.pathwayPoints.size(); ++index) {
        const bool isCurrent = index == state.currentWaypoint;
        DrawSphere(
            flipZY(state.pathwayPoints[index]),
            isCurrent ? 0.022f : 0.01f,
            isCurrent ? YELLOW : Fade(GRAY, 0.6f));
    }

    EndMode3D();
}

// Complex robot

Color lerpColor(Color a, Color b, float t)
{
    return Color{
        static_cast<unsigned char>(a.r + (b.r - a.r) * t),
        static_cast<unsigned char>(a.g + (b.g - a.g) * t),
        static_cast<unsigned char>(a.b + (b.b - a.b) * t),
        255};
}

Color shadeByDirection(Color base, Vector3 surfaceDirection, Vector3 lightDirection, float minFactor, float maxFactor)
{
    const float alignment = Vector3DotProduct(Vector3Normalize(surfaceDirection), Vector3Normalize(lightDirection));
    const float factor = minFactor + (maxFactor - minFactor) * ((alignment + 1.0f) * 0.5f);
    return Color{
        static_cast<unsigned char>(std::clamp(base.r * factor, 0.0f, 255.0f)),
        static_cast<unsigned char>(std::clamp(base.g * factor, 0.0f, 255.0f)),
        static_cast<unsigned char>(std::clamp(base.b * factor, 0.0f, 255.0f)),
        255};
}

Color shadeFlat(Color base, float factor)
{
    return Color{
        static_cast<unsigned char>(std::clamp(base.r * factor, 0.0f, 255.0f)),
        static_cast<unsigned char>(std::clamp(base.g * factor, 0.0f, 255.0f)),
        static_cast<unsigned char>(std::clamp(base.b * factor, 0.0f, 255.0f)),
        255};
}

// A joint housing styled after the reference: twin dark-gray side walls
// sandwiching a large red pulley disc, with small blue bolts ringing the
// disc's face.
void drawJointHousing(Vector3 center, Vector3 axisDirection, float radius, Color bodyColor, bool showPulley)
{
    Vector3 axis = Vector3Normalize(axisDirection);
    Vector3 worldUp {0.0f, 1.0f, 0.0f};
    Vector3 sideways = Vector3CrossProduct(axis, worldUp);
    if (Vector3Length(sideways) < 0.001f) {
        sideways = Vector3CrossProduct(axis, Vector3{1.0f, 0.0f, 0.0f});
    }
    sideways = Vector3Normalize(sideways);
    Vector3 updir = Vector3Normalize(Vector3CrossProduct(sideways, axis));

    const float wallThickness = radius * 0.35f;
    const float wallGap = radius * 1.1f;

    Vector3 wallAOuter = Vector3Add(center, Vector3Scale(axis, wallGap * 0.5f + wallThickness));
    Vector3 wallAInner = Vector3Add(center, Vector3Scale(axis, wallGap * 0.5f));
    Vector3 wallBOuter = Vector3Subtract(center, Vector3Scale(axis, wallGap * 0.5f + wallThickness));
    Vector3 wallBInner = Vector3Subtract(center, Vector3Scale(axis, wallGap * 0.5f));

    // Twin dark-gray side walls (the "clamshell" housing).
    DrawCylinderEx(wallAOuter, wallAInner, radius, radius * 0.95f, 20, shadeFlat(bodyColor, 0.85f));
    DrawCylinderEx(wallBOuter, wallBInner, radius, radius * 0.95f, 20, shadeFlat(bodyColor, 0.85f));

    if (showPulley) {
        // Large red pulley disc sandwiched between the walls.
        const Color pulleyRed {150, 35, 35, 255};
        const float pulleyRadius = radius * 0.82f;
        DrawCylinderEx(wallAInner, wallBInner, pulleyRadius, pulleyRadius, 24, pulleyRed);
        DrawCylinderWiresEx(wallAInner, wallBInner, pulleyRadius, pulleyRadius, 24, shadeFlat(pulleyRed, 0.6f));

        // Small blue bolts ringing the pulley face.
        const Color boltBlue {45, 90, 150, 255};
        Vector3 discFace = Vector3Lerp(wallAInner, wallBInner, 0.5f);
        for (int i = 0; i < 6; ++i) {
            const float angle = (2.0f * PI * i) / 6.0f;
            Vector3 boltDir = Vector3Add(Vector3Scale(sideways, std::cos(angle)), Vector3Scale(updir, std::sin(angle)));
            Vector3 boltPos = Vector3Add(discFace, Vector3Scale(boltDir, pulleyRadius * 0.68f));
            DrawSphere(boltPos, radius * 0.1f, boltBlue);
        }
    }

    // A few visible "bolt" heads around the housing rim itself, dark gray.
    for (int i = 0; i < 8; ++i) {
        const float angle = (2.0f * PI * i) / 8.0f + 0.3f;
        Vector3 boltDir = Vector3Add(Vector3Scale(sideways, std::cos(angle)), Vector3Scale(updir, std::sin(angle)));
        Vector3 boltPos = Vector3Add(wallAOuter, Vector3Scale(boltDir, radius * 0.92f));
        DrawSphere(boltPos, radius * 0.06f, shadeFlat(bodyColor, 0.5f));
    }
}

// A boxy, paneled link section rather than a thin tube — closer to the
// reference's chunky housings.
void drawPaneledLink(Vector3 start, Vector3 end, float width, Color bodyColor, Vector3 lightDirection)
{
    Vector3 axis = Vector3Normalize(Vector3Subtract(end, start));
    Color shaded = shadeByDirection(bodyColor, axis, lightDirection, 0.7f, 1.15f);

    DrawCylinderEx(start, end, width, width * 0.92f, 16, shaded);

    // Panel seam lines for a manufactured look.
    Vector3 mid = Vector3Lerp(start, end, 0.5f);
    DrawCylinderWiresEx(
        Vector3Subtract(mid, Vector3Scale(axis, 0.002f)),
        Vector3Add(mid, Vector3Scale(axis, 0.002f)),
        width * 1.02f, width * 1.0f, 16, shadeFlat(bodyColor, 0.5f));
}

} // namespace

void drawRobot(
    const SimulationState& state,
    const robot_arm::JointPositions& positions,
    const robot_arm::JointTransforms& transforms)
{
    // SIMPLE ROBOT DESING TOGGLE <--------------------------
    if (state.toggleRobotDesign) {
        drawSimpleRobot(state, positions, transforms);
        return;
    }

    // ========= DRAWING  ==========
    BeginMode3D(state.camera);

    const Vector3 lightDirection = Vector3Normalize(Vector3{0.4f, 1.0f, 0.3f});

    // Gray shaded floor.
    constexpr float floorExtent = 40 * 0.05f / 2.0f;
    const Color floorBase {200, 200, 202, 255};  // light warm-neutral gray, not pure white
    DrawCube(Vector3{0.0f, -0.01f, 0.0f}, floorExtent * 2.0f, 0.004f, floorExtent * 2.0f, shadeFlat(floorBase, 1.0f));
    DrawCube(Vector3{0.0f, -0.008f, 0.0f}, floorExtent * 1.94f, 0.002f, floorExtent * 1.94f, shadeFlat(floorBase, 0.85f));

    DrawGrid(40, 0.05f);

    // Target crosshair.
    Vector3 targetDraw = flipZY(state.targetPosition);
    constexpr float crosshairSize = 0.03f;
    DrawSphere(targetDraw, 0.005f, RED);
    DrawLine3D(Vector3Subtract(targetDraw, Vector3{crosshairSize, 0, 0}), Vector3Add(targetDraw, Vector3{crosshairSize, 0, 0}), RED);
    DrawLine3D(Vector3Subtract(targetDraw, Vector3{0, crosshairSize, 0}), Vector3Add(targetDraw, Vector3{0, crosshairSize, 0}), RED);
    DrawLine3D(Vector3Subtract(targetDraw, Vector3{0, 0, crosshairSize}), Vector3Add(targetDraw, Vector3{0, 0, crosshairSize}), RED);

    // Base: wide stepped housing with a red accent ring, matching the
    // reference's base disc.
    const Color bodyDark {68, 68, 72, 255};
    const Color bodyLight {150, 150, 155, 255}; // lighter gray for wrist/gripper section
    const Color accentRed {150, 35, 35, 255};

    Vector3 baseBottom = flipZY(Vector3{0.0f, 0.0f, 0.0f});
    Vector3 baseFootTop = flipZY(Vector3{0.0f, 0.0f, 0.03f});
    Vector3 baseRingTop = flipZY(Vector3{0.0f, 0.0f, 0.045f});
    Vector3 baseBodyTop = flipZY(Vector3{0.0f, 0.0f, 0.17f});
    Vector3 baseCollarTop = flipZY(Vector3{0.0f, 0.0f, 0.195f});

    DrawCylinderEx(baseBottom, baseFootTop, 0.05f, 0.048f, 8, shadeFlat(bodyDark, 0.85f)); // slightly boxy (8 sides)
    DrawCylinderEx(baseFootTop, baseRingTop, 0.046f, 0.046f, 30, accentRed); // red accent ring
    DrawCylinderEx(baseRingTop, baseBodyTop, 0.042f, 0.03f, 8, shadeFlat(bodyDark, 1.0f));
    DrawCylinderEx(baseBodyTop, baseCollarTop, 0.026f, 0.024f, 20, shadeFlat(bodyDark, 0.8f));

    // Base corner bolts for the industrial look.
    for (int i = 0; i < 4; ++i) {
        const float angle = (2.0f * PI * i) / 4.0f + PI / 4.0f;
        Vector3 boltPos = Vector3Add(baseBottom, Vector3{0.045f * std::cos(angle), 0.001f, 0.045f * std::sin(angle)});
        DrawSphere(boltPos, 0.004f, shadeFlat(bodyDark, 0.4f));
    }

    for (std::size_t joint = 0; joint < robot_arm::kJointCount; ++joint) {
        Vector3 start = flipZY(positions[joint]);
        Vector3 end = flipZY(positions[joint + 1]);
        Vector3 linkDirection = Vector3Subtract(end, start);

        // Wrist joints (4, 5) and gripper mount use the lighter body color,
        // matching the reference's distinct end-section shade.
        const bool isWristSection = joint >= 3;
        Color sectionColor = isWristSection ? bodyLight : bodyDark;

        const float linkWidth = isWristSection ? 0.014f : 0.020f - 0.002f * static_cast<float>(joint);

        drawPaneledLink(start, end, linkWidth, sectionColor, lightDirection);

        // Joint housing: big pulley discs on the main shoulder/elbow
        // joints (0-2), smaller plain housings on the wrist.
        const float jointRadius = isWristSection ? 0.016f : 0.026f - 0.002f * static_cast<float>(joint);
        const bool showPulley = joint <= 2;
        drawJointHousing(start, linkDirection, jointRadius, sectionColor, showPulley);
    }

    // End effector mounting plate.
    Vector3 tipPosition = flipZY(positions.back());
    Matrix tipTransform = transforms.back();
    Vector3 tipForward = Vector3Normalize(Vector3Subtract(
        Vector3Transform(Vector3{0.0f, 0.0f, 1.0f}, tipTransform),
        Vector3Transform(Vector3{0.0f, 0.0f, 0.0f}, tipTransform)));
    Vector3 mountPlateBack = Vector3Subtract(tipPosition, Vector3Scale(tipForward, 0.004f));
    Vector3 mountPlateFront = Vector3Add(tipPosition, Vector3Scale(tipForward, 0.001f));
    DrawCube(Vector3Lerp(mountPlateBack, mountPlateFront, 0.5f), 0.02f, 0.02f, 0.005f, shadeFlat(bodyLight, 0.9f));

    drawGripper(positions.back(), transforms.back());

    // Pathway trajectory.
    for (std::size_t index = 0; index + 1 < state.pathwayPoints.size(); ++index) {
        DrawLine3D(flipZY(state.pathwayPoints[index]), flipZY(state.pathwayPoints[index + 1]), Fade(GRAY, 0.5f));
    }
    for (std::size_t index = 0; index < state.pathwayPoints.size(); ++index) {
        const bool isCurrent = index == state.currentWaypoint;
        DrawSphere(
            flipZY(state.pathwayPoints[index]),
            isCurrent ? 0.022f : 0.01f,
            isCurrent ? YELLOW : Fade(GRAY, 0.6f));
    }

    EndMode3D();
}



