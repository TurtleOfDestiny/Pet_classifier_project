local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local GameConfig = require(ReplicatedStorage:WaitForChild("GameConfig"))

-- ──────────────────────────────────────────────
--  Helpers
-- ──────────────────────────────────────────────

local function makePart(name, size, cframe, color, material, anchored, canCollide)
    local p = Instance.new("Part")
    p.Name = name
    p.Size = size
    p.CFrame = cframe
    p.BrickColor = BrickColor.new(color)
    p.Material = material or Enum.Material.SmoothPlastic
    p.Anchored = anchored ~= false
    p.CanCollide = canCollide ~= false
    return p
end

local function killOnTouch(part)
    part.Touched:Connect(function(hit)
        local character = hit.Parent
        local humanoid = character:FindFirstChildOfClass("Humanoid")
        if humanoid then humanoid.Health = 0 end
    end)
end

-- ──────────────────────────────────────────────
--  Stage builders
-- ──────────────────────────────────────────────

local function buildStage1(folder, origin)
    -- Simple stepping-stone path
    local positions = {
        Vector3.new(0, 0, 0),
        Vector3.new(0, 0, 8),
        Vector3.new(4, 2, 14),
        Vector3.new(0, 4, 22),
        Vector3.new(-4, 6, 28),
        Vector3.new(0, 8, 36),
        Vector3.new(0, 10, 44),
    }
    for i, pos in ipairs(positions) do
        local p = makePart("Stone" .. i, Vector3.new(6, 1, 6),
            CFrame.new(origin + pos), "Medium stone grey")
        p.Parent = folder
    end

    -- Spawn pad
    local spawn = makePart("SpawnPad", Vector3.new(14, 1, 14),
        CFrame.new(origin + Vector3.new(0, -0.5, -6)), "Bright green")
    spawn.Parent = folder
end

local function buildStage2(folder, origin)
    -- Moving platforms using TweenService
    local platformData = {
        { pos = Vector3.new(0, 0, 10),  travel = Vector3.new(12, 0, 0), duration = 2.5 },
        { pos = Vector3.new(0, 3, 20),  travel = Vector3.new(0, 8, 0),  duration = 2 },
        { pos = Vector3.new(0, 6, 30),  travel = Vector3.new(-10, 0, 0), duration = 3 },
        { pos = Vector3.new(0, 9, 40),  travel = Vector3.new(0, 0, 10), duration = 2 },
        { pos = Vector3.new(0, 12, 52), travel = Vector3.new(8, 0, 0),  duration = 1.8 },
    }

    for i, data in ipairs(platformData) do
        local p = makePart("MovingPlatform" .. i, Vector3.new(8, 1, 8),
            CFrame.new(origin + data.pos), "Bright blue")
        p.Parent = folder

        local startCF = p.CFrame
        local endCF   = startCF + data.travel
        local tweenIn  = TweenService:Create(p, TweenInfo.new(data.duration, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), { CFrame = endCF })
        local tweenOut = TweenService:Create(p, TweenInfo.new(data.duration, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut), { CFrame = startCF })

        tweenIn.Completed:Connect(function() tweenOut:Play() end)
        tweenOut.Completed:Connect(function() tweenIn:Play() end)
        tweenIn:Play()
    end

    local spawn = makePart("SpawnPad", Vector3.new(14, 1, 14),
        CFrame.new(origin + Vector3.new(0, -0.5, -4)), "Bright blue")
    spawn.Parent = folder
end

local function buildStage3(folder, origin)
    -- Lava floor with safe platforms
    local lava = makePart("LavaFloor", Vector3.new(80, 1, 80),
        CFrame.new(origin + Vector3.new(0, -2, 30)), "Bright red",
        Enum.Material.Neon)
    lava.Parent = folder
    killOnTouch(lava)

    local islandPositions = {
        Vector3.new(0, 0, 0),
        Vector3.new(8, 2, 10),
        Vector3.new(-6, 4, 20),
        Vector3.new(10, 6, 28),
        Vector3.new(0, 8, 38),
        Vector3.new(-8, 10, 48),
        Vector3.new(0, 12, 58),
    }
    for i, pos in ipairs(islandPositions) do
        local p = makePart("Island" .. i, Vector3.new(7, 1, 7),
            CFrame.new(origin + pos), "Reddish brown")
        p.Parent = folder
    end

    local spawn = makePart("SpawnPad", Vector3.new(14, 1, 14),
        CFrame.new(origin + Vector3.new(0, -0.5, -6)), "Reddish brown")
    spawn.Parent = folder
end

local function buildStage4(folder, origin)
    -- Spinning blade obstacles on a straight path
    local pathZ = { 0, 10, 20, 30, 40, 50, 60 }
    for i, z in ipairs(pathZ) do
        local p = makePart("Path" .. i, Vector3.new(8, 1, 8),
            CFrame.new(origin + Vector3.new(0, 0, z)), "Dark grey")
        p.Parent = folder
    end

    -- Spinning blades between platforms
    for i = 1, 3 do
        local blade = makePart("Blade" .. i, Vector3.new(16, 0.5, 2),
            CFrame.new(origin + Vector3.new(0, 3, i * 20 - 5)), "Bright red",
            Enum.Material.Neon)
        blade.Anchored = false

        local bodyAngularVelocity = Instance.new("BodyAngularVelocity", blade)
        bodyAngularVelocity.AngularVelocity = Vector3.new(0, 3 + i, 0)
        bodyAngularVelocity.MaxTorque = Vector3.new(0, math.huge, 0)

        blade.Parent = folder
        killOnTouch(blade)
    end

    local spawn = makePart("SpawnPad", Vector3.new(14, 1, 14),
        CFrame.new(origin + Vector3.new(0, -0.5, -6)), "Dark grey")
    spawn.Parent = folder
end

local function buildStage5(folder, origin)
    -- Final challenge: shrinking platforms + speed required
    local platforms = {
        { size = Vector3.new(10, 1, 10), pos = Vector3.new(0, 0, 0) },
        { size = Vector3.new(7, 1, 7),   pos = Vector3.new(0, 2, 12) },
        { size = Vector3.new(5, 1, 5),   pos = Vector3.new(5, 4, 22) },
        { size = Vector3.new(4, 1, 4),   pos = Vector3.new(-4, 6, 32) },
        { size = Vector3.new(3, 1, 3),   pos = Vector3.new(4, 8, 42) },
        { size = Vector3.new(3, 1, 3),   pos = Vector3.new(-3, 10, 50) },
        { size = Vector3.new(16, 1, 16), pos = Vector3.new(0, 12, 62) }, -- Victory pad
    }

    for i, data in ipairs(platforms) do
        local color = i == #platforms and "Bright yellow" or "Cyan"
        local p = makePart("FinalPlatform" .. i, data.size,
            CFrame.new(origin + data.pos), color)
        if i == #platforms then
            p.Material = Enum.Material.Neon
        end
        p.Parent = folder
    end

    -- Victory sign
    local sign = Instance.new("Part")
    sign.Name = "VictorySign"
    sign.Size = Vector3.new(20, 10, 1)
    sign.CFrame = CFrame.new(origin + Vector3.new(0, 20, 62))
    sign.Anchored = true
    sign.CanCollide = false
    sign.Transparency = 1
    sign.Parent = folder

    local billboard = Instance.new("BillboardGui", sign)
    billboard.Size = UDim2.new(0, 400, 0, 120)
    billboard.StudsOffset = Vector3.new(0, 0, 0)
    billboard.AlwaysOnTop = false

    local label = Instance.new("TextLabel", billboard)
    label.Size = UDim2.fromScale(1, 1)
    label.BackgroundTransparency = 1
    label.Text = "YOU WIN! 🎉"
    label.TextColor3 = Color3.fromRGB(255, 215, 0)
    label.TextScaled = true
    label.Font = Enum.Font.GothamBold

    local spawn = makePart("SpawnPad", Vector3.new(14, 1, 14),
        CFrame.new(origin + Vector3.new(0, -0.5, -6)), "Bright yellow")
    spawn.Material = Enum.Material.Neon
    spawn.Parent = folder
end

-- ──────────────────────────────────────────────
--  Main: build all stages
-- ──────────────────────────────────────────────

local stagesFolder = workspace:WaitForChild("Stages")

local stageBuilders = {
    buildStage1,
    buildStage2,
    buildStage3,
    buildStage4,
    buildStage5,
}

for i, buildFn in ipairs(stageBuilders) do
    local stageFolder = Instance.new("Folder")
    stageFolder.Name = "Stage" .. i
    stageFolder.Parent = stagesFolder

    local origin = GameConfig.STAGES[i].spawnPosition
    buildFn(stageFolder, origin)
end

print("[GameManager] All " .. #stageBuilders .. " stages built.")
