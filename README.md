# Bifrost-Discord
This Discord bot has multiple modules:

### Bifrost-Announce
Uses the Amazon Polly API to generate greeting messages for the roles you want in a Discord server. It has a cost-saving functionality that only generates the .mp3 files once.

### Bifrost-Elections
Creates a "democratic" system that allows certain roles from the server to vote for their representants.

Elections can be invoked using the >elections command along with four parameters that reference four server roles.

For example:
\>elections @master_role @first_pawn_role @pawn @voter

This means that @voter is the role that gets to vote, and after the voting concludes, the server will end up with three @master_roles, two @pawn roles per @master and one @first_pawn. The first pawn is chosen based on who's the @master_role with most votes.


```bash
             / \\
            /   \\
           /     \\
          /       \\
         / bifrost \\
        /           \\
       / master_role \\     ►3
      /               \\
     / first_pawn_role \\   ►1
    /                   \\
   /      pawns_role     \\ ►6
  /                       \\
 /          voter          \\
/___________________________\\	
```






### Dependencies
opus
ffmpeg
