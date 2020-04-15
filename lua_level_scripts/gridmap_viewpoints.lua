-- Demonstration of capturing arbitrary viewpoints on text generated map
--[[
  Currently set up to generate observations in the 4 cardinal directions 
  along the xy-plane.  Custom observations can be created by adding 
  additional variables to api._properties.view_pose and adjusting the Look 
  function accordingly.
]]

local DEFAULT_MAP = [[
************
*    *     *
*    *     *
*          *
*    *     *
*    *     *
*** **** ***
*    *     *
*       P  *
*    *     *
*    *     *
************
]]

local DEFAULT_VARIATION_LAYER = [[
            
 AAAA BBBBB 
 AAAA BBBBB 
 AAAA BBBBB 
 AAAA BBBBB 
 AAAA BBBBB 
            
 CCCC DDDDD 
 CCCC DDDDD 
 CCCC DDDDD 
 CCCC DDDDD 
            
]]

local game = require 'dmlab.system.game'
local SHAPE = {width=100, height=100}

local make_map = require 'common.make_map'
local pickups = require 'common.pickups'
local texture_sets = require 'themes.texture_sets'
local custom_observations = require 'decorators.custom_observations'
local property_decorator = require 'decorators.property_decorator'

local api = {
  _properties = {
    view_pose = {
      x='150.0', 
      y='250.0',
      theta='0.0'
    }
  }
}

property_decorator.decorate(api)
property_decorator.addReadWrite('params', api._properties)

-- Called only once at start up. Settings not recognised by DM Lab internal
-- are forwarded through the params dictionary.
function api:init(params)
  params.text_map = params.text_map or DEFAULT_MAP
  params.variation_map = params.variation_map or DEFAULT_VARIATION_LAYER

  -- Seed the map so only one map is created with lights and decals placed in
  -- the same place each run.
  make_map.random():seed(1)
  api._map = make_map.makeMap{
      mapName = "demo_map_settings",
      mapEntityLayer = params.text_map,
      mapVariationsLayer = params.variation_map,
      decalFrequency = 0.5,
      useSkybox = true,
      textureSet = texture_sets.CUSTOMIZABLE_FLOORS
  }
end

-- `make_map` has default pickup types A = apple_reward and G = goal.
-- This callback is used to create pickups with those names.
function api:createPickup(classname)
  return pickups.defaults[classname]
end

-- On first call we return the name of the map. On subsequent calls we return
-- an empty string. This informs the engine to only perform a quik map restart
-- instead.
function api:nextMap()
  local mapName = api._map
  api._map = ''
  return mapName
end


-- add custom observations like DEBUG.~~~
custom_observations.decorate(api)

-- Look from specified view_pose
local function angleLook(yaw)
  local function look()
    local info = game:playerInfo()
    local pos = {
        tonumber(api._properties.view_pose.x),
        tonumber(api._properties.view_pose.y),
        31.125 -- default height of player
    }
    local look = game:playerInfo().angles
    look[2] = tonumber(api._properties.view_pose.theta) + yaw
    local buffer = game:renderCustomView{
        width = SHAPE.width,
        height = SHAPE.height,
        pos = pos,                      --array of numbers
        look = look,                    --array of numbers
        renderPlayer = false,
    }
    return buffer:clone()
  end
  return look
end

custom_observations.addSpec('RGB.FRONT', 'Bytes',
                            {SHAPE.width, SHAPE.height, 3}, angleLook(0))
custom_observations.addSpec('RGB.LEFT', 'Bytes',
                            {SHAPE.width, SHAPE.height, 3}, angleLook(90))
custom_observations.addSpec('RGB.BACK', 'Bytes',
                            {SHAPE.width, SHAPE.height, 3}, angleLook(180))
custom_observations.addSpec('RGB.RIGHT', 'Bytes',
                            {SHAPE.width, SHAPE.height, 3}, angleLook(270))

return api

