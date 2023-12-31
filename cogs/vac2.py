import discord
import discord.ui
from discord.ext import commands
from discord import app_commands
import json
import asyncio

class var:
    # bot = None
    path = "test.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            pass
    except:
        with open(path, "w") as f:
            f.write("{}")
    def __init__(self, bot):
        self.bot = bot
        print("#[VacV2 Logs]: Loaded")
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    async def load_messages(self):
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        for i in self.data:
            for j in self.data[i]:
                channel = self.bot.get_channel(self.data[i][j]["chan"])
                if channel != None:
                    try:
                        mess = await channel.fetch_message(self.data[i][j]["mess"])
                    except:
                        mess = None
                    if mess != None:
                        self.i = i

                        class start_questionary(discord.ui.View):
                            i = self.i
                            bot = self.bot
                            guild = channel.guild
                            with open(var.path, "r", encoding="utf-8") as f:
                                data = json.load(f)

                            @discord.ui.button(label="Ответить на вопросы",
                                               style=discord.ButtonStyle.blurple,
                                               custom_id=f"{i}<!>{j}",
                                               disabled=not data[str(self.i)][j]["in_use"])
                            async def start_button_callback(self, interaction: discord.Interaction, button: discord.Button):
                                await interaction.response.send_message(content="Проверьте лс.", ephemeral=True)

                                user_answers = []
                                dats = button.custom_id.split("<!>")
                                for g in range(len(self.data[str(dats[0])][dats[1]]["que"])):
                                    try:
                                        await interaction.user.send(self.data[dats[0]][dats[1]]["que"][g])
                                    except:
                                        await interaction.edit_original_response(content="У вас закрыт лс. Откройте его, чтобы получить список вопросов.")
                                        break
                                    try:
                                        response = await self.bot.wait_for('message', check=lambda
                                            m: m.author == interaction.user and m.channel.id == interaction.user.dm_channel.id, timeout=300)

                                        if response.content:
                                            print(response.content, "content")
                                            user_answers.append(response.content)
                                        else:
                                            await interaction.user.send(f"Файлы, голосовые и картинки не принимаются. \nТеперь перепроходи все заново)")
                                            return

                                    except asyncio.TimeoutError:
                                        await interaction.user.send(f"Время на вопрос вышло.")
                                        return

                                await interaction.user.send(f"Спасибо за подачу заявки! В скором времени она будет рассмотрена.")

                                user = self.guild.get_member(int(dats[0]))

                                # print(user_answers)

                                ans = ""
                                out_chan = user

                                out_chan = interaction.guild.get_channel(self.data[dats[0]][dats[1]]["out_chan"])
                                if out_chan == None:
                                    print("Th")
                                    out_chan = interaction.guild.get_thread(self.data[dats[0]][dats[1]]["out_chan"])
                                    if out_chan == None:
                                        out_chan = user

                                for i in range(len(user_answers)):
                                    ans += f"{i + 1}. {self.data[dats[0]][dats[1]]['que'][i]} ```{user_answers[i]}``` \n"
                                embed = discord.Embed(title='', description="", color=16762880)
                                embed.description += f"## Пришла новая заявка! \n"
                                embed.description += f"Пользователь: {interaction.user.mention} \n"
                                embed.description += f"Категория: `{dats[1]}` \n{ans}"
                                embed.set_author(name=interaction.user.display_name,
                                                 icon_url=interaction.user.avatar.url)
                                await out_chan.send(embed=embed)

                        emb = discord.Embed(title=f"{j}", description=self.data[str(i)][j]["description"])
                        await mess.edit(embed=emb, view=start_questionary())

class vac(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open(var.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
    
    @commands.Cog.listener()
    async def on_ready(self):
        var.bot = self.bot
        loader = var(self.bot)
        await loader.load_messages()
        
    @app_commands.command(name="vac-users", description="Настроте пользователей, которые могут пользоваться Vac2")
    async def vac_users(self, ctx:discord.Interaction):

        class view(discord.ui.View):
            @discord.ui.button(label="Добавить пользователя", style=discord.ButtonStyle.blurple)
            async def add_callback(self, interaction: discord.Interaction, button):
                class id_modal(discord.ui.Modal, title="Вставьте ID ользователя"):
                    user_id = discord.ui.TextInput(
                        label="ID",
                        placeholder="",
                        style=discord.TextStyle.short
                    )

                    async def on_submit(self, interaction: discord.Interaction):
                        with open(var.path, "r", encoding="utf-8") as f:
                            self.data = json.load(f)
                        if self.user_id.value in self.data:
                            await interaction.response.send_message("Данный пользователь уже есть в базе данных", ephemeral=True)
                        else:
                            self.data[str(self.user_id.value)] = {}
                            with open(var.path, "w", encoding="utf-8") as f:
                                json.dump(self.data, f, ensure_ascii=False, indent=4)
                            await interaction.response.send_message("Пользователь занесен в базу данных", ephemeral=True)

                await interaction.response.send_modal(id_modal())

            @discord.ui.button(label="Удалить пользователя", style=discord.ButtonStyle.red)
            async def delete_callback(self, interaction:discord.Interaction, button):
                class id_modal(discord.ui.Modal, title="Вставьте ID ользователя"):
                    user_id = discord.ui.TextInput(
                        label="ID",
                        placeholder="",
                        style=discord.TextStyle.short
                    )

                    async def on_submit(self, interaction: discord.Interaction):
                        with open(var.path, "r", encoding="utf-8") as f:
                            self.data = json.load(f)
                        if self.user_id.value in self.data:
                            self.data.pop(str(self.user_id.value))
                            with open(var.path, "w", encoding="utf-8") as f:
                                json.dump(self.data, f, ensure_ascii=False, indent=4)
                            await interaction.response.send_message("Пользователь удален", ephemeral=True)
                        else:
                            await interaction.response.send_message("Нет такого пользователя", ephemeral=True)

                await interaction.response.send_modal(id_modal())


        if ctx.user.guild_permissions.administrator:
            emb = discord.Embed(title="Менеджер пользователей")
            with open(var.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            users = "\n"
            for i in self.data:
                user = self.bot.get_user(int(i))
                users+=f"{user.mention} \n"
            emb.add_field(name="Доступные пользователи:", value=users)
            await ctx.response.send_message(embed=emb, view=view(), ephemeral=True)

        else:
            await ctx.response.send_message("У вас нет прав администратора на данном сервере")

    @app_commands.command(name="vac-menu", description="New Version of Vac")
    async def vacancy_main(self, ctx:discord.Interaction):
        with open(var.path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        if str(ctx.user.id) in self.data:
            emb = discord.Embed(title="Менеджер категорий", description="Добавление / Переименование / Удаление Категорий")
            for i in self.data[str(ctx.user.id)]:
                que = ""
                for j in range(len(self.data[str(ctx.user.id)][i]["que"])):
                    que+=f'{j+1}. {self.data[str(ctx.user.id)][i]["que"][j]} \n'
                if len(que) >= 1000:
                    break
                emb.add_field(name=i, value=f"```{que}```", inline=False)

            class select_category(discord.ui.View):
                with open(var.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    opt=[]
                if len(self.data[str(ctx.user.id)]) != 0:
                    for i in self.data[str(ctx.user.id)]:
                        sel = discord.SelectOption(
                            label=i,
                            description=""
                        )
                        opt.append(sel)

                    @discord.ui.select(options=opt, placeholder="Выбирите нужную категорию")
                    async def select_callback(self, interaction:discord.Interaction, select:discord.ui.Select):
                        class manage_buttons(discord.ui.View):
                            @discord.ui.button(label="Переименовать", style=discord.ButtonStyle.blurple)
                            async def rename_callback(self, interaction: discord.Interaction, button):
                                class rename_modal(discord.ui.Modal, title="Переименование категории"):
                                    feedback = discord.ui.TextInput(
                                        label='Переименование категории',
                                        style=discord.TextStyle.short,
                                        placeholder='Новое название',
                                        required=True,
                                        max_length=100,
                                        default=select.values[0]
                                    )

                                    async def on_submit(self, interaction: discord.Interaction):
                                        with open(var.path, "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        val = self.feedback.value
                                        self.data[str(interaction.user.id)][val] = self.data[str(interaction.user.id)][select.values[0]]
                                        self.data[str(interaction.user.id)].pop(select.values[0])
                                        select.values[0] = val
                                        with open(var.path, "w", encoding="utf-8") as f:
                                            json.dump(self.data, f, ensure_ascii=False, indent=4)
                                        await interaction.response.send_message("Изменения приняты", ephemeral=True)

                                await interaction.response.send_modal(rename_modal())

                            @discord.ui.button(label="Изменить описание", style=discord.ButtonStyle.blurple)
                            async def new_desc_callback(self, interaction:discord.Interaction, button):
                                class rename_modal(discord.ui.Modal, title="Изменение описания категории"):
                                    with open(var.path, "r", encoding="utf-8") as f:
                                        data = json.load(f)
                                    feedback = discord.ui.TextInput(
                                        label='Описание категории',
                                        style=discord.TextStyle.long,
                                        placeholder='Новое описане',
                                        required=True,
                                        max_length=4000,
                                        default=data[str(interaction.user.id)][select.values[0]]["description"]
                                    )

                                    async def on_submit(self, interaction: discord.Interaction):
                                        with open(var.path, "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        val = self.feedback.value
                                        self.data[str(interaction.user.id)][select.values[0]]["description"] = val
                                        with open(var.path, "w", encoding="utf-8") as f:
                                            json.dump(self.data, f, ensure_ascii=False, indent=4)
                                        await interaction.response.send_message("Изменения приняты", ephemeral=True)

                                await interaction.response.send_modal(rename_modal())

                            @discord.ui.button(label="Удалить", style=discord.ButtonStyle.red)
                            async def delete_category(self, interaction:discord.Interaction, button):
                                class confirm_modal(discord.ui.Modal, title="Подтверждение действия"):
                                    con = discord.ui.TextInput(
                                        label=f"Подтверждение удаления категории {select.values[0]}",
                                        placeholder="Имя категории",
                                        style=discord.TextStyle.short,
                                        max_length=100,
                                        required=True
                                    )

                                    async def on_submit(self, interaction:discord.Interaction):
                                        if self.con.value == select.values[0]:
                                            with open(var.path, "r", encoding="utf-8") as f:
                                                self.data = json.load(f)

                                            self.data[str(interaction.user.id)].pop(self.con.value)

                                            with open(var.path, "w", encoding="utf-8") as f:
                                                json.dump(self.data, f, ensure_ascii=False, indent=4)

                                            await interaction.response.send_message("Категория удалена", ephemeral=True)
                                        else:
                                            await interaction.response.send_message("Отклоненно")
                                await interaction.response.send_modal(confirm_modal())

                            @discord.ui.button(label="Изменить вопросы", style=discord.ButtonStyle.blurple)
                            async def change_que_callback(self, interaction: discord.Interaction,
                                                            button: discord.ui.Button):
                                class Feedback(discord.ui.Modal, title=f'Настройка вопросов для {select.values[0]}'):
                                    with open(var.path, "r", encoding="utf-8") as f:
                                        data = json.load(f)
                                    que = ""
                                    for i in range(len(data[str(ctx.user.id)][select.values[0]]["que"])):
                                        que += f'{i + 1}. {data[str(ctx.user.id)][select.values[0]]["que"][i]} \n'

                                    feedback = discord.ui.TextInput(
                                        label='Вопросы',
                                        style=discord.TextStyle.long,
                                        placeholder='Вопросы тут',
                                        required=True,
                                        max_length=4000,
                                        default=que
                                    )

                                    async def on_submit(self, interaction: discord.Interaction):
                                        with open(var.path, "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        val = self.feedback.value
                                        val = val.split("\n")

                                        for i in range(len(val)):
                                            val[i] = "".join(val[i].split(f'{i + 1}. '))

                                        self.data[str(interaction.user.id)][select.values[0]]["que"] = val
                                        print(val)

                                        with open(var.path, "w", encoding='utf-8') as f:
                                            json.dump(self.data, f, ensure_ascii=False, indent=4)
                                        await interaction.response.send_message("Успешно изменено", ephemeral=True)

                                await interaction.response.send_modal(Feedback())

                            if self.data[str(interaction.user.id)][select.values[0]]["in_use"] == True:
                                name = "Закрыть набор"
                            else:
                                name = "Открыть набор"

                            @discord.ui.button(label=name, style=discord.ButtonStyle.green)
                            async def use_switch_callback(self, interaction: discord.Interaction,
                                                            button: discord.ui.Button):
                                with open(var.path, "r", encoding="utf-8") as f:
                                    self.data = json.load(f)
                                self.data[str(interaction.user.id)][select.values[0]]["in_use"] = not self.data[str(interaction.user.id)][select.values[0]]["in_use"]
                                with open(var.path, "w", encoding="utf-8") as f:
                                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                                await interaction.response.send_message("Изменения приняты!", ephemeral=True)

                            @discord.ui.button(label="Назначить канал")
                            async def set_category_channel(self, interaction: discord.Interaction, button):

                                class set_category_channel_modal(discord.ui.Modal,
                                                                 title="Назначение канала для категории"):
                                    chan = discord.ui.TextInput(
                                        label="ID Канала",
                                        placeholder="ID",
                                        required=True,
                                        style=discord.TextStyle.short
                                    )

                                    async def on_submit(self, interaction: discord.Interaction):
                                        val = int(self.chan.value)
                                        with open(var.path, "r", encoding="utf-8") as f:
                                            self.data = json.load(f)

                                        guild = interaction.guild
                                        chan = guild.get_channel(val)
                                        if chan != None:
                                            self.data[str(interaction.user.id)][select.values[0]]["chan"] = int(val)
                                            with open(var.path, "w", encoding="utf-8") as f:
                                                json.dump(self.data, f, ensure_ascii=False, indent=4)
                                            await interaction.response.send_message("Канал успешно изменен",
                                                                                    ephemeral=True)
                                        else:
                                            chan = guild.get_thread(val)
                                            print(chan)
                                            if chan != None:
                                                self.data[str(interaction.user.id)][select.values[0]]["chan"] = int(val)
                                                with open(var.path, "w", encoding="utf-8") as f:
                                                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                                                await interaction.response.send_message("Канал успешно изменен",
                                                                                        ephemeral=True)
                                            else:
                                                await interaction.response.send_message("Канал не найден",
                                                                                        ephemeral=True)

                                await interaction.response.send_modal(set_category_channel_modal())

                            @discord.ui.button(label="Назначить канал для вывода заявок")
                            async def set_out_category_channel(self, interaction: discord.Interaction, button):

                                class set_category_channel_modal(discord.ui.Modal,
                                                                 title="Назначение канала для заявок"):
                                    chan = discord.ui.TextInput(
                                        label="ID Канала",
                                        placeholder="ID",
                                        required=True,
                                        style=discord.TextStyle.short
                                    )

                                    async def on_submit(self, interaction: discord.Interaction):
                                        val = int(self.chan.value)
                                        with open(var.path, "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        if val == 0:
                                            self.data[str(interaction.user.id)][select.values[0]]["out_chan"] = None

                                            await interaction.response.send_message("Теперь заявки будут приходить вам в ЛС.", ephemeral=True)

                                            with open(var.path, "w", encoding="utf-8") as f:
                                                json.dump(self.data, f, ensure_ascii=False, indent=4)

                                            return

                                        else:
                                            guild = interaction.guild
                                            chan = guild.get_channel(val)
                                            if chan != None:
                                                self.data[str(interaction.user.id)][select.values[0]]["out_chan"] = int(val)
                                                with open(var.path, "w", encoding="utf-8") as f:
                                                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                                                await interaction.response.send_message("Канал успешно изменен (Ch)",
                                                                                        ephemeral=True)
                                            else:
                                                chan = guild.get_thread(val)
                                                print(chan)
                                                if chan != None:
                                                    self.data[str(interaction.user.id)][select.values[0]]["out_chan"] = int(val)
                                                    with open(var.path, "w", encoding="utf-8") as f:
                                                        json.dump(self.data, f, ensure_ascii=False, indent=4)
                                                    await interaction.response.send_message("Канал успешно изменен (Th)",
                                                                                            ephemeral=True)
                                                else:
                                                    await interaction.response.send_message("Канал не найден",
                                                                                            ephemeral=True)

                                await interaction.response.send_modal(set_category_channel_modal())

                            @discord.ui.button(label="Респавн сообщения", style=discord.ButtonStyle.red)
                            async def reset_category_channel(self, interaction: discord.Interaction, button):
                                bot = var.bot
                                with open(var.path, "r", encoding="utf-8") as f:
                                    self.data = json.load(f)

                                guild = interaction.guild
                                channel = guild.get_channel(self.data[str(interaction.user.id)][select.values[0]]["chan"])

                                class start_questionary(discord.ui.View):
                                    with open(var.path, "r", encoding="utf-8") as f:
                                        data = json.load(f)
                                    bot = var.bot

                                    if data[str(interaction.user.id)][select.values[0]]["in_use"] == False:
                                        name = "Набор закрыт"
                                    else:
                                        name = "Ответить на вопросы"

                                    @discord.ui.button(label=name,
                                                        style=discord.ButtonStyle.blurple,
                                                        custom_id=f"{interaction.user.id}<!>{select.values[0]}",
                                                        disabled=not data[str(interaction.user.id)][select.values[0]]["in_use"])
                                    async def start_button_callback(self, interaction: discord.Interaction, button:discord.Button):
                                        await interaction.response.send_message(content="Проверьте лс.", ephemeral=True)

                                        user_answers = []
                                        with open(var.path, "r", encoding='utf-8') as f:
                                            self.data = json.load(f)
                                        dats = button.custom_id.split("<!>")
                                        for i in range(len(self.data[dats[0]][dats[1]]["que"])):

                                            try:
                                                await interaction.user.send(self.data[dats[0]][dats[1]]["que"][i])
                                            except:
                                                await interaction.edit_original_response(content="У вас закрыт лс. Откройте его, чтобы получить список вопросов.")
                                                break
                                            try:
                                                response = await bot.wait_for('message', check=lambda
                                                    m: m.author == interaction.user and m.channel.id == interaction.user.dm_channel.id, timeout=300)

                                                if response.content:
                                                    print(response.content, "content")
                                                    user_answers.append(response.content)
                                                else:
                                                    await interaction.user.send(
                                                        f"Файлы, голосовые и картинки не принимаются. \nТеперь перепроходи все заново)")
                                                    return

                                            except asyncio.TimeoutError:
                                                await interaction.user.send(f"Время на вопрос вышло.")
                                                return

                                        await interaction.user.send(f"Спасибо за подачу заявки! В скором времени она будет рассмотрена.")

                                        user = guild.get_member(int(dats[0]))

                                        # print(user_answers)

                                        ans = ""

                                        out_chan = user


                                        out_chan = interaction.guild.get_channel(self.data[dats[0]][dats[1]]["out_chan"])
                                        if out_chan == None:
                                            print("Th")
                                            out_chan = interaction.guild.get_thread(self.data[dats[0]][dats[1]]["out_chan"])
                                            if out_chan == None:
                                                out_chan = user



                                        for i in range(len(user_answers)):
                                            ans+=f"{i+1}. {self.data[dats[0]][dats[1]]['que'][i]} ```{user_answers[i]}``` \n"
                                        embed = discord.Embed(title='', description="", color=16762880)
                                        embed.description+=f"## Пришла новая заявка! \n"
                                        embed.description+=f"Пользователь: {interaction.user.mention} \n"
                                        embed.description+=f"Категория: `{dats[1]}` \n{ans}"
                                        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
                                        await out_chan.send(embed=embed)

                                emb = discord.Embed(title=f"{select.values[0]}", description=self.data[str(interaction.user.id)][select.values[0]]["description"])
                                if channel != None:

                                    mes = None
                                    try:
                                        mes = await channel.fetch_message(self.data[str(interaction.user.id)][select.values[0]]["mess"])
                                    except:
                                        mes = None
                                    if mes == None:
                                        mes = await channel.send(embed=emb, view=start_questionary())
                                        self.data[str(interaction.user.id)][select.values[0]]["mess"] = mes.id
                                    else:
                                        await mes.edit(content="", embed=emb, view=start_questionary())
                                    with open(var.path, "w", encoding="utf-8") as f:
                                        json.dump(self.data, f, ensure_ascii=False, indent=4)
                                    await interaction.response.send_message("Сообщение перезапущенно!",ephemeral=True)

                                else:
                                        channel = guild.get_thread(self.data[str(interaction.user.id)][select.values[0]]["chan"])
                                        if channel != None:
                                            mes = None
                                            try:
                                                mes = await channel.fetch_message(self.data[str(interaction.user.id)][select.values[0]]["mess"])
                                            except:
                                                mes = None
                                            if mes == None:
                                                mes = await channel.send(embed=emb, view=start_questionary())
                                                self.data[str(interaction.user.id)][select.values[0]]["mess"] = mes.id
                                            else:
                                                await mes.edit(content="", embed=emb)
                                            with open(var.path, "w", encoding="utf-8") as f:
                                                json.dump(self.data, f, ensure_ascii=False, indent=4)
                                            await interaction.response.send_message("Сообщение перезапущенно!", ephemeral=True)
                                        else:
                                            await interaction.response.send_message(
                                                "Канал не указан или указан неверно. Укажите его в настройках категории по команде /nt \nThread checker")


                        emb = discord.Embed(title=f"Настройка категории {select.values[0]}")
                        await interaction.response.send_message(embed=emb, view=manage_buttons(), ephemeral=True)

                @discord.ui.button(label="Создать категорию", style=discord.ButtonStyle.blurple)
                async def create_category_callback(self, interaction: discord.Interaction, button):
                    class create_category_modal(discord.ui.Modal, title="Создание новой категории"):
                        name = discord.ui.TextInput(
                            label="Имя категории",
                            placeholder="Введите имя",
                            required=True,
                            max_length=100,
                            style=discord.TextStyle.short
                        )

                        description = discord.ui.TextInput(
                            label="Описание категории",
                            placeholder="Введите Описание",
                            required=True,
                            max_length=4000,
                            style=discord.TextStyle.long
                        )

                        questions = discord.ui.TextInput(
                            label="Вопросы для категории",
                            placeholder="Введите вопросы начиная с '1. '",
                            required=True,
                            max_length=4000,
                            style=discord.TextStyle.long
                        )

                        async def on_submit(self, interaction: discord.Interaction):
                            name = self.name.value
                            val = self.questions.value.split("\n")

                            new_cat = {}
                            new_cat["in_use"] = False
                            new_cat["chan"] = None
                            new_cat["mess"] = None
                            new_cat["description"] = self.description.value

                            for i in range(len(val)):
                                val[i] = "".join(val[i].split(f'{i + 1}. '))

                            new_cat["que"] = val

                            with open(var.path, "r", encoding="utf-8") as f:
                                self.data = json.load(f)
                            self.data[str(interaction.user.id)][name] = new_cat
                            with open(var.path, "w", encoding="utf-8") as f:
                                json.dump(self.data, f, ensure_ascii=False, indent=4)

                            await interaction.response.send_message(f"Категория создана!", ephemeral=True)
                    await interaction.response.send_modal(create_category_modal())



            await ctx.response.send_message(embed=emb, ephemeral=True, view=select_category())
        else:
            await ctx.response.send_message("У вас нет роли шефа. Если вы шеф, обратитесь к сисам", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(vac(bot), guilds=bot.guilds)
    var.bot = bot
    loader = var(bot)
    await loader.load_messages()
