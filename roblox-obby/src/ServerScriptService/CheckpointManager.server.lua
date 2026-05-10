local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))
local Events = ReplicatedStorage:WaitForChild("Events")
local CheckpointReached = Events:WaitForChild("CheckpointReached")

-- Maps player -> { stage = number, lastCheckpointTime = number }
local playerData = {}

local function getCheckpoints()
    return workspace:WaitForChild("Checkpoints"):GetChildren()
end

local function onPlayerAdded(player)
    playerData[player] = { stage = 1, lastCheckpointTime = 0 }

    player.CharacterAdded:Connect(function(character)
        local humanoidRootPart = character:WaitForChild("HumanoidRootPart")
        local data = playerData[player]
        if data then
            local stageConfig = GameConfig.STAGES[data.stage]
            if stageConfig then
                task.wait(0.1)
                humanoidRootPart.CFrame = CFrame.new(stageConfig.spawnPosition)
            end
        end
    end)
end

local function onPlayerRemoving(player)
    playerData[player] = nil
end

-- Touch detection for each checkpoint part
local function setupCheckpoint(checkpoint)
    local stageNumber = tonumber(checkpoint.Name:match("%d+"))
    if not stageNumber then return end

    checkpoint.Touched:Connect(function(hit)
        local character = hit.Parent
        local player = Players:GetPlayerFromCharacter(character)
        if not player then return end

        local data = playerData[player]
        if not data then return end

        local now = tick()
        if now - data.lastCheckpointTime < GameConfig.CHECKPOINT_COOLDOWN then return end

        -- Only advance forward, never back
        if stageNumber > data.stage then
            data.stage = stageNumber
            data.lastCheckpointTime = now
            CheckpointReached:FireClient(player, stageNumber, GameConfig.STAGES[stageNumber])
        end
    end)
end

-- Build the checkpoint parts in Workspace if they don't already exist
local function buildCheckpoints()
    local checkpointsFolder = workspace:WaitForChild("Checkpoints")

    for i, stageConfig in ipairs(GameConfig.STAGES) do
        local existing = checkpointsFolder:FindFirstChild("Checkpoint" .. i)
        if not existing then
            local part = Instance.new("Part")
            part.Name = "Checkpoint" .. i
            part.Size = Vector3.new(14, 8, 2)
            part.CFrame = CFrame.new(stageConfig.spawnPosition + Vector3.new(-10, 0, 0))
            part.Anchored = true
            part.CanCollide = false
            part.Transparency = 0.5
            part.BrickColor = BrickColor.new(stageConfig.checkpointColor)
            part.Material = Enum.Material.Neon

            local billboard = Instance.new("BillboardGui", part)
            billboard.Size = UDim2.new(0, 200, 0, 50)
            billboard.StudsOffset = Vector3.new(0, 5, 0)
            billboard.AlwaysOnTop = false
            local label = Instance.new("TextLabel", billboard)
            label.Size = UDim2.fromScale(1, 1)
            label.BackgroundTransparency = 1
            label.Text = stageConfig.name
            label.TextColor3 = Color3.new(1, 1, 1)
            label.TextScaled = true
            label.Font = Enum.Font.GothamBold

            part.Parent = checkpointsFolder
            setupCheckpoint(part)
        else
            setupCheckpoint(existing)
        end
    end
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)

for _, player in Players:GetPlayers() do
    onPlayerAdded(player)
end

buildCheckpoints()
