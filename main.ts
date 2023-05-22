namespace SpriteKind {
    export const sword = SpriteKind.create()
    export const shield = SpriteKind.create()
}

//  variables
let attacking = false
let gravity = 8
let jump_count = 2
info.setScore(0)
info.setLife(3)
//  sprites
let me = sprites.create(assets.image`me right`, SpriteKind.Player)
scene.cameraFollowSprite(me)
let sword = sprites.create(assets.image`sword right`, SpriteKind.sword)
sword.setFlag(SpriteFlag.GhostThroughWalls, true)
sword.scale = 1.5
let shield = sprites.create(assets.image`shield right`, SpriteKind.shield)
shield.setFlag(SpriteFlag.Invisible, true)
shield.setFlag(SpriteFlag.GhostThroughSprites, true)
function load_level() {
    tiles.setTilemap(assets.tilemap`level1`)
    tiles.placeOnRandomTile(me, assets.tile`player spawn`)
    tiles.setTileAt(me.tilemapLocation(), assets.tile`wall`)
}

load_level()
function position_enemy(enemy: any) {
    tiles.placeOnRandomTile(enemy, assets.tile`wall`)
    if (spriteutils.distanceBetween(enemy, me) < 180) {
        position_enemy(enemy)
    }
    
}

game.onUpdateInterval(2000, function spawn_enemies() {
    let enemy = sprites.create(assets.image`bat`, SpriteKind.Enemy)
    position_enemy(enemy)
    tilesAdvanced.followUsingPathfinding(enemy, me, 50)
    animation.runImageAnimation(enemy, assets.animation`bat right`, 100, true)
})
sprites.onOverlap(SpriteKind.Player, SpriteKind.Enemy, function enemy_collision(me: Sprite, enemy: Sprite) {
    if (me.overlapsWith(shield)) {
        return
    }
    
    info.changeLifeBy(-1)
    pause(2000)
})
controller.B.onEvent(ControllerButtonEvent.Pressed, function defend() {
    timer.background(function trigger_defending() {
        sword.setFlag(SpriteFlag.Invisible, true)
        shield.setFlag(SpriteFlag.Invisible, false)
        shield.setFlag(SpriteFlag.GhostThroughSprites, false)
        pause(500)
        sword.setFlag(SpriteFlag.Invisible, false)
        shield.setFlag(SpriteFlag.Invisible, true)
        shield.setFlag(SpriteFlag.GhostThroughSprites, true)
    })
    shield.setPosition(me.x, me.y)
    if (me.image.equals(assets.image`me left`)) {
        shield.setImage(assets.image`shield left`)
    } else {
        shield.setImage(assets.image`shield right`)
    }
    
})
sprites.onOverlap(SpriteKind.shield, SpriteKind.Enemy, function block(shield: Sprite, enemy: Sprite) {
    let x_vel: number;
    tilesAdvanced.followUsingPathfinding(enemy, me, 0)
    if (shield.image.equals(assets.image`shield left`)) {
        x_vel = -100
    } else {
        x_vel = 100
    }
    
    for (let i = 0; i < 10; i++) {
        enemy.vx = x_vel
        pause(10)
    }
    pause(500)
    tilesAdvanced.followUsingPathfinding(enemy, me, 50)
})
sprites.onOverlap(SpriteKind.sword, SpriteKind.Enemy, function hit_enemy(sword: Sprite, enemy: Sprite) {
    if (attacking) {
        info.changeScoreBy(100)
        enemy.destroy()
    }
    
})
controller.A.onEvent(ControllerButtonEvent.Pressed, function throttle_attack() {
    timer.throttle("attack", 750, function attack() {
        timer.background(function trigger_attacking() {
            
            attacking = true
            pause(250)
            attacking = false
        })
        if (me.image.equals(assets.image`me left`)) {
            animation.runImageAnimation(sword, assets.animation`swing left`, 50, false)
        } else {
            animation.runImageAnimation(sword, assets.animation`swing right`, 50, false)
        }
        
    })
})
function x_movement() {
    if (controller.left.isPressed()) {
        me.vx -= 10
        me.setImage(assets.image`me left`)
    } else if (controller.right.isPressed()) {
        me.vx += 10
        me.setImage(assets.image`me right`)
    }
    
    me.vx *= 0.9
}

controller.up.onEvent(ControllerButtonEvent.Pressed, function jump() {
    
    if (jump_count < 2) {
        me.vy = -175
        jump_count += 1
    }
    
})
function y_movement() {
    
    me.vy += gravity
    if (me.isHittingTile(CollisionDirection.Bottom)) {
        me.vy = 0
        jump_count = 0
    }
    
}

function handle_direction() {
    if (me.image.equals(assets.image`me left`)) {
        sword.setPosition(me.x - 10, me.y - 6)
        if (!attacking) {
            sword.setImage(assets.image`sword left`)
        }
        
    } else {
        sword.setPosition(me.x + 10, me.y - 6)
        if (!attacking) {
            sword.setImage(assets.image`sword right`)
        }
        
    }
    
}

game.onUpdate(function tick() {
    x_movement()
    y_movement()
    handle_direction()
})
