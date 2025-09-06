def award_badges(score: int, delta_market: float, sentiment: float, underdog: bool, picks_count: int):
    badges = []
    if score >= 95: badges.append({"name":"Perfect Plan","emoji":"🏆","desc":"Scored 95+ in a week."})
    if delta_market >= 0.6: badges.append({"name":"Market Sniper","emoji":"🎯","desc":"Exploited market mismatch expertly."})
    if underdog and score >= 85: badges.append({"name":"Bluff Master","emoji":"🎭","desc":"High-scoring underdog plan."})
    if picks_count >= 3 and sentiment >= 0.5: badges.append({"name":"Narrative Navigator","emoji":"📰","desc":"Turned positive narrative into points."})
    if picks_count >= 3 and delta_market < 0 and score >= 80: badges.append({"name":"Against The Grain","emoji":"🧠","desc":"Won despite market headwinds."})
    if score >= 80 and picks_count >= 3: badges.append({"name":"Solid OC","emoji":"📋","desc":"Consistently strong plan."})
    return badges
