#include "simulation_assets/hud.hpp"
#include "simulation_assets/simulation_state.hpp"

#include "raylib.h"

namespace {

constexpr float kTabWidth = 100.0f;
constexpr float kTabHeight = 50.0f;
constexpr float kPanelX = 20.0f;
constexpr float kPanelY = 5.0f;
constexpr float kPanelWidth = kTabWidth * 5;
constexpr float kPanelHeight = 420.0f; // taller, to fit the Controls tab's long list
constexpr float kLineHeight = 22.0f;

constexpr float kStatsPanelHeight = 250.0f;
constexpr float kStatsPanelGap = 10.0f;

void getTabDrawing(int index, Rectangle& outRect)
{
    outRect = Rectangle{kPanelX + kTabWidth * index, kPanelY, kTabWidth, kTabHeight};
}

} // namespace

// ========== UPDATE SIM ===========
void updateHudInput(SimulationState& state)
{
    if (IsKeyPressed(KEY_TAB)) {
        state.hudVisible = !state.hudVisible;
    }
    if (!state.hudVisible) {
        return;
    }
    if (!IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) {
        return;
    }

    Vector2 mousePos = GetMousePosition();

    for (int i = 0; i < 5; ++i) {
        Rectangle tabRect;
        getTabDrawing(i, tabRect);
        if (CheckCollisionPointRec(mousePos, tabRect)) {
            state.activeHudTab = static_cast<HudTab>(i);
        }
    }
}

void drawHudPanel(const SimulationState& state)
{
    // CREDIT TO CLAUDE FOR CHOOSING COLOURS

    if (!state.hudVisible) {
        return;
    }

    // Background
    Rectangle panelRect {kPanelX, kPanelY + kTabHeight, kPanelWidth, kPanelHeight};
    DrawRectangleRounded(panelRect, 0.08f, 8, Fade(Color{28, 28, 32, 255}, 0.9f));
    DrawRectangleRoundedLines(panelRect, 0.08f, 8, Color{110, 110, 120, 255});

    // Tab titles
    const char* labels[5] = {"Controls", "Target", "Joints", "Pick/Place", "Debug"};
    for (int i = 0; i < 5; ++i) {
        Rectangle tabRect {kPanelX + kTabWidth * i, kPanelY, kTabWidth, kTabHeight};
        const bool isActive = static_cast<int>(state.activeHudTab) == i;
        DrawRectangleRounded(tabRect, 0.25f, 8, isActive ? Fade(Color{25, 25, 30, 255}, 0.95f) : Fade(Color{10, 10, 12, 255}, 0.85f));
        DrawRectangleRoundedLines(tabRect, 0.25f, 8, isActive ? Color{150, 150, 165, 255} : Color{60, 60, 68, 255});
        DrawTextEx(state.hudFont, labels[i], Vector2{tabRect.x + 6, tabRect.y + 6}, 18, 1.0f, isActive ? WHITE : Color{160, 160, 170, 255});
    }

    // =========================================== TAB CONTENT ==========================================
    constexpr float textX = kPanelX + 10.0f;
    float textY = kPanelY + kTabHeight + 10.0f;

    switch (state.activeHudTab) {
        case HudTab::Controls:
            DrawTextEx(state.hudFont, "Tab: toggle this HUD", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "WASD: move camera", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "Right-click + drag: rotate camera", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "Scroll: zoom camera", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "1-6: select joint", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "O/P: rotate selected joint", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "0: toggle target/IK mode", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "Arrows: move target X/Z", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "Q/E: move target height", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "L: toggle joint limits", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "C: cycle pathway shape", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "V: toggle pathway mode", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "H: return to home angles", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "-/=: target orientation, Y axis", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "[/]: target orientation, X axis", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "'/\\: target orientation, Z axis", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            break;

        case HudTab::TargetMode:
            DrawTextEx(state.hudFont, "Arrows/Q/E: move target", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "-/=/[/]/'/\\: rotate target orientation", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "0: toggle IK mode | H: return home", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight * 1.5f;
            DrawTextEx(state.hudFont, TextFormat("IK mode: %s", state.targetMode ? "ACTIVE" : "OFF"), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("Target: %.2f, %.2f, %.2f", state.targetPosition.x, state.targetPosition.y, state.targetPosition.z), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("IK speed: %.3f rad/step", state.ikSettings.maximumStepRadians), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("Error: %.4f", state.targetDistance), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("Pathway: %s (%s)", robot_arm::pathwayName(state.pathwayShape).data(), state.pathwayMode ? "ON" : "OFF"), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("Returning home: %s", state.returningHome ? "YES" : "NO"), Vector2{textX, textY}, 20, 1.0f, RAYWHITE);
            break;

        case HudTab::JointControl:
            DrawTextEx(state.hudFont, "1-6: select joint", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "O/P: rotate selected joint", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, "L: toggle joint limits", Vector2{textX, textY}, 18, 1.0f, RAYWHITE); textY += kLineHeight * 1.5f;
            DrawTextEx(state.hudFont, TextFormat("Selected joint: %d", static_cast<int>(state.selectedJoint + 1)), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("theta = %.1f deg", state.angles[state.selectedJoint] * RAD2DEG), Vector2{textX, textY}, 20, 1.0f, RAYWHITE); textY += kLineHeight;
            DrawTextEx(state.hudFont, TextFormat("Joint limits: %s", state.enforceJointLimits ? "ON" : "OFF"), Vector2{textX, textY}, 20, 1.0f, RAYWHITE);
            break;

        case HudTab::PickAndPlace:
            DrawTextEx(state.hudFont, "Pick & Place: not yet implemented", Vector2{textX, textY}, 20, 1.0f, RAYWHITE);
            break;

        case HudTab::Debug:
            break; // intentionally empty for now
    }
}

void drawStatsPanel(const SimulationState& state)
{
    if (!state.hudVisible) {
        return;
    }

    Rectangle statsRect {
        kPanelX,
        kPanelY + kTabHeight + kPanelHeight + kStatsPanelGap,
        kPanelWidth,
        kStatsPanelHeight};

    DrawRectangleRounded(statsRect, 0.06f, 8, Fade(Color{28, 28, 32, 255}, 0.9f));
    DrawRectangleRoundedLines(statsRect, 0.06f, 8, Color{110, 110, 120, 255});

    const float textX = statsRect.x + 10.0f;
    float textY = statsRect.y + 10.0f;

    for (std::size_t joint = 0; joint < robot_arm::kJointCount; ++joint) {
        DrawTextEx(state.hudFont, TextFormat("J%d: %.1f deg", static_cast<int>(joint + 1), state.angles[joint] * RAD2DEG), Vector2{textX, textY}, 16, 1.0f, RAYWHITE);
        textY += 20.0f;
    }

    textY += 4.0f;
    DrawTextEx(state.hudFont, TextFormat("Velocity: %.3f, %.3f, %.3f", state.endEffectorVelocity.x, state.endEffectorVelocity.y, state.endEffectorVelocity.z), Vector2{textX, textY}, 16, 1.0f, RAYWHITE);
    textY += 20.0f;
    DrawTextEx(state.hudFont, TextFormat("Target: %.2f, %.2f, %.2f", state.targetPosition.x, state.targetPosition.y, state.targetPosition.z), Vector2{textX, textY}, 16, 1.0f, RAYWHITE);
    textY += 20.0f;
    DrawTextEx(state.hudFont, TextFormat("Robot pos: %.2f, %.2f, %.2f", state.endEffectorPosition.x, state.endEffectorPosition.y, state.endEffectorPosition.z), Vector2{textX, textY}, 16, 1.0f, RAYWHITE);
    textY += 20.0f;
    DrawTextEx(state.hudFont, TextFormat("Render mode: %s", state.toggleRobotDesign ? "Simple" : "Detailed"), Vector2{textX, textY}, 16, 1.0f, RAYWHITE);
    textY += 20.0f;
    DrawTextEx(state.hudFont, TextFormat("Max reach: %.3f", state.maximumApproximateReach), Vector2{textX, textY}, 16, 1.0f, RAYWHITE);
}