from bfrauxfunc import execute_sqlite

def are_elections_running(guild_id):
    return execute_sqlite(f"SELECT election_id from election WHERE election_id = {guild_id}")

def get_electable_congressman_data(member_id,ctx):
    return execute_sqlite(f"SELECT * FROM electable_congressman WHERE member_id = {member_id} and guild_id = {ctx.guild.id}")

def get_guild_electables_category(guild_id):
    query_result = execute_sqlite(f"SELECT category_electables_id FROM election WHERE election_id = {guild_id}")
    if query_result:
        return query_result[0]['category_electables_id']
    return query_result

def get_election_roles(guild_id):
    return execute_sqlite(f"SELECT * FROM election_role where election_id = {guild_id}")


def get_candidate_campaign_channel(memberId):
    query_result = execute_sqlite(f"SELECT text_channel_id FROM electable_congressman WHERE member_id = {memberId}")
    if query_result:
        return query_result[0]['text_channel_id']
    return query_result