-- This script creates the GUI elements when it runs as a LocalScript inside StarterGui.
-- In Rojo workflow the ScreenGui is built here; in plain Studio you can build it manually.

local screenGui = script.Parent
screenGui.Name = "OBbyGui"
screenGui.ResetOnSpawn = false

-- ── Stage indicator (top-left) ──────────────────────────────────────
local stageFrame = Instance.new("Frame")
stageFrame.Name = "StageFrame"
stageFrame.Size = UDim2.new(0, 220, 0, 50)
stageFrame.Position = UDim2.new(0, 16, 0, 16)
stageFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
stageFrame.BackgroundTransparency = 0.3
stageFrame.BorderSizePixel = 0
stageFrame.Parent = screenGui

local corner1 = Instance.new("UICorner", stageFrame)
corner1.CornerRadius = UDim.new(0, 10)

local stageLabel = Instance.new("TextLabel", stageFrame)
stageLabel.Name = "StageLabel"
stageLabel.Size = UDim2.fromScale(1, 1)
stageLabel.BackgroundTransparency = 1
stageLabel.Text = "Stage: 1"
stageLabel.TextColor3 = Color3.new(1, 1, 1)
stageLabel.TextScaled = true
stageLabel.Font = Enum.Font.GothamBold

-- ── Checkpoint notification (center) ───────────────────────────────
local notification = Instance.new("Frame")
notification.Name = "Notification"
notification.AnchorPoint = Vector2.new(0.5, 0)
notification.Size = UDim2.new(0, 340, 0, 60)
notification.Position = UDim2.fromScale(0.5, 0.05)
notification.BackgroundColor3 = Color3.fromRGB(30, 200, 80)
notification.BackgroundTransparency = 1
notification.BorderSizePixel = 0
notification.Parent = screenGui

local corner2 = Instance.new("UICorner", notification)
corner2.CornerRadius = UDim.new(0, 12)

local notifLabel = Instance.new("TextLabel", notification)
notifLabel.Name = "NotifLabel"
notifLabel.Size = UDim2.fromScale(1, 1)
notifLabel.BackgroundTransparency = 1
notifLabel.Text = ""
notifLabel.TextColor3 = Color3.new(1, 1, 1)
notifLabel.TextScaled = true
notifLabel.Font = Enum.Font.GothamBold
