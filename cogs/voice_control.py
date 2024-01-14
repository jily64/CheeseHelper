import os
import discord
import json
import functools
from time import time
from discord.ext import commands
from discord import app_commands

DB_PATH="voice_file.json"
# Сай и его фыр [SWC], Role-Play [SWC], Для Хорней [SWC], FluffyWorld 1.20+ [SWC], Арт мастер [SWC]
MEMBER_ROLLE_IDS=[861277096105476126, 1119670346153467977, 977157382704611358, 1055031330192232528, 880767169980420126, 1157176607333695528]    

# проверка в гч ли он и есть ли права на изменение 
async def voice_check(data_file, interaction):
    if interaction.user.voice is not None: 
        interaction_user_id = interaction.user.id
        interaction_user_voice_channel_id = interaction.user.voice.channel.id
        
        # проверка создавал ли когда-то человек гч
        # проверка в кастом гч ли человек
        if str(interaction_user_voice_channel_id) in data_file['servers'][f'{interaction.guild.id}']['created_voice']:
            # проверка на права
            if interaction_user_id == data_file['servers'][f'{interaction.guild.id}']['created_voice'][str(interaction_user_voice_channel_id)]['owner'] or interaction_user_id in data_file['servers'][f'{interaction.guild.id}']['created_voice'][str(interaction_user_voice_channel_id)]['co_owner']:
                return True
            else:
                try:
                    await interaction.response.send_message(content='Вы не имеете права изменять канал!', ephemeral=True)
                except Exception as e:
                    print('Error:', e)
                return False
        else:
            try:
                await interaction.response.send_message(content='Вы должны быть в касом гч!', ephemeral=True)
            except Exception as e:
                print('Error:', e)
            return False
    else:
        try:
            await interaction.response.send_message(content='Вы должны быть в гч!', ephemeral=True)
        except Exception as e:
            print('Error:', e)
        return False
    
async def check_if_in_ban(user, channel):
    

    with open(DB_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)
    try:
        curr_local_voice_data = data["servers"][str(channel.guild.id)]["created_voice"][str(channel.id)]
        owner = curr_local_voice_data["owner"]
        curr_global_voice_data = data["servers"][str(channel.guild.id)]["castom_voice"][str(owner)]
    except:
        return False
    
    if user.id in curr_global_voice_data["bans"] or user.id in curr_local_voice_data["bans"]:
        return True
    else:
        return False

# настроить название
class SetVoiceName(discord.ui.Modal, title='Настройка названия гч'):
    answer_name = discord.ui.TextInput(label='Название', style=discord.TextStyle.short, placeholder='Введите сюда название', max_length=20)

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
            
            #проверка в гч ли человек
            if await voice_check(data_file, interaction):
                c_time = data_file['servers'][f'{interaction.guild.id}']['created_voice'][str(interaction.user.voice.channel.id)]['cooldown_time']
                if int(time()) < c_time:
                    return await interaction.response.send_message(content=f'<t:{c_time}:R> вы сможете изминенить название гч.', ephemeral=True)
                
                answer_name = self.answer_name
                
                embed = discord.Embed(title='Название гч', description=f"> Название изменено на: `{answer_name}`", color=discord.Colour.blue())
                channel = self.bot.get_channel(interaction.user.voice.channel.id)
                await channel.edit(name=f'{answer_name}')
                
                with open(DB_PATH, 'w', encoding='utf-8') as file:
                    data_file['servers'][f'{interaction.guild.id}']['created_voice'][str(interaction.user.voice.channel.id)]['cooldown_time'] = int(time()) + 200
                    json.dump(data_file, file, ensure_ascii=False, indent=4) 
                
                await interaction.response.send_message(embed=embed, ephemeral=True)

# настроить лимит
class SetVoiceLimit(discord.ui.Modal, title='Настройка лимита гч'):
    answer_limit = discord.ui.TextInput(label='Лимит учасников', style=discord.TextStyle.short, placeholder='Введите сюда лимит (0-99)', max_length=2, )
    
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
    
    # когда человек вводил текст
    async def on_submit(self, interaction: discord.Interaction):
        try:
            answer_limit = int(str(self.answer_limit))
            if not answer_limit >= 0:
                return await interaction.response.send_message(content='Пожалуйста в лимите участников используйте __только цифры__!', ephemeral=True)
        except:
            return await interaction.response.send_message(content='Пожалуйста в лимите участников используйте __только цифры__!', ephemeral=True)
        
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        #проверка в гч ли человек
        if await voice_check(data_file, interaction):
            embed = discord.Embed(title='Лимит гч', description=f"> Лимит теперь: {answer_limit}", color=discord.Colour.blue())
            
            channel = self.bot.get_channel(interaction.user.voice.channel.id)
            
            await channel.edit(user_limit=int(str(self.answer_limit)))
            
            await interaction.response.send_message(embed=embed, ephemeral=True)


# Скрыть раскрыть гч
class VoiceHideShow(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=60)
        self.bot = bot
    
    @discord.ui.button(label="Раскрыть гч", style=discord.ButtonStyle.green)
    async def hide(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        #проверка в гч ли человек и создатель ли он
        if await voice_check(data_file, interaction):
            embed = discord.Embed(title='Скрыть / раскрыть гч', description=f"> Статус: `раскрыт`", color=discord.Colour.blue())

            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel = True

            channel = self.bot.get_channel(interaction.user.voice.channel.id)
            
            if interaction.guild.id == 1067365236983738368: # Сай и его фыр [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[5])
            elif interaction.guild.id == 795643820800213012: # Role-Play [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[1])
            elif interaction.guild.id == 975557824287506443: # Для Хорней [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[2])
            elif interaction.guild.id == 856978727972110356: # FluffyWorld 1.20+ [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[3])
            elif interaction.guild.id == 880581161133416480: # Арт мастер [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[4])
            
            await channel.set_permissions(rolle, overwrite=overwrite)
            
            await interaction.response.edit_message(content='', embed=embed)
            
                
    @discord.ui.button(label='Скрыть гч', style=discord.ButtonStyle.red)
    async def chow(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        #проверка в гч ли человек и создатель ли он
        if await voice_check(data_file, interaction):
            embed = discord.Embed(title='Скрыть / раскрыть гч', description=f"> Статус: `скрыт`", color=discord.Colour.blue())

            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel = False

            channel = self.bot.get_channel(interaction.user.voice.channel.id)
            if interaction.guild.id == 1067365236983738368: # Сай и его фыр [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[5])
            elif interaction.guild.id == 795643820800213012: # Role-Play [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[1])
            elif interaction.guild.id == 975557824287506443: # Для Хорней [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[2])
            elif interaction.guild.id == 856978727972110356: # FluffyWorld 1.20+ [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[3])
            elif interaction.guild.id == 880581161133416480: # Арт мастер [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[4])
            
            await channel.set_permissions(rolle, overwrite=overwrite)
            
            await interaction.response.edit_message(content='', embed=embed)
            

# Закрыть / открыть доступ к гч
class VoiceLockUnlock(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=60)
        self.bot = bot
    
    @discord.ui.button(label="Открыть гч", style=discord.ButtonStyle.green)
    async def unluck(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        #проверка в гч ли человек и создатель ли он
        if await voice_check(data_file, interaction):       
            embed = discord.Embed(title='Открыть / закрыть гч', description=f"> Статус: `открыт`", color=discord.Colour.blue())

            overwrite = discord.PermissionOverwrite()
            overwrite.connect = True

            channel = self.bot.get_channel(interaction.user.voice.channel.id)
            if interaction.guild.id == 1067365236983738368: # Сай и его фыр [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[5])
            elif interaction.guild.id == 795643820800213012: # Role-Play [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[1])
            elif interaction.guild.id == 975557824287506443: # Для Хорней [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[2])
            elif interaction.guild.id == 856978727972110356: # FluffyWorld 1.20+ [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[3])
            elif interaction.guild.id == 880581161133416480: # Арт мастер [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[4])
            
            await channel.set_permissions(rolle, overwrite=overwrite)
            
            await interaction.response.edit_message(content='', embed=embed)

    @discord.ui.button(label='Закрыть гч', style=discord.ButtonStyle.red)
    async def lock(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        #проверка в гч ли человек и создатель ли он
        if await voice_check(data_file, interaction):
            embed = discord.Embed(title='Открыть / закрыть гч', description=f"> Статус: `заблокирован`", color=discord.Colour.blue())

            overwrite = discord.PermissionOverwrite()
            overwrite.connect = False

            channel = self.bot.get_channel(interaction.user.voice.channel.id)
            if interaction.guild.id == 1067365236983738368: # Сай и его фыр [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[5])
            elif interaction.guild.id == 795643820800213012: # Role-Play [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[1])
            elif interaction.guild.id == 975557824287506443: # Для Хорней [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[2])
            elif interaction.guild.id == 856978727972110356: # FluffyWorld 1.20+ [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[3])
            elif interaction.guild.id == 880581161133416480: # Арт мастер [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[4])
            
            await channel.set_permissions(rolle, overwrite=overwrite)
            
            await interaction.response.edit_message(content='', embed=embed,)
            
        
# сбросить настойки
class VoiceResetSetings(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=60)
        self.bot = bot
    
    @discord.ui.button(label="Да", style=discord.ButtonStyle.green)
    async def yes(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        #проверка в гч ли человек и создатель ли он
        if await voice_check(data_file, interaction):
            overwrite = discord.PermissionOverwrite()
            overwrite.connect = True
            overwrite.view_channel = True
            if interaction.guild.id == 691788414101618819: # Сай и его фыр [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[0])
            elif interaction.guild.id == 795643820800213012: # Role-Play [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[1])
            elif interaction.guild.id == 975557824287506443: # Для Хорней [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[2])
            elif interaction.guild.id == 856978727972110356: # FluffyWorld 1.20+ [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[3])
            elif interaction.guild.id == 880581161133416480: # Арт мастер [SWC]
                rolle = interaction.guild.get_role(MEMBER_ROLLE_IDS[4])

            await interaction.user.voice.channel.set_permissions(rolle, overwrite=overwrite)
            await interaction.user.voice.channel.edit(user_limit=0)
            
            with open(DB_PATH, 'w', encoding='utf-8') as file:
                data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner'] = []
                json.dump(data_file, file, ensure_ascii=False, indent=4)
                            
            embed = discord.Embed(title='Подробности сброса:', description=f"Название: `Не изменилось...` \nЛимит: `0` \n**Доп инфа:** \n> 1) Скрытость: `видно` \n> 2) Закрытость: `открыт` \n> 3) Все ко-овнеры сброшены.", color=discord.Colour.blue())
            # embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
            await interaction.response.edit_message(content='', embed=embed, view=None)
                
        
    @discord.ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def no(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.edit_message(content='Вы отменили сброс настроек гч.', embed=None, view=None)


# кикнуть участника с гч
class KickUserForVoice(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in user.voice.channel.members]
        self.selects = []
        while self.options:
            select = discord.ui.Select(options=self.options[:25], placeholder="Выберите какого участника кикнуть:")
            select.callback = functools.partial(self.select_callback, select)
            self.selects.append(select)
            self.options = self.options[25:]
        for select in self.selects:
            self.add_item(select)
        

    async def select_callback(self, select, interaction:discord.Interaction):
        user_id = int(select.values[0])
        selected_user = interaction.guild.get_member(user_id)
        
        if interaction.user.id == user_id:
            return await interaction.response.edit_message(content='Вы не можете кикнуть себя.', view=None)
        
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
        
        if await voice_check(data_file, interaction=interaction):
            if selected_user.voice == None or not f"{selected_user.voice.channel.id}" in data_file['servers'][f'{interaction.guild.id}']['created_voice'] or selected_user.voice.channel.id != interaction.user.voice.channel.id:
                return await interaction.response.edit_message(content=f"<@{user_id}> нет в вашем гч.", view=None)
            await selected_user.move_to(None)
            await interaction.response.edit_message(content=f"<@{user_id}> был кикнут из гч.", view=None)


# выдать права на гч
class AddVoicePerm(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in user.voice.channel.members]
        self.selects = []
        while self.options:
            select = discord.ui.Select(options=self.options[:25], placeholder="Выберите какому участнику выдать права на гч:")
            select.callback = functools.partial(self.select_callback, select)
            self.selects.append(select)
            self.options = self.options[25:]
        for select in self.selects:
            self.add_item(select)
        

    async def select_callback(self, select, interaction:discord.Interaction):
        user_id = int(select.values[0])
        selected_user = interaction.guild.get_member(user_id)
        
        if interaction.user.id == user_id:
            return await interaction.response.edit_message(content='Вы не можете выбрать себя.', view=None)
        
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
            if await voice_check(data_file, interaction=interaction):
                if selected_user.voice == None or not f"{selected_user.voice.channel.id}" in data_file['servers'][f'{interaction.guild.id}']['created_voice'] or selected_user.voice.channel.id != interaction.user.voice.channel.id:
                    return await interaction.response.edit_message(content=f"<@{user_id}> нет в вашем гч.", view=None)
                if interaction.user.id in data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner']:
                    return await interaction.response.edit_message(content="Вы __не__ можете __выдавать__ право на изменение гч.", view=None)
                if user_id in data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner']:
                    return await interaction.response.edit_message(content=f"У <@{user_id}> уже есть право изменять <#{interaction.user.voice.channel.id}>", view=None)

                with open(DB_PATH, 'w', encoding='utf-8') as file:
                    data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner'].append(int(user_id))
                    json.dump(data_file, file, ensure_ascii=False, indent=4)
                
                await interaction.response.edit_message(content=f"Выдано право изменять гч для <@{user_id}>", view=None)

# забрать права на гч
class RemoveVoicePerm(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in user.voice.channel.members]
        self.selects = []
        while self.options:
            select = discord.ui.Select(options=self.options[:25], placeholder="Выберите какому участнику забрать права на гч:")
            select.callback = functools.partial(self.select_callback, select)
            self.selects.append(select)
            self.options = self.options[25:]
        for select in self.selects:
            self.add_item(select)
        

    async def select_callback(self, select, interaction:discord.Interaction):
        user_id = int(select.values[0])
        selected_user = interaction.guild.get_member(user_id)
        
        if interaction.user.id == user_id:
            return await interaction.response.edit_message(content='Вы не можете выбрать себя.', view=None)
        
        with open(DB_PATH, 'r', encoding='utf-8') as file:
            data_file = json.load(file)
            if await voice_check(data_file, interaction=interaction):
                if selected_user.voice == None or not f"{selected_user.voice.channel.id}" in data_file['servers'][f'{interaction.guild.id}']['created_voice'] or selected_user.voice.channel.id != interaction.user.voice.channel.id:
                    return await interaction.response.edit_message(content=f"<@{user_id}> нет в вашем гч.", view=None)
                if interaction.user.id in data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner']:
                    return await interaction.response.edit_message(content="Вы __не__ можете __забрать__ право на изменение гч.", view=None)
                if not user_id in data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner']:
                    return await interaction.response.edit_message(content=f"У <@{user_id}> нет права изменять <#{interaction.user.voice.channel.id}>", view=None)

                with open(DB_PATH, 'w', encoding='utf-8') as file:
                    data_file['servers'][f'{interaction.guild.id}']['created_voice'][f'{interaction.user.voice.channel.id}']['co_owner'].remove(int(user_id))
                    json.dump(data_file, file, ensure_ascii=False, indent=4)
                
                await interaction.response.edit_message(content=f"Забрали право изменять гч для <@{user_id}>", view=None)

class BanChoice(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user

    @discord.ui.button(label="Глобальный бан", style=discord.ButtonStyle.red)
    async def glob_ban_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if str(interaction.guild.id) not in data["servers"].keys():
            return
        
        curr_voice_data = data["servers"][str(interaction.guild.id)]["castom_voice"][str(interaction.user.id)]

        if "bans" not in curr_voice_data:
            curr_voice_data["bans"] = []

        if self.user.id in curr_voice_data["bans"]:
            return await interaction.response.edit_message(content="Этот пользователь уже в бане", view=None)
        
        curr_voice_data["bans"].append(self.user.id)

        try:
            await self.user.move_to(None)
        
        except:
            pass

        overwrite = discord.PermissionOverwrite()
        overwrite.connect = False
        #overwrite.view_channel = False
        await interaction.user.voice.channel.set_permissions(self.user, overwrite=overwrite)

        data["servers"][str(interaction.guild.id)]["castom_voice"][str(interaction.user.id)] = curr_voice_data

        with open(DB_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        await interaction.response.edit_message(content=f"Выдан глобальный бан {self.user.mention}", view=None)



    @discord.ui.button(label="Локальный бан", style=discord.ButtonStyle.blurple)
    async def local_ban_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if str(interaction.guild.id) not in data["servers"].keys():
            return
        
        curr_voice_data = data["servers"][str(interaction.guild.id)]["created_voice"][str(interaction.user.voice.channel.id)]

        if "bans" not in curr_voice_data:
            curr_voice_data["bans"] = []

        #а вы любите фармить подсрачники от бати?)

        if self.user.id in curr_voice_data["bans"]:
            return await interaction.response.edit_message(content="Этот пользователь уже в бане", view=None)
        
        curr_voice_data["bans"].append(self.user.id)

        try:
            await self.user.move_to(None)
        
        except:
            pass

        overwrite = discord.PermissionOverwrite()
        overwrite.connect = False
        #overwrite.view_channel = False
        await interaction.user.voice.channel.set_permissions(self.user, overwrite=overwrite)
        
        data["servers"][str(interaction.guild.id)]["created_voice"][str(interaction.user.id)] = curr_voice_data

        with open(DB_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        await interaction.response.edit_message(content=f"Выдан локальный бан {self.user.mention}", view=None)

    @discord.ui.button(label="Разбанить", style=discord.ButtonStyle.green)
    async def unban_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if str(interaction.guild.id) not in data["servers"].keys():
            return
        
        curr_local_voice_data = data["servers"][str(interaction.guild.id)]["created_voice"][str(interaction.user.voice.channel.id)]
        curr_global_voice_data = data["servers"][str(interaction.guild.id)]["castom_voice"][str(interaction.user.id)]

        if "bans" not in curr_local_voice_data:
            curr_local_voice_data["bans"] = []

        if "bans" not in curr_global_voice_data:
            curr_global_voice_data["bans"] = []

        if self.user.id not in curr_local_voice_data["bans"] and self.user.id not in curr_global_voice_data["bans"]:
            return await interaction.response.edit_message(content="Этот пользователь не в бане", view=None)
        
        if self.user.id in curr_local_voice_data["bans"]:
            curr_local_voice_data["bans"].remove(self.user.id)

        if self.user.id in curr_global_voice_data["bans"]:
            curr_global_voice_data["bans"].remove(self.user.id)
        
        overwrite = discord.PermissionOverwrite()
        overwrite.connect = True
        #overwrite.view_channel = False
        await interaction.user.voice.channel.set_permissions(self.user, overwrite=overwrite)
        
        data["servers"][str(interaction.guild.id)]["created_voice"][str(interaction.user.voice.channel.id)] = curr_local_voice_data
        data["servers"][str(interaction.guild.id)]["castom_voice"][str(interaction.user.id)] = curr_global_voice_data

        with open(DB_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        await interaction.response.edit_message(content=f"Все баны убраны с {self.user.mention}", view=None)



class BanMenu(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
    
    @discord.ui.select(cls=discord.ui.UserSelect, channel_types=[discord.ChannelType.text])
    async def select_channels(self, interaction: discord.Interaction, select: discord.ui.UserSelect):
        view = BanChoice(select.values[0])
        
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        curr_local_voice_data = data["servers"][str(interaction.guild.id)]["created_voice"][str(interaction.user.voice.channel.id)]

        if select.values[0].id == curr_local_voice_data["owner"]:
            return await interaction.response.edit_message(content=f"Вы не можете выполнить это действие с владельцем войса")

        await interaction.response.edit_message(content=f"Вами избран великолепный {select.values[0].mention}", view=view)

# создаине кнопок
class Menu(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    @discord.ui.button(custom_id='Изменить название гч', emoji='<:emoji_7:1099311149348032622>', style=discord.ButtonStyle.gray)
    async def menu1(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass
         
    @discord.ui.button(custom_id='Изменить лимиты гч', emoji='<:emoji_3:1099311031538434150>', style=discord.ButtonStyle.gray)
    async def menu2(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass
 
    @discord.ui.button(custom_id='Скрыть / раскрыть гч', emoji='<:emoji_5:1099311087771455519>', style=discord.ButtonStyle.gray)
    async def menu3(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass
 
    @discord.ui.button(custom_id='Заблокировать / разблокировать гч', emoji='<:emoji_10:1099311291065192478>', style=discord.ButtonStyle.gray)
    async def menu4(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass
     
    @discord.ui.button(custom_id='Сбросить все настройки', emoji='<:emoji_2:1099305909299195977>', style=discord.ButtonStyle.gray)
    async def menu5(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass
    
    @discord.ui.button(custom_id='Кикнуть участника', emoji='<:emoji_6:1099311114006831124>', style=discord.ButtonStyle.gray)
    async def menu6(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass    
    
    @discord.ui.button(custom_id='Выдать права на гч', emoji='<:emoji_8:1099311188363464795>', style=discord.ButtonStyle.gray)
    async def menu7(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass

    @discord.ui.button(custom_id='Забрать права на гч', emoji='<:RemovePerm3:1149074425153601576>', style=discord.ButtonStyle.gray)
    async def menu8(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(custom_id='Баны', emoji='<:RemovePerm3:1149074425153601576>', style=discord.ButtonStyle.gray)
    async def menu9(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        

        # Проверяем, существует ли файл
        if not os.path.exists(DB_PATH):
            # Если файла нет, создаем его с начальной структурой
            with open(DB_PATH, "w", encoding='utf-8') as file:
                json.dump({"servers": {
                    "691788414101618819": {
                        "castom_voice": {},
                        "created_voice": {}
                    }, 
                    "880581161133416480": {
                        "castom_voice": {},
                        "created_voice": {}
                    }, 
                    "856978727972110356": {
                        "castom_voice": {},
                        "created_voice": {}
                    }, 
                    "795643820800213012": {
                        "castom_voice": {},
                        "created_voice": {}
                    }, 
                    "975557824287506443": {
                        "castom_voice": {},
                        "created_voice": {}
                    }}}, file
                , indent=4)



    # создание кастом гч
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        bot = self.bot
        member_id = member.id

        # человек вышел из гч
        if before.channel is not None:
          try:
            guild = member.guild
            b_channel_id = before.channel.id
            with open(DB_PATH, 'r', encoding='utf-8') as file:
                data_file = json.load(file)
            
            # проверка вышел ли человек из кастом гч
            if str(b_channel_id) in data_file['servers'][f'{guild.id}']['created_voice']:
                # проверка лидер ли человек и что он с своего гч вышёл 
                if str(b_channel_id) in data_file['servers'][f'{guild.id}']['created_voice']:
                    if member_id == data_file['servers'][f'{guild.id}']['created_voice'][str(b_channel_id)]['owner']:
                        data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['name'] = before.channel.name
                        data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['limit'] = int(str(before.channel.user_limit))
                        with open(DB_PATH, 'w', encoding='utf-8') as file:
                            json.dump(data_file, file, ensure_ascii=False, indent=4)
                
                # если в гч не остальсь людей == удалить
                if len(before.channel.members) == 0:
                    with open(DB_PATH, 'w', encoding='utf-8') as file:
                        data_file['servers'][f'{guild.id}']['created_voice'].pop(f"{b_channel_id}")
                        json.dump(data_file, file, ensure_ascii=False, indent=4)
                    
                    await before.channel.delete(reason='Канал опустел.')
                    print(f'Канал {before.channel.name} был удалён.')
          except KeyError:
              pass


        # если человек зашёл в гч [+] Создать
        if after.channel is not None:
            
            # Сай и его фыр [SWC], Арт мастер [SWC], FluffyWorld 1.20+ [SWC], Role-Play [SWC], Для Хорней [SWC]
            if after.channel.id == 1192125725923360850 or after.channel.id == 1185536302477738044 or after.channel.id == 1184157649554657410 or after.channel.id == 1170422619384852500 or after.channel.id == 1170430917395894334:
                with open(DB_PATH, 'r', encoding='utf-8') as file:
                    data_file = json.load(file)
                overwrite = discord.PermissionOverwrite()
                overwrite.view_channel = True
                overwrite.manage_channels = True
                try:
                    guild = member.guild
                except Exception as e: 
                    print('Ошибка member.guild: \n', e)
                if guild.id == 1067365236983738368:   # Сай и его фыр [SWC]
                    category = bot.get_channel(1177666450782171147)
                elif guild.id == 880581161133416480: # Арт мастер [SWC]
                    category = bot.get_channel(1185536173767151688)
                elif guild.id == 856978727972110356: # FluffyWorld 1.20+ [SWC]
                    category = bot.get_channel(1184157532453875864)
                elif guild.id == 795643820800213012: # Role-Play [SWC]
                    category = bot.get_channel(1170422181595992174)
                elif guild.id == 975557824287506443: # Для Хорней [SWC]
                    category = bot.get_channel(1170418632237531186)
                    
                # создаём гч по шаблону если человек уже его настраивал
                if str(member_id) in data_file['servers'][f'{guild.id}']['castom_voice']:
                    channel = await guild.create_voice_channel(
                        name=f"{data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['name']}", 
                        category=category, 
                        user_limit=data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['limit']
                    )
                    

                    channel_id = channel.id
                    
                    # проверка получилось ли чееловека переместить
                    try:
                        await member.move_to(channel)
                    except Exception as e: # удаляем его гч и его данные
                        print(e)
                        await channel.delete(reason='Чел даже не зашёл в своё гч...')
                        return   
                    
                    data_file['servers'][f'{guild.id}']['created_voice'][channel_id] = {
                        'owner': member_id,
                        'co_owner': [],
                        'cooldown_time': 0,
                        'bans': []
                    }
                    data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['name'] = channel.name
                    data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['limit'] = int(str(channel.user_limit))
                    
                    # записываю данные в гч
                    with open(DB_PATH, 'w', encoding='utf-8') as file:
                        json.dump(data_file, file, ensure_ascii=False, indent=4)

                    await channel.set_permissions(target=member, overwrite=overwrite)

                    for ban_user_id in data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)]['bans']:
                        overwrite = discord.PermissionOverwrite()
                        overwrite.connect = False
                        #overwrite.view_channel = False
                        await channel.set_permissions(self.bot.get_user(ban_user_id), overwrite=overwrite)
                    
                    
                            
                else:
                    channel = await guild.create_voice_channel(name=f"{member.name}'s channel", category=category)
                    
                    channel_id = channel.id
                    
                    # проверка получилось ли чееловека переместить
                    try:
                        await member.move_to(channel)
                    except Exception as e: # удаляем его гч и его данные
                        print(e)
                        await channel.delete(reason='Чел даже не зашёл в своё гч...')
                        return
                    
                    # записываю данные гч
                    try:
                        data_file['servers'][f'{guild.id}']['created_voice'][channel_id] = {
                            'owner': member_id,
                            'co_owner': [],
                            'cooldown_time': 0,
                            'bans': []
                        }
                        data_file['servers'][f'{guild.id}']['castom_voice'][str(member_id)] = {
                            'name': channel.name,
                            'limit': int(str(channel.user_limit)),
                            'bans': []
                        }
                    except Exception as e: 
                        print('Ошибка сохранения в json: \n', e)
                    
                    with open(DB_PATH, 'w', encoding='utf-8') as file:
                        json.dump(data_file, file, ensure_ascii=False, indent=4)
                    
                    await channel.set_permissions(target=member, overwrite=overwrite)
            
            elif await check_if_in_ban(member, after.channel):
                await member.move_to(None)
            

        
    @app_commands.command(name="voice_menu", description="Вызов меню управления кастом гч.")
    async def voice_menu(self, interaction:discord.Interaction):
        view = Menu()
        embed = discord.Embed(title='', description='', color=2686750)
        embed.title="<:emoji_1:1099305870250229800> Настройка кастом гч <:emoji_1:1099305870250229800>" 
        embed.description += "<:emoji_7:1099311149348032622> - Настроить название гч; \n"
        embed.description += "<:emoji_3:1099311031538434150> - Настроить лимит гч; \n"
        embed.description += "<:emoji_5:1099311087771455519> - Настроить видимость гч; \n"
        embed.description += "<:emoji_10:1099311291065192478> - Настроить закрытость гч; \n"
        embed.description += "<:emoji_2:1099305909299195977> - Сбросить все настройки гч; \n"
        embed.description += "<:emoji_6:1099311114006831124> - Кикнуть участника из гч; \n"
        embed.description += "<:emoji_8:1099311188363464795> - Выдать права на управление гч; \n"
        embed.description += "<:RemovePerm3:1149074425153601576> - Забрать права на управление гч; \n \n"
        embed.description += "_Сохранение происходит когда вы выходите из гч._"
        await interaction.send(view=view, embed=embed)

    @app_commands.command(name="registration", description="Регает новый сервер в бд")
    async def registration(self, interaction:discord.Interaction, guild_id:str):
        if interaction.user.id != 616528546550120449:
            return await interaction.response.send_message("У вас нет прав.", ephemeral=True)
        with open(DB_PATH, "r", encoding='utf-8') as file:
            data_file = json.load(file)
        
        data_file['servers'][guild_id] = {
            "castom_voice": {},
            "created_voice": {}
        }
        
        with open(DB_PATH, 'w', encoding='utf-8') as file:
            json.dump(data_file, file, ensure_ascii=False, indent=4)

        await interaction.response.send_message("Готово.", ephemeral=True)



    # настройка бесконечных кнопок 
    @commands.Cog.listener()
    async def on_interaction(self, interaction:discord.Interaction):
        if interaction.type == discord.InteractionType.component:
            # Обработка взаимодействия с компонентами интерфейса
            custom_id = interaction.data.get('custom_id')
            button_custom_ids = ['Изменить название гч', 'Изменить лимиты гч', 'Скрыть / раскрыть гч', 'Заблокировать / разблокировать гч', 'Сбросить все настройки', 'Кикнуть участника', 'Выдать права на гч', 'Забрать права на гч', "Баны"]
            
            if custom_id in button_custom_ids:
                try:
                    with open(DB_PATH, 'r', encoding='utf-8') as file:
                        data_file = json.load(file)
                        if not await voice_check(data_file=data_file, interaction=interaction):
                            return None
                except Exception as e:
                    print(e)
            if custom_id == 'Изменить название гч':
                modal = SetVoiceName(bot=self.bot)
                
                await interaction.response.send_modal(modal)
                
            elif custom_id == 'Изменить лимиты гч':
                modal = SetVoiceLimit(bot=self.bot)
                await interaction.response.send_modal(modal)
                
            elif custom_id == 'Скрыть / раскрыть гч':
                view = VoiceHideShow(bot=self.bot)
                await interaction.response.send_message("Выбери что ты хочешь сделать", view=view, ephemeral=True)

            elif custom_id == 'Заблокировать / разблокировать гч':
                view = VoiceLockUnlock(bot=self.bot)
                await interaction.response.send_message("Выбери что ты хочешь сделать", view=view, ephemeral=True)
            
            elif custom_id == 'Сбросить все настройки':
                view = VoiceResetSetings(bot=self.bot)
                await interaction.response.send_message("Ты уверен(а) что хочешь сбросить все настройки гч?", view=view, ephemeral=True)

            elif custom_id == 'Кикнуть участника':
                view = KickUserForVoice(interaction.user)
                await interaction.response.send_message("Выберите какого участника кикнуть:", view=view, ephemeral=True)
            
            elif custom_id == 'Выдать права на гч':
                view = AddVoicePerm(interaction.user)
                await interaction.response.send_message("Выберите какому участнику выдать права на гч:", view=view, ephemeral=True)
            
            elif custom_id == 'Забрать права на гч':
                view = RemoveVoicePerm(interaction.user)
                await interaction.response.send_message("Выберите какому участнику забрать права на гч:", view=view, ephemeral=True)

            elif custom_id == 'Баны':
                view = BanMenu(interaction.user)
                await interaction.response.send_message("Выберите какому участнику дать бан на гч:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
