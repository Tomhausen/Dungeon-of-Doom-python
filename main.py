@namespace
class SpriteKind:
    sword = SpriteKind.create()
    shield = SpriteKind.create()

# variables
attacking = False
gravity = 8
jump_count = 2
frame = 0
tiles_to_animate: List[tiles.Location] = []
info.set_score(0)
info.set_life(3)

# sprites
me = sprites.create(assets.image("me right"), SpriteKind.player)
scene.camera_follow_sprite(me)
sword = sprites.create(assets.image("sword right"), SpriteKind.sword)
sword.set_flag(SpriteFlag.GHOST_THROUGH_WALLS, True)
sword.scale = 1.5
shield = sprites.create(assets.image("shield right"), SpriteKind.shield)
shield.set_flag(SpriteFlag.INVISIBLE, True)
shield.set_flag(SpriteFlag.GHOST_THROUGH_SPRITES, True)
dash = sprites.create(assets.image("dash right"))
dash.set_flag(SpriteFlag.INVISIBLE, True)

def load_level():
    global tiles_to_animate
    tiles.set_tilemap(assets.tilemap("level1"))
    tiles.place_on_random_tile(me, assets.tile("player spawn"))
    tiles.set_tile_at(me.tilemap_location(), assets.tile("wall"))
    tiles_to_animate = tiles.get_tiles_by_type(assets.tile("torch"))
load_level()

def flicker():
    global frame
    anim = assets.animation("torch flicker")
    for tile in tiles_to_animate:
        tiles.set_tile_at(tile, anim[frame])
    frame += 1
    if frame == len(anim) - 1:
        frame = 0
game.on_update_interval(200, flicker)

def position_enemy(enemy):
    tiles.place_on_random_tile(enemy, assets.tile("wall"))
    if spriteutils.distance_between(enemy, me) < 180:
        position_enemy(enemy)

def spawn_enemies():
    enemy = sprites.create(assets.image("bat"), SpriteKind.enemy)
    position_enemy(enemy)
    tilesAdvanced.follow_using_pathfinding(enemy, me, 50)
    animation.run_image_animation(enemy, assets.animation("bat right"), 100, True)
game.on_update_interval(2000, spawn_enemies)
          
def enemy_collision(me, enemy):
    if me.overlaps_with(shield):
        return
    info.change_life_by(-1)
    pause(2000)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy, enemy_collision)

def trigger_defending():
    sword.set_flag(SpriteFlag.INVISIBLE, True)
    shield.set_flag(SpriteFlag.INVISIBLE, False)
    shield.set_flag(SpriteFlag.GHOST_THROUGH_SPRITES, False)
    pause(500)
    sword.set_flag(SpriteFlag.INVISIBLE, False)
    shield.set_flag(SpriteFlag.INVISIBLE, True)
    shield.set_flag(SpriteFlag.GHOST_THROUGH_SPRITES, True)

def defend():
    timer.background(trigger_defending)
    shield.set_position(me.x, me.y)
    if me.image.equals(assets.image("me left")):
        shield.set_image(assets.image("shield left"))
    else:
        shield.set_image(assets.image("shield right"))
controller.B.on_event(ControllerButtonEvent.PRESSED, defend)

def block(shield, enemy):
    tilesAdvanced.follow_using_pathfinding(enemy, me, 0)
    if shield.image.equals(assets.image("shield left")):
        x_vel = -100
    else:
        x_vel = 100
    for i in range(10):
        enemy.vx = x_vel
        pause(10)
    pause(500)
    tilesAdvanced.follow_using_pathfinding(enemy, me, 50)
sprites.on_overlap(SpriteKind.shield, SpriteKind.enemy, block)

def hit_enemy(sword, enemy):
    if attacking:
        info.change_score_by(100)
        enemy.destroy()
sprites.on_overlap(SpriteKind.sword, SpriteKind.enemy, hit_enemy)

def attack():
    timer.background(trigger_attacking)
    if me.image.equals(assets.image("me left")):
        animation.run_image_animation(sword, assets.animation("swing left"), 50, False)
    else:
        animation.run_image_animation(sword, assets.animation("swing right"), 50, False)

def throttle_attack():
    timer.throttle("attack", 750, attack)
controller.A.on_event(ControllerButtonEvent.PRESSED, throttle_attack)

def trigger_attacking():
    global attacking
    attacking = True
    pause(250)
    attacking = False

def dash_anim():
    dash.set_flag(SpriteFlag.INVISIBLE, False)
    while Math.abs(me.vx) > 100:
        dash.set_position(me.x, me.y)
        if me.vx > 0:
            dash.set_image(assets.image("dash right"))
        else:
            dash.set_image(assets.image("dash left"))
        pause(10)
    dash.set_flag(SpriteFlag.INVISIBLE, True)

def dash_left():
    me.vx = -300
    timer.background(dash_anim)
controller.combos.attach_combo("ll", dash_left)

def dash_right():
    me.vx = 300
    timer.background(dash_anim)
controller.combos.attach_combo("rr", dash_right)

def x_movement():
    if controller.left.is_pressed():
        me.vx -= 10
        me.set_image(assets.image("me left"))
    elif controller.right.is_pressed():
        me.vx += 10
        me.set_image(assets.image("me right"))
    me.vx *= 0.9

def jump():
    global jump_count
    if jump_count < 2:
        me.vy = -175
        jump_count += 1
controller.up.on_event(ControllerButtonEvent.PRESSED, jump)

def y_movement():
    global jump_count
    me.vy += gravity
    if me.is_hitting_tile(CollisionDirection.BOTTOM):
        me.vy = 0
        jump_count = 0

def handle_direction():
    if me.image.equals(assets.image("me left")):
        sword.set_position(me.x - 10, me.y - 6)
        if not attacking:
            sword.set_image(assets.image("sword left"))
    else:
        sword.set_position(me.x + 10, me.y - 6)
        if not attacking:
            sword.set_image(assets.image("sword right"))

def tick():
    x_movement()
    y_movement()
    handle_direction()
game.on_update(tick)
