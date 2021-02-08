# Bifrost-Discord
This Discord bot has multiple modules:

### Bifrost-Announce
Uses the Amazon Polly API to generate greeting messages for the roles you want in a Discord server. It has a cost-saving functionality that only generates the .mp3 files once.

### Bifrost-Elections
This module creates a "democratic" server-wide election that allows certain roles from the server to vote for their representants.

Elections can be invoked using the >elections command along with four parameters that reference four server roles using the Discord role mention function.

For example, let's say that in my server I have four existing roles, Congressman, First Inspector, Inspector and Verified Member
>\>elections @Congressman @First Inspector @Inspector @Verified Member

This means that @Verified Member is the role that gets to vote, and after the voting concludes, the server will end up with...
- Three @Congressman
- Two @Inspector per @master 
- One @First Inspector. The First Inspector is chosen based on who's the @congressman that got the most votes.

The name of the roles could be anything, the arguments are positional so only the order matters, in my case, this would be the hierarchy of my server:

```bash
             / \\
            /   \\
           /     \\
          /       \\
         /         \\
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
- Election start
After an administrator member uses the >elections command, elections start and everyone who has the @voter role gets to postulate himself as a candidate for the @master_role

Postulating for the @master_role grants you a text channel. In this channel you must propose two members to fulfill the @pawn_role


### Dependencies
opus
ffmpeg
