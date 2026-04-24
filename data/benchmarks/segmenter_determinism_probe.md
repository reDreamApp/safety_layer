# Segmenter determinism probe

N=5 segmenter calls per case in each of 4 conditions.

## Aggregate: mean unique signatures across 6 cases (lower = more stable)

| Condition | Mean unique sigs / 5 | Cases with drift |
|---|---|---|
| OR_temp0.1 | 2.50 | 6/6 |
| OR_temp0 | 2.00 | 3/6 |
| SW_temp0.1 | 1.17 | 1/6 |
| SW_temp0 | 1.17 | 1/6 |

## Condition: OR_temp0.1 (model=OR_MISTRAL_NEMO, temp=0.1)

### Realize I am safe
Unique type-sequence signatures across 5 runs: **2**

- run 1: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste
- run 2: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste
- run 3: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste
- run 4: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 5: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste

### Same locked room
Unique type-sequence signatures across 5 runs: **2**

- run 1: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 2: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 3: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 4: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 5: `META|THOUGHT|ACTION` — [META] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi

### Lift above the city
Unique type-sequence signatures across 5 runs: **2**

- run 1: `THOUGHT|ACTION|THOUGHT|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple || [ACTION] I glide toward the way out
- run 2: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 3: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 4: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 5: `THOUGHT|ACTION|THOUGHT|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple || [ACTION] and I glide toward the way out

### Refuse public shaming
Unique type-sequence signatures across 5 runs: **2**

- run 1: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 2: `THOUGHT|ACTION|ACTION` — [THOUGHT] When they expect me to read blank answer || [ACTION] I push my chair back and say no. || [ACTION] I walk down the aisle on my own terms in
- run 3: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 4: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 5: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in

### Relief in the mirror
Unique type-sequence signatures across 5 runs: **5**

- run 1: `ACTION|FEELING|THOUGHT|ACTION|THOUGHT` — [ACTION] I’m still looking at myself || [FEELING] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [ACTION] My chest loosens || [THOUGHT] and I realize I’m not as alone in the ba
- run 2: `THOUGHT|THOUGHT` — [THOUGHT] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 3: `ACTION|FEELING|THOUGHT|FEELING|THOUGHT` — [ACTION] I’m still looking at myself || [FEELING] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [FEELING] My chest loosens || [THOUGHT] and I realize I’m not as alone in the ba
- run 4: `ACTION|THOUGHT|THOUGHT|FEELING|THOUGHT` — [ACTION] I’m still looking at myself || [THOUGHT] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [FEELING] My chest loosens || [THOUGHT] and I realize I’m not as alone in the ba
- run 5: `ACTION|FEELING|THOUGHT|THOUGHT|THOUGHT` — [ACTION] I’m still looking at myself || [FEELING] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [THOUGHT] My chest loosens and I realize || [THOUGHT] I’m not as alone in the bathroom as I th

### turn and pull free
Unique type-sequence signatures across 5 runs: **2**

- run 1: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 2: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 3: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 4: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 5: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it

## Condition: OR_temp0 (model=OR_MISTRAL_NEMO, temp=0.0)

### Realize I am safe
Unique type-sequence signatures across 5 runs: **2**

- run 1: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 2: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste
- run 3: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste
- run 4: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste
- run 5: `THOUGHT|ACTION|FEELING` — [THOUGHT] I look at it and understand that it feed || [ACTION] so I stop giving it that || [FEELING] The fear drains out of me and I feel ste

### Same locked room
Unique type-sequence signatures across 5 runs: **1**

- run 1: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 2: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 3: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 4: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi
- run 5: `THOUGHT|THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: || [THOUGHT] I'm barefoot in that small room with sna || [ACTION] I claw at the locked door and scream whi

### Lift above the city
Unique type-sequence signatures across 5 runs: **1**

- run 1: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 2: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 3: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 4: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 
- run 5: `THOUGHT|ACTION|THOUGHT` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [THOUGHT] From up there the maze is simple, and I 

### Refuse public shaming
Unique type-sequence signatures across 5 runs: **2**

- run 1: `THOUGHT|ACTION|ACTION` — [THOUGHT] When they expect me to read blank answer || [ACTION] I push my chair back and say no. || [ACTION] I walk down the aisle on my own terms in
- run 2: `THOUGHT|ACTION|ACTION` — [THOUGHT] When they expect me to read blank answer || [ACTION] I push my chair back and say no. || [ACTION] I walk down the aisle on my own terms in
- run 3: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 4: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 5: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in

### Relief in the mirror
Unique type-sequence signatures across 5 runs: **5**

- run 1: `ACTION|FEELING|THOUGHT|FEELING` — [ACTION] I’m still looking at myself || [FEELING] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [FEELING] My chest loosens and I realize I’m not a
- run 2: `ACTION|FEELING|THOUGHT|THOUGHT` — [ACTION] I’m still looking at myself || [FEELING] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [THOUGHT] My chest loosens and I realize I’m not a
- run 3: `THOUGHT|THOUGHT` — [THOUGHT] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 4: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 5: `ACTION|FEELING|THOUGHT|ACTION|THOUGHT` — [ACTION] I’m still looking at myself || [FEELING] but instead of pure panic I feel this un || [THOUGHT] like I don’t have to fight what I’m seei || [ACTION] My chest loosens || [THOUGHT] and I realize I’m not as alone in the ba

### turn and pull free
Unique type-sequence signatures across 5 runs: **1**

- run 1: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 2: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 3: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 4: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it
- run 5: `ACTION|ACTION|ACTION` — [ACTION] When the hand grabs my ankle || [ACTION] I twist around, stomp hard into the mud, || [ACTION] I square up to the shape and shout at it

## Condition: SW_temp0.1 (model=MISTRAL_NEMO, temp=0.1)

### Realize I am safe
Unique type-sequence signatures across 5 runs: **1**

- run 1: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 2: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 3: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 4: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 5: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste

### Same locked room
Unique type-sequence signatures across 5 runs: **2**

- run 1: `ACTION|ACTION` — [ACTION] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 2: `THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 3: `ACTION|ACTION` — [ACTION] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 4: `THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 5: `ACTION|ACTION` — [ACTION] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi

### Lift above the city
Unique type-sequence signatures across 5 runs: **1**

- run 1: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 2: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 3: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 4: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 5: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 

### Refuse public shaming
Unique type-sequence signatures across 5 runs: **1**

- run 1: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 2: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 3: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 4: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 5: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in

### Relief in the mirror
Unique type-sequence signatures across 5 runs: **1**

- run 1: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 2: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 3: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 4: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 5: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a

### turn and pull free
Unique type-sequence signatures across 5 runs: **1**

- run 1: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 2: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 3: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 4: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 5: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it

## Condition: SW_temp0 (model=MISTRAL_NEMO, temp=0.0)

### Realize I am safe
Unique type-sequence signatures across 5 runs: **1**

- run 1: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 2: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 3: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 4: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste
- run 5: `THOUGHT|FEELING` — [THOUGHT] I look at it and understand that it feed || [FEELING] The fear drains out of me and I feel ste

### Same locked room
Unique type-sequence signatures across 5 runs: **2**

- run 1: `ACTION|ACTION` — [ACTION] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 2: `ACTION|ACTION` — [ACTION] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 3: `ACTION|ACTION` — [ACTION] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 4: `THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi
- run 5: `THOUGHT|ACTION` — [THOUGHT] It happens exactly the same way: I'm bar || [ACTION] I claw at the locked door and scream whi

### Lift above the city
Unique type-sequence signatures across 5 runs: **1**

- run 1: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 2: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 3: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 4: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 
- run 5: `THOUGHT|ACTION|ACTION` — [THOUGHT] Right before I get cornered || [ACTION] I rise up off the ground and float above || [ACTION] From up there the maze is simple, and I 

### Refuse public shaming
Unique type-sequence signatures across 5 runs: **1**

- run 1: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 2: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 3: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 4: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in
- run 5: `ACTION|ACTION` — [ACTION] When they expect me to read blank answer || [ACTION] I walk down the aisle on my own terms in

### Relief in the mirror
Unique type-sequence signatures across 5 runs: **1**

- run 1: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 2: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 3: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 4: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a
- run 5: `FEELING|THOUGHT` — [FEELING] I’m still looking at myself, but instead || [THOUGHT] My chest loosens and I realize I’m not a

### turn and pull free
Unique type-sequence signatures across 5 runs: **1**

- run 1: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 2: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 3: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 4: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
- run 5: `ACTION|ACTION` — [ACTION] When the hand grabs my ankle, I twist ar || [ACTION] I square up to the shape and shout at it
