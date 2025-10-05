# ---------------- Weather Classification ----------------
def classify_conditions(temp, rain, wind, humidity):
    """
    Classify weather conditions based on thresholds.
    """
    results = {}
    results["temp"] = "Very Hot" if temp > 35 else "Very Cold" if temp < 10 else "Comfortable"
    results["rain"] = "Wet" if rain > 5 else "Dry"
    results["wind"] = "Very Windy" if wind > 36 else "Calm"
    results["humidity"] = "Uncomfortable" if humidity > 80 or humidity < 30 else "Comfortable"
    return results

def risk_score(temp, rain, wind, humidity):
    """
    Calculate simple risk score based on weather conditions.
    """
    risk = 0
    if temp > 35 or temp < 10:
        risk += 1
    if rain > 5:
        risk += 2
    if wind > 36:
        risk += 1
    if humidity > 80 or humidity < 30:
        risk += 1
    return risk
