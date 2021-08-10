import StoriesBase

async def story(bot, ctx, args):
    combined = "".join(args).strip()
    tree = StoriesBase.parse_tree()
    print(tree)

    # if combined:
    #     await help.jump(bot, ctx, combined)
    # else:
    #     await help.start_help(bot, ctx)
