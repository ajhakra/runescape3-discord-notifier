import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import re
import time

# Globals for easy access to variables that need to be configured
fileStorageLoc = "/your/location/here/"
userNameList = (open(fileStorageLoc+"userlist.txt", "rt").read()).replace("[", "").replace("]", "").replace(" ", "").split(",")
webhookUrlLevel = (open(fileStorageLoc+"webhooks.txt", "rt").read()).replace("[", "").replace("]", "").replace(" ", "").split(",")[0]
webhookUrlLoot = (open(fileStorageLoc+"webhooks.txt", "rt").read()).replace("[", "").replace("]", "").replace(" ", "").split(",")[1]
footerText = str((open(fileStorageLoc+"footer.txt", "rt").read()))

def getData(charName):
    # Query the Runescape API to get the 20 latest account activities
    dataQuery = (requests.get("https://apps.runescape.com/runemetrics/profile/profile?user="+charName+"&activities=20").json())["activities"]
    return str(dataQuery),charName

def activityComparison(dataQuery,charName):
    # Create file to store the last 20 activities received, if it doesnt already exist
    try:
        open(fileStorageLoc + charName + "-activity.txt", "xt")
    except:
        pass

    # Read from activity file and parse into required format (proper json pending)
    readFile = open(fileStorageLoc + charName + "-activity.txt", "rt").read()

    fileReadParse= readFile.replace("}", "~").replace("{", "").replace("~, ", "~").replace("[", "").replace("]", "").replace("\"", "").split("~")

    # Parse queried data into required format (proper json pending)
    dataQueryParse = dataQuery.replace("}", "~").replace("{", "").replace("~, ", "~").replace("[", "").replace("]", "").replace("\"", "").split("~")

    # Compare the queried data to the read data, and output the differences into a new list
    updateList = list([entry for entry in dataQueryParse if entry not in fileReadParse])
    for entry in updateList:
        print(entry)
    
    # Write queried data to activity file
    open(fileStorageLoc + charName + "-activity.txt", "wt").write(dataQuery)
    return reversed(updateList), charName

def postToDiscord(payload,charName):
    # For each activity, set the activity type, extract relevant info, and set relevant webhook. Extra data still required to account for all activity types....
    for activity in payload:
        if re.search("Levelled up", activity):
            notifType="Level Up"
            setSkill=re.findall("Levelled up (\\w+)", activity)[0]
            levelNumber=re.findall("I am now level (\\d+)", activity)[0]
            webhookUrl = webhookUrlLevel
        else:
            if re.search("gimme the loot", activity):
                notifType="Loot Drop"
                webhookUrl = webhookUrlLoot

        # Setting up payload and sending it to discord
        discord = DiscordWebhook(url=webhookUrl, rate_limit_retry=True)
        fancy = DiscordEmbed(title=notifType, description=charName + " has levelled " + setSkill + " to " + levelNumber, color="2A415F")
        fancy.set_author(name=charName, icon_url="https://static.wikia.nocookie.net/runescape2/images/a/a7/RuneScape_Companion_logo.png/revision/latest?cb=20170207223045")
        fancy.set_thumbnail(url="https://runescape.wiki/images/thumb/" + setSkill + "-icon.png/21px-" + setSkill + "-icon.png?c19b9")
        fancy.set_footer(text=footerText)
        fancy.set_timestamp()
        discord.add_embed(fancy)
        discord.execute()

def main():
    # To infinity and beyond
    while True:
        for character in userNameList:
            getDataValue = getData(character)
            activityComparisonValue = activityComparison(getDataValue[0], getDataValue[1])
            postToDiscord(activityComparisonValue[0], activityComparisonValue[1])
            # rate limit avoidance (for the runescape endpoint)
            time.sleep(2)

main()
