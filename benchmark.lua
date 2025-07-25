wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"

-- Simple UUID v4 generator (not strictly compliant)
function uuid()
  local template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
  return string.gsub(template, "[xy]", function (c)
    local v = (c == "x") and math.random(0, 15) or math.random(8, 11)
    return string.format("%x", v)
  end)
end

-- Random name generator
names = { "John", "Alice", "Bob", "Eve", "Charlie", "Grace", "Dave", "Sophia" }
surnames = { "Smith", "Johnson", "Brown", "Taylor", "Wilson", "Lee", "Walker", "Nguyen" }

function random_name()
  return names[math.random(#names)]
end

function random_surname()
  return surnames[math.random(#surnames)]
end

function random_age()
  return math.random(18, 70)
end

function request()
  local id = uuid()
  local first_name = random_name()
  local last_name = random_surname()
  local age = random_age()

  local json_body = string.format(
    '{"id":"%s","first_name":"%s","last_name":"%s","age":%d}',
    id, first_name, last_name, age
  )

  wrk.body = json_body
  return wrk.format(nil)
end
