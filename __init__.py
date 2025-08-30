from .judges_appeals_cog import JudgesAppealsCog

def setup(bot):
    bot.add_cog(JudgesAppealsCog(bot))