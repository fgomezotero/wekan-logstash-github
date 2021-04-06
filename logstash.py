#!/usr/bin/env python
#
# logstash.py
#
# Simple tool that will print cards data for logstash (ELK Kibana)
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#
# {"storyPoint": 2.0, "nbComments": 1, "createdBy": "fmonthel", "labels": ["vert", "jaune"], 
# "members": ["fmonthel", "Olivier"], "id": "7WfoXMKnmbtaEwTnn",
# "archivedAt": "2017-02-19T02:13:24.269Z", "createdAt": "2017-02-19T02:13:24.269Z", "lastModification":
# "2017-02-19T03:12:13.740Z", "list": "Done", "dailyEvents": 5, "board": "Test", "isArchived": true,
# "duedAt": "2017-02-19T02:13:24.269Z", "swimlaneTitle": "Swinline Title", "customfieldName1": "value",
# "customfieldName2": "value", "assignees": "fmonthel", "title": "Card title", "boardId": "eJPAgty3guECZf4hs",
# "cardUrl": "http://localhost/b/xxQ4HBqsmCuP5mYkb/semanal-te/WufsAmiKmmiSmXr9m"}


import datetime
import json
import os
import requests
from pymongo import MongoClient

# Parameters
mongo_user = os.getenv('MONGODB_USER', '')
mongo_password = os.getenv('MONGODB_PWD', '')
mongo_server = os.getenv('MONGODB_HOST', 'localhost')
mongo_port = os.getenv('MONGODB_PORT', '27017')
mongo_database = os.getenv('MONGODB_DB', 'wekan')
baseURL = os.getenv('BASEURL', 'http://localhost')
logstashEndpoint = os.getenv('LOGSTASH_SERVER', 'http://localhost:5044')
time_start = datetime.datetime.now()
date_start = datetime.datetime.today().date()


def calllogstashpipeline(card):
    """Make a request to logstash endpoint services

    :param card: A single card
    :return: Response status code
    """
    r = requests.post(logstashEndpoint, data=card, headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
    return r.status_code


def main():
    """Main function that iterate over all the cards and makes the request to the logstash endpoint

    :return:
    """
    cards = getcardsdata()
    try:
        for id in cards:
            print(json.dumps(cards[id], ensure_ascii=False, sort_keys=True))
            # calllogstashpipeline(json.dumps(cards[id], ensure_ascii=True, sort_keys=True))
    except requests.exceptions.RequestException as e:
        print(e)
    finally:
        print("Programa Finalizado, {} documentos procesados".format(len(cards)))


def getcustomfieldnamevalue(customfieldsref, customfield):
    """Function that will get a dict for a customField with name and value keys

    :param customfieldsref: customfields collection
    :param customfield: specific customfield
    :return: dict with name and value of the specific customfield provided by parameter
    """
    result = dict()
    cursor = customfieldsref.find({"_id": customfield['_id']})
    for document in cursor:
        result['name'] = document['name']
        if document['type'] == 'dropdown':
            for item in document["settings"]["dropdownItems"]:
                if item['_id'] == customfield['value']:
                    result['value'] = item['name']
        else:
            result['value'] = customfield['value']
    return result


def getwhitelistboards():
    """Get list of boards that will be in whitelist

    :return: A list of boards ids
    """
    text_file = open(os.path.dirname(os.path.abspath(__file__)) + "/white-list-boards.txt", "r")
    lines = text_file.read().split('\n')
    text_file.close()
    return lines


def getstorypoint(title):
    """Function that will get in the title the first characters as storypoints

    :param title: Card title
    :return:
    """
    tmp = ""
    for l in title:
        if l in ['.', ',', ' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            tmp += l
        else:
            break
    try:
        return float(tmp)
    except ValueError:
        return 0


def getcardsdata():
    """Function that will populate dict for logstash

    :return: A dict with the collections of all cards
    """
    # create connection string depending on whether mongo database accepts username and password or not
    conn_str = "mongodb://" + mongo_user + ":" + mongo_password + "@" + mongo_server + "/" + mongo_database \
        if mongo_user != '' else \
        "mongodb://" + mongo_server + "/" + mongo_database
    mongo = MongoClient(conn_str)
    db = mongo[mongo_database]
    users = db['users']
    boards = db['boards']
    lists = db['lists']
    cards = db['cards']
    card_comments = db['card_comments']
    activities = db['activities']
    swimlanes = db['swimlanes']
    customfields = db['customFields']

    # Get white list boards
    whitelistboards = getwhitelistboards()

    # Get cards data
    data = dict()
    # select cards for boards in whitelist file
    for card in cards.find({'boardId': {'$in': whitelistboards}}):

        # Create index on id of the card
        data[card["_id"]] = dict()

        # Get id
        data[card["_id"]]['id'] = card["_id"]

        # Get archived data
        data[card["_id"]]['isArchived'] = card["archived"]
        if card["archived"]:
            # Get date of archive process
            if activities.find({"cardId": card["_id"], "activityType": "archivedCard"}).count() >= 1:
                data[card["_id"]]["archivedAt"] = \
                    activities.find_one({"cardId": card["_id"], "activityType": "archivedCard"})["createdAt"]
                data[card["_id"]]["archivedAt"] = datetime.datetime.strftime(data[card["_id"]]["archivedAt"],
                                                                             "%Y-%m-%dT%H:%M:%S.000Z")

        # Get storypoint data
        data[card["_id"]]['storyPoint'] = getstorypoint(card["title"])

        # Get created date data
        data[card["_id"]]['createdAt'] = datetime.datetime.strftime(card["createdAt"], "%Y-%m-%dT%H:%M:%S.000Z")

        # Get dueAt date data
        if 'dueAt' not in card or card["dueAt"] is None:
            data[card["_id"]]['dueAt'] = 'None'
        else:
            data[card["_id"]]['dueAt'] = datetime.datetime.strftime(card["dueAt"], "%Y-%m-%dT%H:%M:%S.000Z")

        # Get last activity date data (will be updated after)
        data[card["_id"]]['lastModification'] = card["dateLastActivity"]

        # Get number of comments data
        data[card["_id"]]['nbComments'] = card_comments.count_documents({"cardId": card["_id"]})

        # Get creator name
        if users.count_documents({"_id": card["userId"]}) == 1 and 'username' in users.find_one(
                {"_id": card["userId"]}).keys():
            data[card["_id"]]['createdBy'] = users.find_one({"_id": card["userId"]})['username']
        else:
            data[card["_id"]]['createdBy'] = 'User not found'

        # Get swimlane name
        if swimlanes.count_documents({"_id": card["swimlaneId"]}) == 1:
            data[card["_id"]]['swimlaneTitle'] = swimlanes.find_one({"_id": card["swimlaneId"]})['title']
        else:
            data[card["_id"]]['swimlaneTitle'] = "Swimlane not found"

        # Get customs fields labels selected
        listofcustomfields = card["customFields"]
        for customField in listofcustomfields:
            keys = customField.keys()
            if 'value' in keys and customField.get('value') is not None:
                cf = getcustomfieldnamevalue(customfields, customField)
                data[card["_id"]][cf['name']] = cf['value']

        # Get list name
        if lists.count_documents({"_id": card["listId"]}) == 1:
            data[card["_id"]]['list'] = lists.find_one({"_id": card["listId"]})['title']
        else:
            data[card["_id"]]['list'] = 'List not found'

        # Get board data for board name and card title and label name
        if boards.count_documents({"_id": card["boardId"]}) == 1:
            # Get board data
            tmp_board = boards.find_one({"_id": card["boardId"]})
            data[card["_id"]]['board'] = tmp_board['title']
            data[card["_id"]]["boardId"] = tmp_board['_id']
            # Public board or in whitelist => get title of cards ?
            # if tmp_board["permission"] == 'public' or tmp_board["_id"] in whitelistboards:
            # Get title data
            data[card["_id"]]['title'] = card["title"]
            # else:
            # Get title data null
            #    data[card["_id"]]['title'] = ""
            # Get Labels name
            data[card["_id"]]["labels"] = list()
            if "labelIds" in card:
                for labelId in card["labelIds"]:
                    # We will parse board label
                    for label in tmp_board["labels"]:
                        if "_id" in label.keys() and labelId == label["_id"]:
                            if "name" not in label or label["name"] == '':
                                data[card["_id"]]["labels"].append(label["color"])
                            else:
                                data[card["_id"]]["labels"].append(label["name"])
            if "labelIds" not in card or len(card["labelIds"]) == 0:
                data[card["_id"]]['labels'].append('No label')
            # add card URL to dict
            data[card["_id"]]["cardUrl"] = baseURL + "/b/" + card["boardId"] + '/' + tmp_board[
                'title'].lower().replace(' ', '-') + '/' + card["_id"]
        else:
            data[card["_id"]]['board'] = 'Board not found'
            # Get title data null
            data[card["_id"]]['title'] = ""

        # Get members data
        data[card["_id"]]["members"] = list()
        if "members" in card:
            for member in card["members"]:
                if users.find({"_id": member}).count() == 1 and 'username' in users.find_one({"_id": member}).keys():
                    data[card["_id"]]['members'].append(users.find_one({"_id": member})['username'])
                else:
                    data[card["_id"]]['members'].append('User not found')
        if "members" not in card or len(card["members"]) == 0:
            data[card["_id"]]['members'].append('Unassigned')

        # Get assignees data
        data[card["_id"]]["assignees"] = list()
        if "assignees" in card:
            for member in card["assignees"]:
                if users.count_documents({"_id": member}) == 1 and 'username' in users.find_one({"_id": member}).keys():
                    data[card["_id"]]['assignees'].append(users.find_one({"_id": member})['username'])
                else:
                    data[card["_id"]]['assignees'].append('User not found')
        if "assignees" not in card or len(card["assignees"]) == 0:
            data[card["_id"]]['assignees'].append('Unassigned')

        # Get daily events and update lastModification of card
        data[card["_id"]]["dailyEvents"] = 0
        for activity in activities.find({"cardId": card["_id"]}):
            if activity["createdAt"].date() == date_start:
                data[card["_id"]]["dailyEvents"] += 1
            if activity["createdAt"] > data[card["_id"]]['lastModification']:
                data[card["_id"]]['lastModification'] = activity["createdAt"]

        # Fornat the lastModification date now
        data[card["_id"]]['lastModification'] = datetime.datetime.strftime(data[card["_id"]]['lastModification'],
                                                                           "%Y-%m-%dT%H:%M:%S.000Z")
    # End, time to return dict :)
    return data


if __name__ == "__main__":
    main()
