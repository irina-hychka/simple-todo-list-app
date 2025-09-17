-- mix.lua — навантаження CRUD без модулів json/cjson
-- Формуємо JSON як рядок і дістаємо id з відповіді регулярками.

local ids = {}
local bodySizes = {256, 512, 1024, 2048}

local function rand(n) return math.random(n) end

local function json_escape(s)
  -- мінімальне екранування (достатньо для нашого payload)
  s = s:gsub('\\', '\\\\'):gsub('"', '\\"')
  return s
end

local function payload(n)
  local suffix = string.rep("x", n)
  local title  = "wrk-" .. tostring(math.random(10^9)) .. "-" .. suffix
  return string.format('{"title":"%s"}', json_escape(title))
end

request = function()
  -- 60% POST, 25% GET, 10% TOGGLE, 5% DELETE
  local r = math.random(100)

  if r <= 60 then
    local size = bodySizes[rand(#bodySizes)]
    wrk.method = "POST"
    wrk.body   = payload(size)
    wrk.headers["Content-Type"] = "application/json"
    return wrk.format(nil, "/api/tasks")

  elseif r <= 85 then
    wrk.method = "GET"
    wrk.body = nil
    return wrk.format(nil, "/api/tasks?status=all")

  elseif r <= 95 then
    if #ids > 0 then
      local id = ids[rand(#ids)]
      wrk.method = "PATCH"
      wrk.body = ""
      return wrk.format(nil, "/api/tasks/" .. id .. "/toggle")
    else
      wrk.method = "GET"
      return wrk.format(nil, "/api/tasks?status=all")
    end

  else
    if #ids > 0 then
      local idx = rand(#ids)
      local id  = ids[idx]
      table.remove(ids, idx)
      wrk.method = "DELETE"
      wrk.body = ""
      return wrk.format(nil, "/api/tasks/" .. id)
    else
      wrk.method = "GET"
      return wrk.format(nil, "/api/tasks?status=all")
    end
  end
end

response = function(status, headers, body)
  if (status == 200 or status == 201) and body and #body > 0 then
    -- якщо прийшов один об’єкт: {"id":123,...}
    local single = body:match('"id"%s*:%s*(%d+)')
    if single then
      table.insert(ids, tonumber(single))
      return
    end
    -- якщо масив: [{"id":1,...},{"id":2,...}]
    local count = 0
    for id in body:gmatch('"id"%s*:%s*(%d+)') do
      table.insert(ids, tonumber(id))
      count = count + 1
      if count >= 10 then break end
    end
  end
end
