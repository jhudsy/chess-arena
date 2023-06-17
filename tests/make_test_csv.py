import random
alphabet="abcdefghijklmnopqrstuvwxyz"

club_list=[]
for i in range(20):
  club_list.append(f"club{i}")

with open("players.csv","w") as f:
   for i in range(100): 
     avoid=','.join(list(map(lambda x: str(x),random.choices(range(100),k=random.randint(1,10)))))
     print(f"{i},{''.join(random.choices(alphabet,k=6))},{''.join(random.choices(alphabet,k=6))},{random.choices(club_list,k=1)[0] if random.random()<0.5 else ''},{random.randint(0,1000)},{random.randint(0,20)},{avoid}",file=f)
  
