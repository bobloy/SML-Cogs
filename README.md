# SML-Cogs

This repo hosts a variety of cogs (aka modules) for use with the **Red Discord Bot** ([source](https://github.com/Twentysix26/Red-DiscordBot) / [documentation](https://twentysix26.github.io/Red-Docs/)). Most of them are in active development and are developed specifically for the **Reddit Alpha Clan Family** (RACF) Discord server.

While some of these cogs can theoretically be used for any Discord server, many contain codes which are RACF-specifc.

If you would like to see most of these in action, you can join the RACF Discord server with this invite code: [http://discord.gg/racf](http://discord.gg/racf)

You are welcome to log any issues in the Issues tab, or try to find me on either the RACF Discord server or my own Discord server at [http://discord.me/sml](http://discord.me/sml)

There are no extensive documentation on these cogs. However, usage for many of these commands can be found on the documentation site for the RACF server, since these cogs were mostly written for it: http://docs.redditalpha.com

# Table of Contents

* [SML\-Cogs](#sml-cogs)
  * [Installation](#installation)
    * [1\. Add the repo](#1-add-the-repo)
    * [2\. Add the cog you want to installed](#2-add-the-cog-you-want-to-installed)
  * [Cogs](#cogs)
    * [General Cogs](#general-cogs)
    * [Brawl Stars Cogs](#brawl-stars-cogs)
    * [Clash Royale Cogs](#clash-royale-cogs)
    * [RACF cogs](#racf-cogs)
    * [RCS cogs](#rcs-cogs)
    * [No longer maintained](#no-longer-maintained)
  * [Notes](#notes)

## Installation

To install a cog on your bot instance:

### 1. Add the repo

`[p]cog repo add SML-Cogs http://github.com/smlbiobot/SML-Cogs`

`[p]` stands for server prefix. So if you use `!` as to run bot commands, you would instead type:

`!cog repo add SML-Cogs http://github.com/smlbiobot/SML-Cogs`

### 2. Add the cog you want to installed

`[p]cog install SML-Cogs deck`

## Cogs

### General Cogs

* **archive**: Archive channel messages from one channel to another.
* **banned**: quick list for banned players
* **eslog**: Elasticsearch logging
* **figlet**: Convert text into ASCII graphics
* **logstash**: Logstash logging
* **magic**: automagically change color for the magic role
* **mm: member management**: use and + not operators to combine the display of multiple roles
* **nlp**: natural language processing. Google translate.
* **rolehist**: display role addition and removal history
* **quotes**: quotes by author. Similar to customcom but does not use top level command space
* **reactionmanager**: Add / remove reactions from bot, see who reacted on a message.
* **timezone**: Convert and determine timezone using Google Maps API
* **togglerole**: Allow users to self-assigned roles based on role permission.
* **userdata**: Free-form user data store.

### Brawl Stars Cogs

* **bsdata**: Brawl Stars profile and clan using brawlstars.io API

### Clash Royale Cogs

* **crclan**: Clash Royale clan using [cr-api](https://github.com/cr-api/cr-api) API
* **crdata**: Clash Royale Global 200 leaderboard (requires Starfi.re login)
    * [User docs](http://docs.redditalpha.com/#/visitor/crdata)
* **crdatae**: Clash Royale Global 200 leaderboard using emojis (requires SF Auth)
    * [User docs](http://docs.redditalpha.com/#/visitor/crdata)
* **crprofile**: Clash Royale profile using [cr-api](https://github.com/cr-api/cr-api) API
    * [User docs](http://docs.redditalpha.com/#/visitor/crprofile)
* **[deck](https://github.com/smlbiobot/SML-Cogs/wiki/Deck)**: Clash Royale deck builder


### RACF cogs

These cogs were written specifically for the RACF (Reddit Alpha Clan Family) Discord server and will be useless for other servers.

* **farmers**: display clan chest farmers historic data
* **feddback**: Send feedbacks to leaders
* **racf**: utilities
* **trophies**: display clan trophy requirements
* **vcutil**: Automatically enter VC specific text chat based on VC participation

### RCS cogs

These are developed specifically for the RCS (Reddit Clan System) server.

* **rcs**: verify users
* **rcsapplication**: Retrieve RCS application responses
* **recruit**: add and edit recruitment messages for clans.

### No longer maintained

Some of these might still work, but they are no longer maintained.

* **activity**: weekly server activity logging
* **card**: Clash Royale card popularity snapshots
* **clanbattle**: automatic voice channel creation for clan battles
* **ddlog**: datadog logging
* **ddlogmsg**: datadog logging messages
* **draftroyale**: Clash Royale drafting bot (active development)
* **ga**: Hacking Google Analytics as free data storage for Discord logging

## Notes

The top-level scripts `./enable-cog` and `./disable-cog` were written to help with local cog development and are not needed for the end users. They were made so that cogs can maintain the folder structures expected by the Red bot while making it possible to “install” into the Red folder without using the `cog install` command.

In the production environment, however, you should always install the cogs as specified in the [Installation](#installation) section above.


