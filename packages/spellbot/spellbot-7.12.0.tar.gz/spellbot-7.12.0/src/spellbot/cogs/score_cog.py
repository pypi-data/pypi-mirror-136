import logging

from ddtrace import tracer
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType

from .. import SpellBot
from ..interactions import ScoreInteraction
from ..metrics import add_span_context
from ..utils import for_all_callbacks

logger = logging.getLogger(__name__)


@for_all_callbacks(commands.guild_only())
class ScoreCog(commands.Cog):
    def __init__(self, bot: SpellBot):
        self.bot = bot

    @cog_ext.cog_context_menu(target=ContextMenuType.USER, name="View Score")
    @tracer.wrap(name="interaction", resource="view_score")
    async def view_score(self, ctx: MenuContext):
        add_span_context(ctx)
        assert ctx.target_author
        async with ScoreInteraction.create(self.bot, ctx) as interaction:
            await interaction.execute(target=ctx.target_author)

    @cog_ext.cog_slash(name="score", description="View your game record on this server.")
    @tracer.wrap(name="interaction", resource="score")
    async def score(self, ctx: SlashContext):
        add_span_context(ctx)
        async with ScoreInteraction.create(self.bot, ctx) as interaction:
            await interaction.execute(target=ctx.author)

    @cog_ext.cog_slash(
        name="history",
        description="View historical game records in this channel.",
    )
    @tracer.wrap(name="interaction", resource="history")
    async def history(self, ctx: SlashContext):
        add_span_context(ctx)
        async with ScoreInteraction.create(self.bot, ctx) as interaction:
            await interaction.history()


def setup(bot: SpellBot):
    bot.add_cog(ScoreCog(bot))
