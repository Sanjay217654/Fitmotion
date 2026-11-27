from enum import StrEnum


class ExerciseType(StrEnum):
    SQUAT = "squat"
    PUSH_UP = "push_up"
    LUNGE = "lunge"
    BICEP_CURL = "bicep_curl"
    SHOULDER_PRESS = "shoulder_press"


class FitnessLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class FitnessGoal(StrEnum):
    TECHNIQUE = "improve_technique"
    STRENGTH = "build_strength"
    FITNESS = "improve_fitness"
    FLEXIBILITY = "improve_flexibility"
    SPORTS_PERFORMANCE = "sports_performance"
    WEIGHT_MANAGEMENT = "weight_management"
