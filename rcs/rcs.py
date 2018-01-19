# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2017 SML

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import os
from collections import defaultdict

import discord
from __main__ import send_cmd_help
from discord.ext import commands
import aiohttp
import json
import asyncio

from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import pagify, box

BOTCOMMANDER_ROLES = ['Bot Commander']

TOGGLE_ROLES = ["Trusted", "Visitor"]

TOGGLE_PERM = {
    "Trusted": [
        "Tournaments"
    ],
    "Visitor": [
    ]
}

PATH = os.path.join("data", "rcs")
JSON = os.path.join(PATH, "settings.json")

RCS_SERVER_IDS = ''


def nested_dict():
    """Recursively nested defaultdict."""
    return defaultdict(nested_dict)


class SCTag:
    """SuperCell tags."""

    TAG_CHARACTERS = list("0289PYLQGRJCUV")

    def __init__(self, tag: str):
        """Init.

        Remove # if found.
        Convert to uppercase.
        Convert Os to 0s if found.
        """
        if tag.startswith('#'):
            tag = tag[1:]
        tag = tag.replace('O', '0')
        tag = tag.upper()
        self._tag = tag

    @property
    def tag(self):
        """Return tag as str."""
        return self._tag

    @property
    def valid(self):
        """Return true if tag is valid."""
        for c in self.tag:
            if c not in self.TAG_CHARACTERS:
                return False
        return True

    @property
    def invalid_chars(self):
        """Return list of invalid characters."""
        invalids = []
        for c in self.tag:
            if c not in self.TAG_CHARACTERS:
                invalids.append(c)
        return invalids

    @property
    def invalid_error_msg(self):
        """Error message to show if invalid."""
        return (
            'The tag you have entered is not valid. \n'
            'List of invalid characters in your tag: {}\n'
            'List of valid characters for tags: {}'.format(
                ', '.join(self.invalid_chars),
                ', '.join(self.TAG_CHARACTERS)
            ))


class RCS:
    """Reddit Clan System (RCS) utility."""

    def __init__(self, bot):
        """Init."""
        self.bot = bot
        self.settings = nested_dict()
        self.settings.update(dataIO.load_json(JSON))
        
    def _getAuth(self):
        return {"auth" : self.settings['token']}

    @commands.group(pass_context=True, no_pm=True)
    @checks.mod_or_permissions()
    async def rcsset(self, ctx):
        """RCS Settings."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            
    @rcsset.command(name="token", pass_context=True)
    @checks.admin_or_permissions()
    async def rcsset_token(self, ctx, token):
        """Set's the cr-api.com token"""
        self.settings["token"] = token
        dataIO.save_json(JSON, self.settings)
        await self.bot.say("Set token to "+token)
        
    @rcsset.command(name="settings", pass_context=True)
    @checks.mod_or_permissions()
    async def rcsset_settings(self, ctx):
        """Shows settings."""
        server = ctx.message.server
        try:
            clans = self.settings[server.id]["clans"].values()
            print(clans)
            clans = sorted(clans, key=lambda c: c["role_name"])
            fmt = '{:<16} {:<16} {:<16}'
            out = [
                fmt.format('Role', 'Nick', 'Tag'),
                '-' * 50
            ]
            for clan in clans:
                out.append(
                    fmt.format(
                        clan["role_name"],
                        clan["role_nick"],
                        clan["tag"]
                    ))
            for page in pagify(box('\n'.join(out)), shorten_by=24):
                await self.bot.say(page)
        except KeyError:
            await self.bot.say("No server settings found.")

    @rcsset.command(name="role", pass_context=True)
    @checks.mod_or_permissions()
    async def rcsset_clan(self, ctx, clan_tag, role_name, role_nick=None):
        """Associate clan tags to role names.

        Internally store roles as role IDs in case role renames.
        Optionally set role_nick for used in nicknames for special cases
        e.g. RACF Delta uses Ⓐ - Delta instead of the default
        """
        server = ctx.message.server
        role = discord.utils.get(server.roles, name=role_name)
        if role is None:
            await self.bot.say("Cannot find that role on this server.")
            return
        if role_nick is None:
            role_nick = role_name

        sctag = SCTag(clan_tag)
        if not sctag.valid:
            await self.bot.say(sctag.invalid_error_msg)

        clan_tag = sctag.tag
        clan = {
            "tag": clan_tag,
            "role_id": role.id,
            "role_name": role.name,
            "role_nick": role_nick
        }
        self.settings[server.id]["clans"][clan_tag] = clan
        dataIO.save_json(JSON, self.settings)
        await self.bot.say(
            "Settings updated:\n"
            "Clan Tag: {}\n"
            "Role Name: {}\n"
            "Role Nick: {}\n"
            "Role ID: {}\n".format(
                clan_tag, role_name, role_nick, role.id
            )
        )

    @commands.group(pass_context=True, no_pm=True)
    async def rcs(self, ctx):
        """Reddit Clan System (RCS)."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @checks.mod_or_permissions(manage_roles=True)
    @rcs.command(name="verify", aliases=["v"], pass_context=True, no_pm=True)
    async def verify(self, ctx, member: discord.Member, tag, *, options=None):
        """Verify RCS membership using player tag.

        1. Check clan information via CR Profile API
        2. Map clan information to server roles.
        3. Assign Trused + clan roles.
        4. Rename user to IGN (Role)

        Options:
        add --notourney as last parameter to not add the Tournaments role

        """
        # Check options
        if options is None:
            options = ''
        options = options.split(' ')

        include_tourney = '--notourney' not in options

        # Check clan info
        sctag = SCTag(tag)
        if not sctag.valid:
            await self.bot.say(sctag.invalid_error_msg)
            return

        tag = sctag.tag
        player = await self.fetch_player_profile(tag)
        try:
            player_clan_tag = player["clan"]["tag"]
        except KeyError:
            await self.bot.say("Cannot find clan tag in API. Aborting…")
            return

        server = ctx.message.server
        clans = self.settings[server.id]["clans"]
        if player_clan_tag not in clans:
            await self.bot.say("User is not in one of our clans, or the clan has not be set by MODs.")
            return

        clan_settings = self.settings[server.id]["clans"][player_clan_tag]

        # Assign roles
        roles = ["Trusted", clan_settings["role_name"]]
        if include_tourney:
            roles.append('Tournaments')
        await self.changerole(ctx, member, *roles)

        # Rename member to IGN (role_nick)
        nick = "{ign} ({role_nick})".format(
            ign=player["name"],
            role_nick=clan_settings["role_nick"]
        )

        try:
            await self.bot.change_nickname(member, nick)
            await self.bot.say("Renamed {} to {}".format(member, nick))
        except discord.errors.Forbidden:
            await self.bot.say("I do not have permission to change the nick of {}".format(member))

    async def changerole(self, ctx, member: discord.Member, *roles):
        """Perfect change roles."""
        mm = self.bot.get_cog("MemberManagement")
        await ctx.invoke(mm.changerole, member, *roles)

    async def fetch_player_profile(self, tag):
        """Fetch player profile data."""
        url = "{}{}".format('http://api.cr-api.com/player/', tag)

        try:
            async with aiohttp.ClientSession(headers=self._getAuth()) as session:
                async with session.get(url, timeout=30) as resp:
                    data = await resp.json()
        except json.decoder.JSONDecodeError:
            raise
        except asyncio.TimeoutError:
            raise

        return data

    @commands.has_any_role(*TOGGLE_ROLES)
    @rcs.command(pass_context=True, no_pm=True)
    async def togglerole(self, ctx, role_name):
        """Self-toggle role assignments."""
        author = ctx.message.author
        server = ctx.message.server
        # toggleable_roles = [r.lower() for r in TOGGLEABLE_ROLES]

        member_role = discord.utils.get(server.roles, name="Trusted")
        is_member = member_role in author.roles

        if is_member:
            toggleable_roles = TOGGLE_PERM["Trusted"]
        else:
            toggleable_roles = TOGGLE_PERM["Visitor"]

        toggleable_roles = sorted(toggleable_roles)

        toggleable_roles_lower = [r.lower() for r in toggleable_roles]

        if role_name.lower() in toggleable_roles_lower:
            role = [
                r for r in server.roles
                if r.name.lower() == role_name.lower()]

            if len(role):
                role = role[0]
                if role in author.roles:
                    await self.bot.remove_roles(author, role)
                    await self.bot.say(
                        "Removed {} role from {}.".format(
                            role.name, author.display_name))
                else:
                    await self.bot.add_roles(author, role)
                    await self.bot.say(
                        "Added {} role for {}.".format(
                            role_name, author.display_name))
            else:
                await self.bot.say(
                    "{} is not a valid role on this server.".format(role_name))
        else:
            out = []
            out.append(
                "{} is not a toggleable role for you.".format(role_name))
            out.append(
                "Toggleable roles for you: {}.".format(
                    ", ".join(toggleable_roles)))
            await self.bot.say("\n".join(out))


def check_folder():
    """Check folder."""
    if not os.path.exists(PATH):
        os.makedirs(PATH)


def check_file():
    """Check files."""
    if not dataIO.is_valid_json(JSON):
        dataIO.save_json(JSON, {})


def setup(bot):
    """Setup."""
    check_folder()
    check_file()
    n = RCS(bot)
    bot.add_cog(n)
