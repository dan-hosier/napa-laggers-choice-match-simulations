#! /usr/bin/python2

import pickle
import random
import time


OPPONENT = "Rack And Run"
US = "Zoosters Millions"
GRAPHS = "one_line"
SIMULATION_COUNT = 5000


def get_combined_wins_losses(player, opponent, race_differential):
    """Get combined wins and losses for a player as it relates to the opponent

    player(dict): player dictionary
    opponent(dict): opponent dictionary
    race_differential(int): skill difference

    returns (combined_wins(int), combined_losses(int))
    """
    minimum_games = 10 
    combined_wins = 0
    combined_losses = 0
    for spread in [
        0,
        -1,
        1,
        -2,
        2,
        -3,
        3,
        -4,
        4
    ]:
        if (int(race_differential) + int(spread)) in player:
            combined_wins = (
                combined_wins + player[race_differential + spread]["games_won"]
            )
            combined_losses = (
                combined_losses + player[race_differential + spread]["games_lost"]
            )
        if (int(race_differential) + int(spread)) in opponent:
            combined_wins = (
                combined_wins + opponent[race_differential + spread]["games_lost"]
            )
            combined_losses = (
                combined_losses + opponent[race_differential + spread]["games_won"]
            )
        if combined_wins + combined_losses >= minimum_games:
            return (combined_wins, combined_losses, spread)
    return (combined_wins, combined_losses, 4)


def get_race(player1skill, player2skill):
    """Get the race between 2 players

    args:
      player1skill(int): skill rating of our player
      player2skill(int): skill rating of the opponent player

    returns:
      (unnamed list):  (ourrace, theirrace)
    """
    race_tables = {
        89: {
            74: (10, 2),
            68: (9, 2),
            58: (8, 2),
            48: (9, 3),
            42: (8, 3),
            35: (7, 3),
            28: (8, 4),
            22: (7, 4),
            17: (6, 4),
            11: (7, 5),
            4: (6, 5),
            -1: (6, 6),
        },
        69: {
            62: (8, 2),
            56: (7, 2),
            46: (6, 2),
            36: (7, 3),
            28: (6, 3),
            21: (5, 3),
            14: (6, 4),
            5: (5, 4),
            -1: (5, 5),
        },
        49: {
            48: (6, 2),
            39: (5, 2),
            29: (4, 2),
            18: (5, 3),
            6: (4, 3),
            -1: (4, 4),
        },
        39: {
            26: (4, 2),
            10: (3, 2),
            -1: (3, 3),
        },
        -1: {
            19: (3, 2),
            -1: (2, 2),
        },
    }
    stronger = max(player1skill, player2skill)
    weaker = min(player1skill, player2skill)
    difference = stronger - weaker
    for skillclass in reversed(sorted(race_tables)):
        if stronger > skillclass:
            for skill_level_difference in reversed(sorted(race_tables[skillclass])):
                if difference > skill_level_difference:
                    if stronger == player1skill:
                        return list(race_tables[skillclass][skill_level_difference])
                    else:
                        return list(
                            reversed(race_tables[skillclass][skill_level_difference])
                        )


def predict_typical(predictions, player_history):
    """Predict score by player's typical game play

    args:
      predictions(dict): prediction keyed by game ('8_ball', 9_ball, 10_ball)
      player_history(dict):  Player's history
        Example:
           u'Dan Hosier': {
             'player_id': u'10068287',
             '8_ball': {
               0: {'games_lost': 14, 'games_won': 12},
               1: {'games_lost': 2, 'games_won': 5},
               2: {'games_lost': 9, 'games_won': 24},
               3: {'games_lost': 0, 'games_won': 12},
               4: {'games_lost': 6, 'games_won': 22},
               -1: {'games_lost': 7, 'games_won': 5},
               -3: {'games_lost': 7, 'games_won': 1},
               -2: {'games_lost': 31, 'games_won': 23}
              },
              '9_ball': {
                0: {'games_lost': 10, 'games_won': 7},
                2: {'games_lost': 4, 'games_won': 5},
                3: {'games_lost': 3, 'games_won': 2}
              },
              '10_ball': {
                0: {'games_lost': 4, 'games_won': 2},
                1: {'games_lost': 4, 'games_won': 2},
                -1: {'games_lost': 14, 'games_won': 6},
                -2: {'games_lost': 6, 'games_won': 3}
              },
              'skill_level': [84, 62, 59]
           }
    """
    results = {}
    total_games_played = 0
    for game in ("8_ball", "9_ball", "10_ball"):
        games_played = 0
        for bucket in player_history[game]:
            games_played += player_history[game][bucket]["games_lost"]
            games_played += player_history[game][bucket]["games_won"]
        results[game] = games_played * predictions[game]
        total_games_played += games_played

    return round(
        (results["8_ball"] + results["9_ball"] + results["10_ball"])
        / total_games_played,
        2,
    )


def run_simulations(combined_win_percentage, my_race, their_race, SIMULATION_COUNT):
    """Run simulations based on combined_win_percentage, games needed for a win
    and bucket the results across the points received per simulation

    args:
      combined_win_percentage(float):  Average of (
        our player's percentage games won  at this race,
        their player's percentage games lost at this race
      )
      my_race(int):  games needed for our player to win
      their_race(int):  games needed for their player to win
      SIMULATION_COUNT(int):  Number of iterations to get the counts.

    returns:
      results(dict):  Dictionary of simulation result counts bucketed by points earned by our player
        ex.
          results{
            1:  5000,
            3:  30000,
            6:  30000,
            14: 30000,
            20: 5000,
          }
    """
    results = {
        1: 0,  # no wins
        3: 0,  # 1 win
        6: 0,  # hill loss
        14: 0,  # match win
        20: 0,  # shutout
    }
    for x in range(0, SIMULATION_COUNT):
        games_won = 0
        games_lost = 0
        while True:
            if combined_win_percentage > random.randrange(100):
                games_won += 1
            else:
                games_lost += 1
            if any((games_won == my_race, games_lost == their_race)):
                break
        if games_lost == their_race:  # I lost
            if games_won == my_race - 1:
                results[6] += 1
            elif games_won > 0:
                results[3] += 1
            else:
                results[1] += 1
        else:  # I won
            if games_lost == 0:
                results[20] += 1
            else:
                results[14] += 1
    return results


data_file = open("data.pkl", "rb")
players = pickle.load(data_file)

predictions = {}
for player in players[US]:
    predictions.setdefault(player, {})
    game_map = {0: "8  ", 1: "9  ", 2: "10 "}
    try:
        print (
            "\n\n#### %s %s ####"
            % (
                player,
                " ".join(
                    [
                        str(players[US][player]["skill_level"][0]),
                        str(players[US][player]["skill_level"][1]),
                        str(players[US][player]["skill_level"][2]),
                    ]
                ),
            )
        )
    except:
        pass
    for against in players[OPPONENT]:
        try:
            predictions[player].setdefault(against, {})
            predictions[player][against].setdefault("combined", {})
            seed_games = {"8_ball": 0, "9_ball": 0, "10_ball": 0}
            spread = {"8_ball": 0, "9_ball": 0, "10_ball": 0}
            results = {}
            for bucket in ["c_loss", "loss", "h_loss", "win", "c_win", "one_line"]:
                results.setdefault(bucket, [])
            game_index = 0
            races = []
            for game in ("8_ball", "9_ball", "10_ball"):
                predictions[player][against].setdefault(game, 10)
                my_race, their_race = get_race(
                    players[US][player]["skill_level"][game_index],
                    players[OPPONENT][against]["skill_level"][game_index],
                )
                race_differential = my_race - their_race
                combined_wins, combined_losses, spread_count = get_combined_wins_losses(
                    players[US][player][game],
                    players[OPPONENT][against][game],
                    race_differential,
                )
                combined_total = combined_wins + combined_losses
                seed_games[game] = seed_games[game] + combined_total
                spread[game] = spread[game] + spread_count 
                if combined_total == 0:
                    combined_win_percentage = 50
                else:
                    combined_win_percentage = (
                        float(combined_wins) / combined_total
                    ) * 100
                simulation_results = run_simulations(
                    combined_win_percentage, my_race, their_race, SIMULATION_COUNT
                )
                distribution = [
                    int(float(simulation_results[1]) / SIMULATION_COUNT * 100 + 0.5),
                    int(float(simulation_results[3]) / SIMULATION_COUNT * 100 + 0.5),
                    int(float(simulation_results[6]) / SIMULATION_COUNT * 100 + 0.5),
                    int(float(simulation_results[14]) / SIMULATION_COUNT * 100 + 0.5),
                    int(float(simulation_results[20]) / SIMULATION_COUNT * 100 + 0.5),
                ]
                predictions[player][against][game] = (
                    (distribution[1] * 3)
                    + (distribution[2] * 6)
                    + (distribution[3] * 14)
                    + (distribution[4] * 20)
                ) / 100.0
                while sum(distribution) < 100:
                    distribution[3] += 1
                while sum(distribution) > 100:
                    distribution[3] -= 1
                races.append("%s: %s-%s" % (game, my_race, their_race))
                results["c_loss"].append(game_map[game_index] * distribution[0])
                results["loss"].append(game_map[game_index] * distribution[1])
                results["h_loss"].append(game_map[game_index] * distribution[2])
                results["win"].append(game_map[game_index] * distribution[3])
                results["c_win"].append(game_map[game_index] * distribution[4])
                if seed_games[game] < 10:
                    results["one_line"].append(
                        game_map[game_index] + "Not enough results".center(100)
                    )
                else:
                    results["one_line"].append(
                        game_map[game_index]
                        + u"\u001b[45;1m"
                        + str(distribution[0]).center(distribution[0])
                        + u"\u001b[0m"
                        + u"\u001b[41;1m"
                        + str(distribution[1]).center(distribution[1])
                        + u"\u001b[0m"
                        + u"\u001b[43;1m"
                        + str(distribution[2]).center(distribution[2])
                        + u"\u001b[0m"
                        + u"\u001b[42;1m"
                        + str(distribution[3]).center(distribution[3])
                        + u"\u001b[0m"
                        + u"\u001b[44;1m"
                        + str(distribution[4]).center(distribution[4])
                        + u"\u001b[0m : "
                        + str(predictions[player][against][game])
                    )

                game_index += 1
            print "%s --- %s --- seed games %s, %s, %s --- skill %s %s %s --- spreads %s %s %s" % (
                against,
                ", ".join(races),
                seed_games["8_ball"],
                seed_games["9_ball"],
                seed_games["10_ball"],
                str(players[OPPONENT][against]["skill_level"][0]),
                str(players[OPPONENT][against]["skill_level"][1]),
                str(players[OPPONENT][against]["skill_level"][2]),
                spread["8_ball"],
                spread["9_ball"],
                spread["10_ball"],
            )
            if GRAPHS == "bucket_per_line":
                for bucket in ["c_loss", "loss", "h_loss", "win", "c_win"]:
                    for line in results[bucket]:
                        print "%s:\t%s" % (bucket, line)
            elif GRAPHS == "one_line":
                for line in results["one_line"]:
                    print line

            our_pick = max(
                predictions[player][against]["8_ball"],
                predictions[player][against]["9_ball"],
                predictions[player][against]["10_ball"],
            )
            their_pick = predict_typical(
                predictions[player][against], players[OPPONENT][against]
            )
            print (
                "Predictions:  Our Pick %s,   Their Pick %s,   Combined %s"
                % (our_pick, their_pick, ((our_pick + their_pick) / 2))
            )
            predictions[player][against]["combined"] = str(
                round((our_pick + their_pick) / 2, 2)
            )
            print "-" * 103
        except:
            pass


predictions_file = open("predictions.pkl", "wb")
pickle.dump(predictions, predictions_file)
predictions_file.close()
