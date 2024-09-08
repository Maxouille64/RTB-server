from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import numpy as np
import random
import xml.etree.ElementTree as ET
import json

team = []
levels = {'lunatic': 0 , 'hard': 1500, 'normal': 1630, 'easy': 1760}
levels_ou = {'lunatic': 0 , 'hard': 1500, 'normal': 1695, 'easy': 1825}
tiers_ou = ["gen8ou","gen8doublesou","gen9ou"]

url = "https://raw.githubusercontent.com/Maxouille64/database/main/stats/2023-12/"
#url = "https://www.smogon.com/stats/2024-08/chaos/"
root_dir = "/home/Maxouille/mysite/"
list_pok = []

def get_raw(url):
    myfile = requests.get(url)
    return myfile.text

def add_user(username):
	doc = open(root_dir + "userlist.json","r+")
	text = doc.read()
	jsn = json.loads(text)
	jsn[username] = (jsn[username] + 1) if jsn.__contains__(username) else 1
	doc.seek(0)
	doc.truncate()
	doc.write(json.dumps(jsn))
	return

#load custom graph
with open(root_dir + "mat/gen8ou/matrice.txt","r") as raw_mat:
	mat = raw_mat.read().split("\n")
	mat = [i.split(",") for i in mat]
	mat.pop()

for i in range(len(mat)):
	mat[i][i] = float("inf")

tree = ET.parse(root_dir + "mat/gen8ou/graphe.graphml")
root = tree.getroot()

for child in root[0]:
	if child.tag == "node":
		list_pok.append([child.attrib["id"], child.attrib["mainText"]])

def url_to_json(url):
    x = requests.get(url)
    data = x.json()
    return data

#loads smogons usages stats
def json_to_mat(jsn, t):
	mat_stat = []
	list_pok = []

	jsn.keys()
	n=0
	for i in jsn.keys():
		list_pok.append([n,i])
		n+=1

	for i in range(n):
		jsn[list_pok[i][1]][t][list_pok[i][1]] = 0
		l_temp=[]
		for j in list_pok:
			if j[1] in (jsn[list_pok[i][1]][t]):
				l_temp.append(jsn[list_pok[i][1]][t][j[1]])
			else:
				l_temp.append(0)
		mat_stat.append(l_temp)

	dim=len(mat_stat)

	for i in range(dim):
		mat_stat[i][i] = float("inf")

	return mat_stat, list_pok

def teamify(M,l,p):
	dim=len(M)
	team = []
	vraiteam = []
	length = len(l)
	print("TEAM => ",p)
	if len(p) <= 0:
		p = random.randint(0,length-1)
		team.append(p)
		vraiteam.append(l[p][1])
	else:
		for i in l:
			if i[1] in p:
				 team.append(int(i[0]))
				 vraiteam.append(i[1])
	print("length",length)
	print("dim",dim)
	print("1) ", vraiteam)
	for i in range(6-len(team)):
		tab_val = np.zeros(length)
		for j in range(0,len(team)):
			for k in range(0,length):
				tab_val[k] = tab_val[k] + abs(float(M[int(team[j])][k]))
		#Préparation tirage
		tab_val[tab_val == float("inf")] = 0
		#Tirage
		#print(tab_val)
		x = random.choices(
		 	population=l,
		   	weights=tab_val,
		   	k=1)[0]

		team.append(int(x[0]))
		vraiteam.append(x[1])

		print(str(int(i) + 2) + ") ",vraiteam)

	return vraiteam, team

def pastify(team, jsn):
	paste = ""
	for pokemon in team:
		paste = paste + str(pokemon) + " @ "
		p=[]
		w=[]
		for i, j in jsn[pokemon]["Items"].items():
			p.append(i)
			w.append(j)
		paste = paste + random.choices(
		 	population=p,
		   	weights=w,
		   	k=1)[0]
		p=[]
		w=[]
		for i, j in jsn[pokemon]["Abilities"].items():
			p.append(i)
			w.append(j)
		paste = paste + "\nAbility: " + random.choices(
		 	population=p,
		   	weights=w,
		   	k=1)[0]
		p=[]
		w=[]
		for i, j in jsn[pokemon]["Spreads"].items():
			p.append(i)
			w.append(j)
		spread = random.choices(
		 	population=p,
		   	weights=w,
		   	k=1)[0].split(":")
		evs = spread[1].split("/")
		paste = paste + "\nEVs: " + evs[0] + " HP / " + evs[1] + " Atk / " + evs[2] + " Def / " + evs[3] + " SpA / " + evs[4] + " SpD / " + evs[5] + " Spe / " + evs[0] + "\n" + spread[0] + " Nature"
		p=[]
		w=[]
		for i, j in jsn[pokemon]["Moves"].items():
			p.append(i)
			w.append(j)
		for k in range(4):
			#Tirage
			x = random.choices(
			 	population=p,
			   	weights=w,
			   	k=1)[0]
			w[p.index(x)] = 0
			paste = paste + "\n- " + x
		paste = paste + "\n\n"
	return paste

def setify(team, jsn):
    paste = ""
    for pokemon in team:
        set = random.choices(
            population=list(jsn[pokemon.replace("-","").replace(" ","").lower()].keys()),
            weights=list(jsn[pokemon.replace("-","").replace(" ","").lower()].values()),
            k=1)[0]
        set = set.split("|")
        paste = paste + str(pokemon) + " @ "
        paste = paste + set[1]
        paste = paste + "\nAbility: " + set[0]
        evs = set[3].split(",")
        paste = paste + "\nEVs: " + evs[0] + " HP / " + evs[1] + " Atk / " + evs[2] + " Def / " + evs[3] + " SpA / " + evs[4] + " SpD / " + evs[5] + " Spe / " + evs[0] + "\n" + set[2] + " Nature"
        for k in range(4):
            paste = paste + "\n- " + set[4 + k]
        paste = paste + "\n\n"
    return paste

def sisify(team, tier):
		jsn = url_to_json("https://pkmn.github.io/smogon/data/stats/" + tier + ".json")["pokemon"]
		mat, list_pok = json_to_mat(jsn, "teammates")
		return teamify(mat , list_pok, team)

def smogonify(team, jsn):
    paste = ""
    for pokemon in team:
        pokemon = pokemon.replace("-Mega","").replace("Ash-","")
        set = jsn[pokemon][random.choice(list(jsn[pokemon].keys()))]
        paste += str(pokemon) + " @ "
        if isinstance(set["item"], list):
            paste += random.choice(set["item"])
        else:
            paste += set["item"]
        if "ability" in set:
            if isinstance(set["ability"], list):
                paste += "\nAbility: " + random.choice(set["ability"])
            else:
                paste += "\nAbility: " + set["ability"]

        if "teratypes" in set:
            if isinstance(set["teratypes"], list):
                paste += "\nTera Type: " + random.choice(set["teratypes"])
            else:
                paste += "\nTera Type: " + set["teratypes"]

        paste += "\nEVs: "
        if isinstance(set["evs"], list):
            evs = random.choice(set["evs"])
        else:
            evs = set["evs"]
        print(evs)
        for i in evs:
            paste = paste + str(evs[i]) + " " + i + " / "
        if isinstance(set["nature"], list):
            paste += "\n" + random.choice(set["nature"])  + " Nature\n"
        else:
            paste += "\n" + set["nature"]  + " Nature\n"
        for i in set["moves"]:
            if isinstance(i, list):
                paste += "-" + random.choice(i) + "\n"
            else:
                paste += "-" + i + "\n"
        paste = paste + "\n\n"
    return paste

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/')
def test():
    doc = open(root_dir + "userlist.json","r+")
    text = doc.read()
    return jsonify(sorted(json.loads(text).items(), key=lambda x: x[1], reverse=True))

@app.route('/matrix/', methods=['GET', 'POST'])
def handle_request():
	text = request.args.get('input')
	print(text)
	jsn = json.loads(text)
	tier = jsn['tier']
	username = jsn['username'] if jsn.__contains__('username') else "no name"
	add_user(username)
	if tier != "gen8ou":
		print("== /!\ ERREUR /!\ ==")
		return
	team = jsn['team'] if jsn.__contains__('team') else []
	six = teamify(mat, list_pok, team)[0]
	jsn2 = url_to_json("https://raw.githubusercontent.com/pmariglia/showdown/604757e2954eb7a2db752c7d05a7bbd5f28b4fa8/data/ou_sets.json")["pokemon"]
	return setify(six,jsn2)

@app.route('/lunatic/', methods=['GET', 'POST'])
def lunatic():
	text = str(request.args.get('input'))
	print(text)
	jsn = json.loads(text)
	tier = jsn['tier']
	print(tier)
	team = jsn['team'] if jsn.__contains__('team') else []
	elo = jsn['mod']
	username = jsn['username'] if jsn.__contains__('username') else "no name"
	add_user(username)
	#if tiers_ou[tier]:
	if tier in tiers_ou:
		elo = levels_ou[elo]
		text = str(request.args.get('input'))
		jsn = json.loads(text)
		tier = jsn['tier']
		team = jsn['team'] if jsn.__contains__('team') else []
		jsn2 = url_to_json(url + tier + "-" + str(elo) + ".json")["data"]
		mat, list_pok = json_to_mat(jsn2, "Teammates")
		return pastify(teamify(mat , list_pok, team)[0], jsn2)
	else:
		elo = levels[elo]
		text = str(request.args.get('input'))
		jsn = json.loads(text)
		tier = jsn['tier']
		team = jsn['team'] if jsn.__contains__('team') else []
		jsn2 = url_to_json(url + tier + "-" + str(elo) + ".json")["data"]
		mat, list_pok = json_to_mat(jsn2, "Teammates")
		return pastify(teamify(mat , list_pok, team)[0], jsn2)


@app.route('/smogdex/', methods=['GET', 'POST'])
def smogdex():
    text = str(request.args.get('input'))
    print(text)
    jsn = json.loads(text)
    tier = jsn['tier']
    print(tier)
    username = jsn['username'] if jsn.__contains__('username') else "no name"
    add_user(username)
    jsn = url_to_json("https://pkmn.github.io/smogon/data/sets/" + tier + ".json")
    return smogonify(sisify([random.choice(list(jsn.keys()))],tier)[0], jsn)

@app.route('/teambuilder/', methods=['GET', 'POST'])
def teambuilder():
	text = request.args.get('input')
	print(text)
	jsn = json.loads(text)
	return jsn