# Bifrost-Discord
This Discord bot has multiple modules:

### Bifrost-Announce
Uses the Amazon Polly API to generate greeting messages for the roles you want in a Discord server. It has a cost-saving functionality that only generates the .mp3 files once.

### Bifrost-Elections
This module creates a "democratic" server-wide election that allows one specific role from the server to vote for their representants.

Elections can be invoked using the >elections command along with four positional arguments that reference four server roles using the Discord role mention function.

For example, let's say that in my server I have four existing roles, Congressman, First Inspector, Inspector and Verified Member
>\>elections @Congressman @First Inspector @Inspector @Verified Member

*It is recommended that you use a role that trusted members have as the @Verified Member.

This means that @Verified Member is the role that gets to vote, and after the voting concludes, the server will end up with...
- Three @Congressman
- Two @Inspector per @Congressman 
- One @First Inspector. The First Inspector is chosen based on who's the @Congressman that got the most votes.

The name of the roles could be anything, the arguments are positional so only the order matters, in my case, this would be the hierarchy of my server:

```bash
         ____________
        /           \\
       / Congressman \\     ►3
      /               \\
     / First Inspector \\   ►1
    /                   \\
   /      Inspector      \\ ►6
  /                       \\
 /     Verified Member     \\
/___________________________\\	
```

The election is compromised of two stages
- Postulations

After an administrator member uses the >elections command, elections start and everyone who has the @Verified Member role gets to postulate himself as a candidate for the @Congressman role. Don't worry, you get to vote even if you postulate.

Postulating for the @Congressman role grants you a text channel. In this channel, as a Congressman candidate, you can postulate members with the rank of @Verified Member to be one of your two mandatory @Inspector, and your optional @First Inspector candidate

Candidates you postulate must accept the candidature in order to be part of your party.

You must meet all the requirements in order to get to the next phase of the elction. Basically, you must have two confirmed @Inspector in your party.

Also you should add a banner to your party, and the colour you like the most.

- Voting


### Dependencies
opus
ffmpeg
