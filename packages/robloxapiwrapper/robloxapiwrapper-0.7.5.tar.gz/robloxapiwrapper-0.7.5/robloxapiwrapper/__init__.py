import json
import requests
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

group_info_dict = {"past": 0}


class groupBot:
    
    def __init__(self, group_id=False, group_join=False, auto_moderate=False, auto_role=False, sales_tracker=False, webhook=False):
        self.group_join = group_join
        self.auto_moderate = auto_moderate
        self.auto_role = auto_role
        self.sales_tracker = sales_tracker
        self.webhook = webhook
        
        if group_id == False:
            raise Exception("group_id not defined")
        
        else:
            group_info_dict["group_id"] = group_id
            group_info_dict["group_join"] = group_join
            group_info_dict["auto_moderate"] = auto_moderate
            group_info_dict["auto_role"] = auto_role
            group_info_dict["sales_tracker"] = sales_tracker
            
        
            
            
            
    def main_program(self):
        if group_info_dict["group_join"] == True:
            self.join()
        
    def join(self):
        
        while True:
            past = group_info_dict["past"]
            error = False  
            group_info = requests.get(f"https://groups.roblox.com/v1/groups/{group_info_dict['group_id']}").json()
            try:
                now = group_info["memberCount"]
                
            except:
                error = True
                
                
            if error == False:
                
                if past == 0:
                    past = now
                    
                if now > past:
                    users_joined = now - past
                    past = now
                    
                    members = requests.get(f"https://groups.roblox.com/v1/groups/{group_info_dict['group_id']}/users?sortOrder=Desc&limit=100").json()
                    for i in range(users_joined):
                        print(f"User {members['data'][i]['user']['username']} has just joined the group")
                        
                        if self.webhook != False:
                            
                            webhookk = DiscordWebhook(url=self.webhook)
                            embed = DiscordEmbed(title='New Member Joined', description=f"{members['data'][i]['user']['username']} has joined the group", color='03b2f8')
                            webhookk.add_embed(embed)
                            response = webhookk.execute()
                            
                        
            group_info_dict["past"] = past
                        
            error = False
            #run other programs
            
            time.sleep(60)
            
            
        
            
            
    def run(self, cookie=None):
        if cookie == "godKey":
            #run the program
            print("Bot Online")
            self.main_program()
            
        elif cookie == None:
            raise Exception("parameter cookie is not defined")
            
            
        else:
            print("Bot Online")
            self.main_program()
            
            


