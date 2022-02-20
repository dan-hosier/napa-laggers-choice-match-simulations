#! /usr/bin/python2

import pickle
import itertools


def available_players(team):
    """get available players for a team

    args team(dict)

    returns available[list]: list of names of team members
    """
    available = []
    for index in team:
        if team[index][1] == "available":
            available.append(team[index][0])
    return available


def member_availability(our_team, their_team):

    context = "our_team"
    while context == "our_team":
        print "Toggle our team member availability"
        print ("0: Continue to their team")
        for index in sorted(our_team.keys()):
            print ("%s: %s (%s)" % (str(index), our_team[index][0], our_team[index][1]))
        selection = raw_input(">  ")
        try:
            if int(selection) == 0:
                context = "their_team"
            else:
                if our_team[int(selection)][1] == "available":
                    our_team[int(selection)][1] = "unavailable"
                else:
                    our_team[int(selection)][1] = "available"
        except:
            pass
    print ("==================================")
    while context == "their_team":
        print ("Toggle their team member availability")
        print ("0:  Continue")
        for index in sorted(their_team.keys()):
            print (
                "%s: %s (%s)" % (str(index), their_team[index][0], their_team[index][1])
            )
        selection = raw_input(">  ")
        try:
            if int(selection) == 0:
                context = "best_play"
            else:
                if their_team[int(selection)][1] == "available":
                    their_team[int(selection)][1] = "unavailable"
                else:
                    their_team[int(selection)][1] = "available"
        except:
            pass
    return our_team, their_team


def remove_duplicate_play(all_permutations_team_duplicate_play):
    all_permutations_team = []
    counter = 0
    for set in all_permutations_team_duplicate_play:
        counter += 1
        skip = False
        us_found = []
        them_found = []
        for subset in set:
            if any((subset[0] in us_found, subset[1] in them_found)):
                skip = True
            else:
                us_found.append(subset[0])
                them_found.append(subset[1])
        if not skip:
            all_permutations_team.append(set)
    print (counter, len(all_permutations_team))
    return all_permutations_team


def best_scenario(games_remaining, our_available, their_available, their_pick=None):
    """Get best scenario (this game and remaining games)

    args:
      games_remaining(int): number of games remaining
      our_available(list): our available players
      their_available(list): their available players
      their_pick (str): optionsl their pick

    returns:
      best pick (str): our player best pick
    """
    us = {k: v for k, v in enumerate(our_available)}
    them = {k: v for k, v in enumerate(their_available)}
    all_permutations_individual = {}
    all_permutations_team = []
    for player in us:
        for opponent in them:
            all_permutations_individual[(player, opponent)] = predictions[us[player]][
                them[opponent]
            ]["combined"]
    all_permutations_team_duplicate_play = itertools.permutations(
        all_permutations_individual.keys(), games_remaining
    )
    all_permutations_team = remove_duplicate_play(all_permutations_team_duplicate_play)

    if not their_pick:
        picks = {}
        for player in us:
            this_match_count = 0
            this_match_total = 0
            player_count = 0
            player_total = 0
            for set in all_permutations_team:
                if player == set[0][0]:
                    if all_permutations_individual[set[0]]:
                        this_match_count += 1
                        this_match_total += float(all_permutations_individual[set[0]])
                    for subset in set[1:]:
                        if all_permutations_individual[subset]:
                            player_count += 1
                            player_total += float(all_permutations_individual[subset])
            player_count = max(1, player_count)
            this_match_count = max(1, this_match_count)
            predicted_score = (this_match_total / this_match_count) + (
                player_total / player_count
            ) * games_remaining -1 
            picks.setdefault(predicted_score, [])
            picks[predicted_score].append(us[player])
        print (
            "===== blind selections:  expect score for next %s games ====="
            % games_remaining
        )
        for k in sorted(picks.keys(), reverse=True):
            print picks[k], k
    else:
        for k in them:
            if them[k] == their_pick:
                they_picked = k
        picks = {}
        for player in us:
            this_match_count = 0
            this_match_total = 0
            player_count = 0
            player_total = 0
            for set in all_permutations_team:
                if all((player == set[0][0], they_picked == set[0][1])):
                    if all_permutations_individual[set[0]]:
                        this_match_count += 1
                        this_match_total += float(all_permutations_individual[set[0]])
                    for subset in set[1:]:
                        if all_permutations_individual[subset]:
                            player_count += 1
                            player_total += float(all_permutations_individual[subset])
            player_count = max(1, player_count)
            this_match_count = max(1, this_match_count)
            predicted_score = (this_match_total / this_match_count) + (
                player_total / player_count
            ) * (games_remaining - 1)
            picks.setdefault(predicted_score, [])
            picks[predicted_score].append(us[player])
        print (
            "===== player against %s expect score for next %s games ====="
            % (their_pick, games_remaining)
        )
        for k in sorted(picks.keys(), reverse=True):
            print picks[k], k


data_file = open("predictions.pkl", "rb")
predictions = pickle.load(data_file)


our_team = {}
index_number = 1
for player in predictions:
    our_team[index_number] = [player, "available"]
    index_number += 1

their_team = {}
index_number = 1
for player in predictions[our_team[1][0]]:
    their_team[index_number] = [player, "available"]
    index_number += 1

print ("==================================")
print ("Enter number of games (no more than the minimum number of players)")
games_remaining = raw_input(">  ")

print ("==================================")
print ("Which team is putting up?  1. Us,   2. Them")
put_up = raw_input(">  ")

for i in range(int(games_remaining), 0, -1):
    print ("==================================")
    print ("%s games remaining" % str(i))
    our_team, their_team = member_availability(our_team, their_team)
    if int(put_up) == 1:
        best_scenario(i, available_players(our_team), available_players(their_team))
        put_up = 2
    else:
        print ("Their selection")
        for index in sorted(their_team.keys()):
            print (
                "%s: %s (%s)" % (str(index), their_team[index][0], their_team[index][1])
            )
        their_player = raw_input(">  ")
        best_scenario(
            i,
            available_players(our_team),
            available_players(their_team),
            their_team[int(their_player)][0],
        )
        put_up = 1
