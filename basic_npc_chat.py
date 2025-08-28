import json 
from datetime import datetime 
from collections import defaultdict, deque 


def detect_mood(message: str, current_mood: str) -> str: 
    """Simple rule-based mood detector.""" 
    text = message.lower() 
    if any(word in text for word in ["help", "please", "thanks"]): 
        return "friendly" 
    elif any(word in text for word in ["stupid", "hate", "idiot"]): 
        return "angry" 
    
    return current_mood 

# keep same mood if nothing detected 
def generate_npc_reply(message: str, mood: str, history: list) -> str: 
    """Mock reply generator (replace later with GPT API).""" 
    return f"(NPC in {mood} mood replies to: '{message}')" 

def main(): 
    with open("players.json", "r") as f: 
        messages = json.load(f) 
        
    print("Sample messages:\n")
    for m in messages[:5]: 
        print(m) 
        
    messages.sort(key=lambda x: datetime.fromisoformat(x["timestamp"])) 
    
    # 3. Per-player state 
    player_history = defaultdict(lambda: deque(maxlen=3)) # last 3 messages 
    player_mood = defaultdict(lambda: "neutral") 
    
    results = [] 
    # 4. Process each message 
    for msg in messages: 
        player_id = msg["player_id"] 
        text = msg["text"] 
        timestamp = msg["timestamp"] 
        
        # update history 
        player_history[player_id].append(text) 
        # update mood 
        current_mood = detect_mood(text, player_mood[player_id]) 
        player_mood[player_id] = current_mood 
        
        # generate reply (mock for now) 
        npc_reply = generate_npc_reply(text, current_mood, list(player_history[player_id])) 
        
        # log result 
        results.append(
            { "player_id": player_id, 
             "message": text, 
             "npc_reply": npc_reply, 
             "last_3_messages": list(player_history[player_id]), 
             "npc_mood": current_mood, 
             "timestamp": timestamp 
             }
        ) 
        
    with open("npc_logs.json", "w") as f: 
        json.dump(results[::-1], f, indent=4) 
            
    if __name__ == "__main__": 
        main()