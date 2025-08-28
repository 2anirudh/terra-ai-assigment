import json 
from datetime import datetime 
from collections import defaultdict, deque 
from dotenv import load_dotenv 
import os 
from openai import OpenAI 

load_dotenv() 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

def detect_mood(message: str, prev_mood: str = "neutral") -> str: 
    """Detect mood from player's message using OpenAI GPT.""" 
    system_prompt = """ You are a mood detection AI. Given a player's message, classify their mood as one of: 
    [friendly, sad, angry, excited, confused, neutral]. Only return the mood word. """ 
    
    try: 
        response = client.chat.completions.create( 
            model="gpt-3.5-turbo", 
            messages=[ 
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": f'Message: "{message}"\nPrevious mood: {prev_mood}'} 
                ], 
            max_tokens=10, 
            temperature=0 
        )

        return response.choices[0].message.content.strip().lower() 
    
    except Exception as e: 
        print(f"Error in detect_mood: {e}") 
        return prev_mood 
    
def generate_npc_reply(player_id: str, message: str, mood: str, history: list) -> str: 
    """Use OpenAI GPT to generate NPC reply based on mood + recent history.""" 
    

    system_prompt = f""" You are a Non-Player Character (NPC) in a role-playing game. 
                    Your current mood is: {mood}. 
                    Reply briefly (1-2 short sentences) and stay consistent with your mood. """ 
    
    # Context from last 3 messages 
    conversation_context = "\n".join([f"Player: {msg}" for msg in history]) 

    user_prompt = f""" Player just said: "{message}" Recent conversation:\n{conversation_context} 
                  Generate your NPC reply now. """ 
    try: 
        response = client.chat.completions.create( 
            model="gpt-3.5-turbo", 
            messages=[ 
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_prompt},
                ], 
            max_tokens=60, 
            temperature=0.7,
        ) 
        
        return response.choices[0].message.content.strip() 
    
    except Exception as e: 
        return f"(Error generating reply: {e})" 


def main(): 
    with open("players.json", "r") as f: 
        messages = json.load(f) 
    
    print("Sample messages:\n") 
    for m in messages[:5]: print(m) 
    
    messages.sort(key=lambda x: datetime.fromisoformat(x["timestamp"])) 
    
    # 3. Per-player state 
    player_history = defaultdict(lambda: deque(maxlen=3)) 
    # last 3 messages
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
        npc_reply = generate_npc_reply(player_id, text, current_mood, list(player_history[player_id])) 
        
        # log result 
        results.append({ "player_id": player_id, "message": text, "npc_reply": npc_reply, "last_3_messages": list(player_history[player_id]), "npc_mood": current_mood, "timestamp": timestamp }) 
        

    with open("npc_logs.json", "w") as f: 
        json.dump(results[::-1], f, indent=4) 
    
    if __name__ == "__main__": main()