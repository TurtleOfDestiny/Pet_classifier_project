-- Shared configuration for the obby game
local GameConfig = {}

GameConfig.STAGES = {
    {
        name = "Stage 1 - The Beginning",
        checkpointColor = Color3.fromRGB(0, 255, 0),
        spawnPosition = Vector3.new(0, 5, 0),
    },
    {
        name = "Stage 2 - Moving Platforms",
        checkpointColor = Color3.fromRGB(0, 100, 255),
        spawnPosition = Vector3.new(100, 5, 0),
    },
    {
        name = "Stage 3 - Lava Floor",
        checkpointColor = Color3.fromRGB(255, 165, 0),
        spawnPosition = Vector3.new(200, 5, 0),
    },
    {
        name = "Stage 4 - Spinning Blades",
        checkpointColor = Color3.fromRGB(255, 0, 100),
        spawnPosition = Vector3.new(300, 5, 0),
    },
    {
        name = "Stage 5 - The Finale",
        checkpointColor = Color3.fromRGB(255, 215, 0),
        spawnPosition = Vector3.new(400, 5, 0),
    },
}

GameConfig.RESPAWN_TIME = 3
GameConfig.CHECKPOINT_COOLDOWN = 1

return GameConfig
