local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer
local Events = ReplicatedStorage:WaitForChild("Events")
local CheckpointReached = Events:WaitForChild("CheckpointReached")

local gui = player.PlayerGui:WaitForChild("OBbyGui")
local stageLabel = gui:WaitForChild("StageFrame"):WaitForChild("StageLabel")
local notification = gui:WaitForChild("Notification")
local notifLabel = notification:WaitForChild("NotifLabel")

local function showNotification(text)
    notifLabel.Text = text
    notification.BackgroundTransparency = 0

    local fadeIn = TweenService:Create(notification,
        TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        { Position = UDim2.fromScale(0.5, 0.15) })
    fadeIn:Play()
    fadeIn.Completed:Wait()

    task.wait(2)

    local fadeOut = TweenService:Create(notification,
        TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
        { Position = UDim2.fromScale(0.5, 0.05), BackgroundTransparency = 1 })
    fadeOut:Play()
end

CheckpointReached.OnClientEvent:Connect(function(stageNumber, stageConfig)
    stageLabel.Text = "Stage: " .. stageNumber
    if stageConfig then
        showNotification("Checkpoint! " .. stageConfig.name)
    end
end)
