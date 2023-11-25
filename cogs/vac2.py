import discord
import discord.ui
from discord.ext import commands
from discord import app_commands
import json
import asyncio

class vac(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open("vac2.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
        print("#[VacV2 Logs]: Loaded")

    @app_commands.command(name="nt", description="New Version of Vac")
    async def vacancy_main(self, ctx:discord.Interaction):
        with open("vac2.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)
        if str(ctx.user.id) in self.data:
                emb = discord.Embed(title="Менеджер категорий", description="Добавление / Переименование / Удаление Категорий")
                for i in self.data[str(ctx.user.id)]:
                    que = ""
                    for j in range(len(self.data[str(ctx.user.id)][i]["que"])):
                        que+=f'{j+1}. {self.data[str(ctx.user.id)][i]["que"][j]} \n'
                    emb.add_field(name=i, value=f"```{que}```", inline=False)

                class select_category(discord.ui.View):
                    with open("vac2.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                    opt=[]
                    for i in self.data[str(ctx.user.id)]:
                        sel = discord.SelectOption(
                            label=i,
                            description=""
                        )
                        opt.append(sel)
                    @discord.ui.select(options=opt, placeholder="Выбирите нужную категорию")
                    async def select_callback(self, interaction:discord.Interaction, select:discord.ui.Select):
                        class manage_buttons(discord.ui.View):
                            @discord.ui.button(label="Переименовать")
                            async def rename_callback(self, interaction:discord.Interaction, button):
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
                                        with open('vac2.json', "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        val = self.feedback.value
                                        self.data[str(interaction.user.id)][val] = self.data[str(interaction.user.id)][select.values[0]]
                                        self.data[str(interaction.user.id)].pop(select.values[0])
                                        with open("vac2.json", "w", encoding="utf-8") as f:
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
                                            with open("vac2.json", "r", encoding="utf-8") as f:
                                                self.data = json.load(f)

                                            self.data[str(interaction.user.id)].pop(self.con.value)

                                            with open("vac2.json", "w", encoding="utf-8") as f:
                                                json.dump(self.data, f, ensure_ascii=False, indent=4)

                                            await interaction.response.send_message("Категория удалена", ephemeral=True)
                                        else:
                                            await interaction.response.send_message("Отклоненно")
                                await interaction.response.send_modal(confirm_modal())

                            @discord.ui.button(label="Изменить вопросы", style=discord.ButtonStyle.blurple)
                            async def change_que_callback(self, interaction: discord.Interaction,
                                                          button: discord.ui.Button):
                                class Feedback(discord.ui.Modal, title=f'Настройка вопросов для {select.values[0]}'):
                                    with open("vac2.json", "r", encoding="utf-8") as f:
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
                                        with open('vac2.json', "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        val = self.feedback.value
                                        val = val.split("\n")

                                        for i in range(len(val)):
                                            val[i] = "".join(val[i].split(f'{i + 1}. '))

                                        self.data[str(interaction.user.id)][select.values[0]]["que"] = val
                                        print(val)

                                        with open('vac2.json', "w", encoding='utf-8') as f:
                                            json.dump(self.data, f, ensure_ascii=False, indent=4)
                                        await interaction.response.send_message("Успешно изменено", ephemeral=True)

                                await interaction.response.send_modal(Feedback())

                            if self.data[str(ctx.user.id)][select.values[0]]["in_use"] == True:
                                name = "Закрыть набор"
                            else:
                                name = "Открыть набор"

                            @discord.ui.button(label=name, style=discord.ButtonStyle.green)
                            async def use_switch_callback(self, interaction: discord.Interaction,
                                                          button: discord.ui.Button):
                                with open("vac2.json", "r", encoding="utf-8") as f:
                                    self.data = json.load(f)
                                self.data[str(interaction.user.id)][select.values[0]]["in_use"] = \
                                self.data[str(interaction.user.id)][select.values[0]]["in_use"]
                                with open("vac2.json", "w", encoding="utf-8") as f:
                                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                                await interaction.response.send_message("Изменения приняты!", ephemeral=True)

                            if self.data[str(interaction.user.id)][select.values[0]]["chan"] != None:
                                @discord.ui.button(label="Изменить канал")
                                async def reset_category_channel(self, interaction: discord.Interaction, button):
                                    class reset_category_channel_modal(discord.ui.Modal,
                                                                     title="Назначение канала для категории"):
                                        with open("vac2.json", "r", encoding="utf-8") as f:
                                            self.data = json.load(f)
                                        chan = discord.ui.TextInput(
                                            label="ID Канала",
                                            placeholder="ID",
                                            required=True,
                                            style=discord.TextStyle.short,
                                            default=self.data[str(interaction.user.id)][select.values[0]]["chan"]
                                        )

                                        async def on_submit(self, interaction: discord.Interaction):
                                            val = int(self.chan.value)
                                            with open("vac2.json", "r", encoding="utf-8") as f:
                                                self.data = json.load(f)

                                            guild = interaction.guild
                                            chan = guild.get_channel(val)
                                            if chan != None:
                                                self.data[str(interaction.user.id)][select.values[0]]["chan"] = val

                                                with open("vac2.json", "w", encoding="utf-8") as f:
                                                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                                                await interaction.response.send_message("Канал успешно изменен",
                                                                                        ephemeral=True)
                                            else:
                                                await interaction.response.send_message("Канал не найден",
                                                                                        ephemeral=True)

                                    await interaction.response.send_modal(reset_category_channel_modal())
                            else:
                                @discord.ui.button(label="Назначить канал")
                                async def set_category_channel(self, interaction:discord.Interaction, button):
                                    class set_category_channel_modal(discord.ui.Modal, title="Назначение канала для категории"):
                                        chan = discord.ui.TextInput(
                                            label="ID Канала",
                                            placeholder="ID",
                                            required=True,
                                            style=discord.TextStyle.short
                                        )
                                        async def on_submit(self, interaction:discord.Interaction):
                                            val = int(self.chan.value)
                                            with open("vac2.json", "r", encoding="utf-8") as f:
                                                self.data = json.load(f)

                                            guild = interaction.guild
                                            chan = guild.get_channel(val)
                                            if chan != None:
                                                self.data[str(interaction.user.id)][select.values[0]]["chan"] = val

                                                with open("vac2.json", "w", encoding="utf-8") as f:
                                                    json.dump(self.data, f, ensure_ascii=False, indent=4)
                                                await interaction.response.send_message("Канал успешно изменен", ephemeral=True)
                                            else:
                                                await interaction.response.send_message("Канал не найден", ephemeral=True)
                                    await interaction.response.send_modal(set_category_channel_modal())


                        await interaction.response.send_message(select.values[0], view=manage_buttons(), ephemeral=True)

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

                                for i in range(len(val)):
                                    val[i] = "".join(val[i].split(f'{i + 1}. '))

                                new_cat["que"] = val

                                with open("vac2.json", "r", encoding="utf-8") as f:
                                    self.data = json.load(f)
                                self.data[str(interaction.user.id)][name] = new_cat
                                with open("vac2.json", "w", encoding="utf-8") as f:
                                    json.dump(self.data, f, ensure_ascii=False, indent=4)

                                await interaction.response.send_message(f"Изменения приняты! \n\nDebug\nname={name}\n\n```{new_cat}```")
                        await interaction.response.send_modal(create_category_modal())



                await ctx.response.send_message(embed=emb, ephemeral=True, view=select_category())
        else:
            await ctx.response.send_message("У вас нет роли шефа. Если вы шеф, обратитесь к сисам")


async def setup(bot: commands.Bot):
    await bot.add_cog(vac(bot), guilds=bot.guilds)
