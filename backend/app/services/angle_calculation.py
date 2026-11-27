import math


# ============================================================
# BASIC VECTOR HELPERS
# ============================================================

def _get_coordinate(point, axis, default=0.0):
    """
    Safely read x/y/z from a MediaPipe landmark.
    """
    if point is None:
        return None

    value = getattr(point, axis, default)

    try:
        value = float(value)
    except (TypeError, ValueError):
        return default

    if not math.isfinite(value):
        return default

    return value


def _distance_3d(a, b):
    """
    Calculate 3D Euclidean distance between two landmarks.
    """
    if a is None or b is None:
        return None

    ax = _get_coordinate(a, "x")
    ay = _get_coordinate(a, "y")
    az = _get_coordinate(a, "z")

    bx = _get_coordinate(b, "x")
    by = _get_coordinate(b, "y")
    bz = _get_coordinate(b, "z")

    dx = ax - bx
    dy = ay - by
    dz = az - bz

    distance = math.sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    )

    if not math.isfinite(distance):
        return None

    return distance


# ============================================================
# 3D ANGLE CALCULATION
# ============================================================

def calculate_angle_3d(a, b, c):
    """
    Calculate the angle ABC using 3D landmark coordinates.

    a = first point
    b = vertex/joint
    c = third point

    Example:
        hip -> knee -> ankle

    returns:
        angle in degrees [0, 180]
        or None when the calculation is unreliable.
    """

    if a is None or b is None or c is None:
        return None

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    ax = _get_coordinate(a, "x")
    ay = _get_coordinate(a, "y")
    az = _get_coordinate(a, "z")

    bx = _get_coordinate(b, "x")
    by = _get_coordinate(b, "y")
    bz = _get_coordinate(b, "z")

    cx = _get_coordinate(c, "x")
    cy = _get_coordinate(c, "y")
    cz = _get_coordinate(c, "z")

    # --------------------------------------------------------
    # Vectors BA and BC
    # --------------------------------------------------------

    ba_x = ax - bx
    ba_y = ay - by
    ba_z = az - bz

    bc_x = cx - bx
    bc_y = cy - by
    bc_z = cz - bz

    # --------------------------------------------------------
    # Vector magnitudes
    # --------------------------------------------------------

    magnitude_ba = math.sqrt(
        ba_x * ba_x +
        ba_y * ba_y +
        ba_z * ba_z
    )

    magnitude_bc = math.sqrt(
        bc_x * bc_x +
        bc_y * bc_y +
        bc_z * bc_z
    )

    # Very small vectors produce unstable angles.
    if magnitude_ba < 1e-6 or magnitude_bc < 1e-6:
        return None

    # --------------------------------------------------------
    # Dot product
    # --------------------------------------------------------

    dot_product = (
        ba_x * bc_x +
        ba_y * bc_y +
        ba_z * bc_z
    )

    denominator = magnitude_ba * magnitude_bc

    if denominator < 1e-8:
        return None

    cosine_angle = dot_product / denominator

    # Floating-point protection.
    cosine_angle = max(
        -1.0,
        min(1.0, cosine_angle)
    )

    # --------------------------------------------------------
    # Angle
    # --------------------------------------------------------

    angle_radians = math.acos(cosine_angle)
    angle_degrees = math.degrees(angle_radians)

    if not math.isfinite(angle_degrees):
        return None

    # Numerical safety.
    angle_degrees = max(
        0.0,
        min(180.0, angle_degrees)
    )

    return angle_degrees


# ============================================================
# 2D ANGLE CALCULATION
# ============================================================

def calculate_angle_2d(a, b, c):
    """
    Calculate the angle ABC using only x/y coordinates.

    This is useful as a fallback when z coordinates are
    unreliable.
    """

    if a is None or b is None or c is None:
        return None

    ax = _get_coordinate(a, "x")
    ay = _get_coordinate(a, "y")

    bx = _get_coordinate(b, "x")
    by = _get_coordinate(b, "y")

    cx = _get_coordinate(c, "x")
    cy = _get_coordinate(c, "y")

    ba_x = ax - bx
    ba_y = ay - by

    bc_x = cx - bx
    bc_y = cy - by

    magnitude_ba = math.sqrt(
        ba_x * ba_x +
        ba_y * ba_y
    )

    magnitude_bc = math.sqrt(
        bc_x * bc_x +
        bc_y * bc_y
    )

    if magnitude_ba < 1e-6 or magnitude_bc < 1e-6:
        return None

    dot_product = (
        ba_x * bc_x +
        ba_y * bc_y
    )

    denominator = magnitude_ba * magnitude_bc

    if denominator < 1e-8:
        return None

    cosine_angle = dot_product / denominator

    cosine_angle = max(
        -1.0,
        min(1.0, cosine_angle)
    )

    angle = math.degrees(
        math.acos(cosine_angle)
    )

    if not math.isfinite(angle):
        return None

    return max(
        0.0,
        min(180.0, angle)
    )


# ============================================================
# ROBUST ANGLE CALCULATION
# ============================================================

def calculate_robust_angle(a, b, c):
    """
    Calculate a stable joint angle.

    The 3D MediaPipe landmark coordinates are used first.

    If the 3D calculation cannot produce a valid result,
    the function falls back to the 2D x/y calculation.

    Returns:
        float angle in degrees
        or None
    """

    angle_3d = calculate_angle_3d(
        a,
        b,
        c
    )

    if angle_3d is not None:
        return angle_3d

    return calculate_angle_2d(
        a,
        b,
        c
    )


# ============================================================
# ANGLE VALIDATION
# ============================================================

def is_valid_angle(angle):
    """
    Check whether an angle is physically/numerically valid.
    """

    if angle is None:
        return False

    try:
        angle = float(angle)
    except (TypeError, ValueError):
        return False

    if not math.isfinite(angle):
        return False

    return 0.0 <= angle <= 180.0


# ============================================================
# ANGLE CHANGE
# ============================================================

def calculate_angle_change(previous_angle, current_angle):
    """
    Calculate absolute change between two angles.

    Example:
        previous = 150
        current  = 120

        result = 30
    """

    if not is_valid_angle(previous_angle):
        return None

    if not is_valid_angle(current_angle):
        return None

    return abs(
        float(current_angle) -
        float(previous_angle)
    )


# ============================================================
# NORMALIZED ANGLE
# ============================================================

def normalize_angle(angle):
    """
    Clamp a valid angle to the standard [0, 180] range.
    """

    if not is_valid_angle(angle):
        return None

    return max(
        0.0,
        min(180.0, float(angle))
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def calculate_angle(a, b, c):
    """
    Existing function used by the rest of the project.

    It now uses the robust angle calculation.
    """

    return calculate_robust_angle(
        a,
        b,
        c
    )