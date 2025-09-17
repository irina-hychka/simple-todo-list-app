-- 80% POST, 20% GET до /api/tasks
counter = 0
request = function()
  counter = counter + 1
  if counter % 5 == 0 then
    -- GET кожен 5-й запит
    return wrk.format("GET", "/api/tasks?status=all")
  else
    local body = string.format('{"title":"load-%d"}', math.random(1,1e9))
    local headers = { ["Content-Type"] = "application/json" }
    return wrk.format("POST", "/api/tasks", headers, body)
  end
end
