#pragma once

struct SimulationState; // Forward decleration

enum class HudTab {
    Controls,
    TargetMode,
    JointControl,
    PickAndPlace,
    Debug
};

void drawHudPanel(const SimulationState& state);
void drawStatsPanel(const SimulationState& state);
void updateHudInput(SimulationState& state);