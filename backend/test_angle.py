from types import SimpleNamespace

from app.services.angle_calculation import calculate_angle


# Example points
hip = SimpleNamespace(x=0.0, y=0.0)
knee = SimpleNamespace(x=1.0, y=0.0)
ankle = SimpleNamespace(x=2.0, y=0.0)

angle = calculate_angle(hip, knee, ankle)

print("Knee angle:", angle)