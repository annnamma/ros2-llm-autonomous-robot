def validate_mission(mission):
    allowed_missions = ["patrol"]

    if "mission" not in mission:
        return False, "Missing mission"

    if mission["mission"] not in allowed_missions:
        return False, "Invalid mission"

    if "loops" in mission:
        loops = mission["loops"]
        if loops < 1 or loops > 10:
            return False, "Invalid loop count"

    return True, "Mission valid"
