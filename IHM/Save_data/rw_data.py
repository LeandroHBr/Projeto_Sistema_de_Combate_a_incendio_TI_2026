import json


def Read_data():
    with open("./data.json","r",encoding="utf-8") as saved_data:
        return json.load(saved_data);

def Write_data(Conf = None,Alert=None,Bomb_state=None):
    with open("./data.json","r",encoding="utf-8") as saved_data:
        data = json.load(saved_data)
    with open("./data.json","w",encoding="utf-8") as saved_data:
        Conf = data["Conf"] if Conf is None else Conf
        Alert = data["Alert"] if Alert is None else Alert
        Bomb_state = data["Bomb"] if Bomb_state is None else Bomb_state
        
        json.dump({
        "Conf":Conf,
        "Alert":Alert,
        "Bomb":Bomb_state
        },saved_data,indent=1);
        

