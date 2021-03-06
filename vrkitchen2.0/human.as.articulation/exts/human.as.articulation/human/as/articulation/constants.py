# constants

humanoid_joint2_motor_effort = {
    "lower_waist:0": 67.5, #0
    "lower_waist:1": 67.5,
    "right_upper_arm:0": 67.5,
    "right_upper_arm:2": 67.5,
    "left_upper_arm:0": 67.5,
    "left_upper_arm:2": 67.5, #5
    "pelvis": 67.5,
    "right_lower_arm": 45.0,
    "left_lower_arm": 45.0,
    "right_thigh:0": 45.0,
    "right_thigh:1": 135.0, #10
    "right_thigh:2": 45.0,
    "left_thigh:0": 45.0,
    "left_thigh:1": 135.0,
    "left_thigh:2": 45.0,
    "right_shin": 90.0, #15
    "left_shin": 90.0,
    "right_foot:0": 22.5,
    "right_foot:1'": 22.5,
    "left_foot:0": 22.5,
    "left_foot:1'": 22.5, #20
}

humanoid_motor_effort = list(humanoid_joint2_motor_effort.values())


sit_position_target = [0., 0., 0., 0., 0., 
                          0., 0., -1.5, -1.5, 0., 
                          -1.5, 0., 0., -1.5, 0., 
                          -1.5, -1.5, 0., 0., 0., 
                          0.]