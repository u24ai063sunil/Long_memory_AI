sessions = {}

def get_turn(session_id):
    if session_id not in sessions:
        sessions[session_id]=0
    sessions[session_id]+=1
    return sessions[session_id]
