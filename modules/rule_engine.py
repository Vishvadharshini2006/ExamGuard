PENALTIES = {



    # Browser Monitoring
    "Tab Switched": 5,
    "Right Click": 2,
    "Copy Attempt": 5,
    "Paste Attempt": 5,
    "F12 Pressed": 7,
    "Developer Tools Attempt": 10,
    "View Source Attempt": 7

}


def calculate_score(score,event):

    deduction = PENALTIES.get(event,0)

    score -= deduction

    if score < 0:

        score = 0

    return score