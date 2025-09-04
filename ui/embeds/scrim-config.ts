import { BracketClient } from "@/base/classes/client";
import { discordTimestamp } from "@/lib/utils";
import { Scrim } from "@prisma/client";
import { EmbedBuilder } from "discord.js";

export function scrimConfigEmbed(scrim: Scrim, client: BracketClient) {
  return new EmbedBuilder()
    .setTitle("⚙️ Scrim Configuration")
    .setColor("Green")
    .setAuthor({
      name: client.user?.username || "Scrim Bot",
    })
    .addFields(
      {
        name: "📋 General",
        value: [
          `**Name:** ${scrim.name}`,
          `**Scrim ID:** \`${scrim.id}\``,
        ].join("\n"),
        inline: false,
      },
      {
        name: "🧑‍🤝‍🧑 Teams",
        value: [
          `**Max Teams:** ${scrim.maxTeams}`,
          `**Players/Team:** ${
            scrim.minPlayersPerTeam && scrim.maxPlayersPerTeam
              ? scrim.minPlayersPerTeam === scrim.maxPlayersPerTeam
                ? `${scrim.minPlayersPerTeam}`
                : `${scrim.minPlayersPerTeam}–${scrim.maxPlayersPerTeam}`
              : "Not set"
          }`,
          `**Substitutes/Team:** ${scrim.maxSubstitutePerTeam}`,
        ].join("\n"),
        inline: false,
      },
      {
        name: "📅 Registration",
        value: [
          `**Opens:** ${discordTimestamp(scrim.registrationStartTime)}`,
          `**Auto-Close:** ${
            scrim.autoCloseRegistration ? "✅ Enabled" : "❌ Disabled"
          }`,
        ].join("\n"),
        inline: false,
      },
      {
        name: "🎯 Slotlist Mode",
        value: scrim.autoSlotList ? "⚡ Auto" : "📝 Manual",
        inline: false,
      }
    )
    .setFooter({
      text: "Configuration locks once the registration opens.",
    })
    .setImage("https://i.ibb.co/XxXCWznH/image.png");
}
