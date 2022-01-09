#! /usr/bin/python2

import random
import time

from selenium import webdriver

opponent = "Just Hard Enough"
us = "Zoosters Millions"
division = 9321
simulation_count = 100000
graphs = "one_line"

BASEURL = "https://www.napaleagues.com/stats.php?playerSelected=Y&playerID"
ROSTERSURL = "https://www.napaleagues.com/roster_grid.php?did=%s" % division

WEBDRIVER = "Chrome"


XPATHS = {
    "8ball_skill": "/html/body/div/div/div/table/tbody/tr[12]/td[2]/h5",
    "9ball_skill": "/html/body/div/div/div/table/tbody/tr[13]/td[2]/h5",
    "10ball_skill": "/html/body/div/div/div/table/tbody/tr[14]/td[2]/h5",
    "score_tables": "/html/body/div/div/div/",
}


def get_rosters(browser, url):
    players = {}
    browser.get(url)
    browser.implicitly_wait(6)
    for row in browser.find_elements_by_xpath("/html/body/table/tbody/tr"):
        for team in row.find_elements_by_xpath("./td"):
            teamname = None
            for player in team.find_elements_by_xpath("./table/tbody/tr"):
                data = player.find_element_by_xpath("./td[2]").text
                if teamname is None:
                    teamname = data.split("\n")[0]
                    players.setdefault(teamname, {})
                else:
                    playername, playerid = data.split("\n")
                    players[teamname].setdefault(playername, {})
                    players[teamname][playername]["player_id"] = playerid
            teamname = None
    return players


def get_race(player1skill, player2skill):
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


def create_connection(driver=WEBDRIVER):
    """Create a connection to the web driver

    args:
        driver(str): Which webdriver (Chrome default)
    returns:
        browser(selenium.webdriver):  Handle to the selenium webdriver class
    """
    browser = None
    if driver == "Chrome":
        browser = webdriver.Chrome()
        browser.implicitly_wait(10)
    else:
        pass

    return browser


def get_player_skill_levels(browser, player_id):
    try:
      browser.get("%s=%s" % (BASEURL, player_id))
      browser.implicitly_wait(6)

      sl8 = browser.find_element_by_xpath(XPATHS["8ball_skill"]).text
      sl9 = browser.find_element_by_xpath(XPATHS["9ball_skill"]).text
      sl10 = browser.find_element_by_xpath(XPATHS["10ball_skill"]).text
      return [int(sl8), int(sl9), int(sl10)]
    except:
      pass


def get_player_stats(browser, player_id, game):
    results = {}
    game_tabs = {"8_ball": "2", "9_ball": "3", "10_ball": "4"}
    for page in ["0", "10", "20", "30"]:
        time.sleep(0.5)
        browser.get(
            "%s=%s&xTab=%s&start=%s" % (BASEURL, player_id, game_tabs[game], page)
        )
        browser.implicitly_wait(6)
        this_player = browser.find_element_by_xpath(
            "/html/body/div/div/div/table[1]/tbody/tr[2]/td/h2"
        ).text
        matches = browser.find_elements_by_class_name("card-body")
        for match in matches:
            try:
                tables = match.find_elements_by_xpath("./table")
                for table in tables[2:-2]:
                    if "y forfeit" in table.text:
                        continue
                    player1 = table.find_element_by_xpath(
                        "./tbody/tr[2]/td[2]"
                    ).text.replace("\n", " ")
                    if player1 == this_player:
                        skill_diff = int(
                            table.find_element_by_xpath("./tbody/tr[3]/td[2]").text
                        ) - int(table.find_element_by_xpath("./tbody/tr[3]/td[3]").text)
                        results.setdefault(
                            skill_diff, {"games_won": 0, "games_lost": 0}
                        )
                        results[skill_diff]["games_won"] = results[skill_diff][
                            "games_won"
                        ] + int(table.find_element_by_xpath("./tbody/tr[7]/td[2]").text)
                        results[skill_diff]["games_lost"] = results[skill_diff][
                            "games_lost"
                        ] + int(table.find_element_by_xpath("./tbody/tr[7]/td[3]").text)
                    else:
                        skill_diff = int(
                            table.find_element_by_xpath("./tbody/tr[3]/td[3]").text
                        ) - int(table.find_element_by_xpath("./tbody/tr[3]/td[2]").text)
                        results.setdefault(
                            skill_diff, {"games_won": 0, "games_lost": 0}
                        )
                        results[skill_diff]["games_won"] = results[skill_diff][
                            "games_won"
                        ] + int(table.find_element_by_xpath("./tbody/tr[7]/td[3]").text)
                        results[skill_diff]["games_lost"] = results[skill_diff][
                            "games_lost"
                        ] + int(table.find_element_by_xpath("./tbody/tr[7]/td[2]").text)
            except:
                pass

    return results


def run_simulations(combined_win_percentage, my_race, their_race, simulation_count):
    results = {
        1: 0,  # no wins
        3: 0,  # 1 win
        6: 0,  # hill loss
        14: 0,  # match win
        20: 0,  # shutout
    }
    for x in range(0, simulation_count):
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


browser = create_connection(WEBDRIVER)
players = get_rosters(browser, ROSTERSURL)

for player in players[us]:
    players[us][player].setdefault("skill_level", [])
    players[us][player]["skill_level"] = get_player_skill_levels(
        browser, players[us][player]["player_id"]
    )
    for game in ["8_ball", "9_ball", "10_ball"]:
        players[us][player].setdefault(game, [])
        players[us][player][game] = get_player_stats(
            browser, players[us][player]["player_id"], game
        )

for player in players[opponent]:
    players[opponent][player].setdefault("skill_level", [])
    players[opponent][player]["skill_level"] = get_player_skill_levels(
        browser, players[opponent][player]["player_id"]
    )
    for game in ["8_ball", "9_ball", "10_ball"]:
        players[opponent][player].setdefault(game, [])
        players[opponent][player][game] = get_player_stats(
            browser, players[opponent][player]["player_id"], game
        )
predictions = {}
for player in players[us]:
    predictions.setdefault(player, {})
    game_map = {0: "8  ", 1: "9  ", 2: "10 "}
    print (
        "\n\n#### %s %s ####"
        % (
            player,
            " ".join(
                [
                    str(players[us][player]["skill_level"][0]),
                    str(players[us][player]["skill_level"][1]),
                    str(players[us][player]["skill_level"][2]),
                ]
            ),
        )
    )
    for against in players[opponent]:
        try:
            predictions[player].setdefault(against, {})
            seed_games = {"8_ball": 0, "9_ball": 0, "10_ball": 0}
            results = {}
            for bucket in ["c_loss", "loss", "h_loss", "win", "c_win", "one_line"]:
                results.setdefault(bucket, [])
            game_index = 0
            races = []
            for game in ("8_ball", "9_ball", "10_ball"):
                predictions[player][against].setdefault(game, 10)
                my_race, their_race = get_race(
                    players[us][player]["skill_level"][game_index],
                    players[opponent][against]["skill_level"][game_index],
                )
                skill_difference = my_race - their_race
                combined_wins = 0
                combined_losses = 0
                for spread in [-1, 0, 1]:
                    if (int(skill_difference) + int(spread)) in players[us][player][
                        game
                    ]:
                        combined_wins = (
                            combined_wins
                            + players[us][player][game][skill_difference + spread][
                                "games_won"
                            ]
                        )
                        combined_losses = (
                            combined_losses
                            + players[us][player][game][skill_difference + spread][
                                "games_lost"
                            ]
                        )
                    if ((int(skill_difference) + int(spread)) * -1) in players[
                        opponent
                    ][against][game]:
                        combined_wins = (
                            combined_wins
                            + players[opponent][against][game][
                                (skill_difference + spread) * -1
                            ]["games_lost"]
                        )
                        combined_losses = (
                            combined_losses
                            + players[opponent][against][game][
                                (skill_difference + spread) * -1
                            ]["games_won"]
                        )
                combined_total = combined_wins + combined_losses
                seed_games[game] = seed_games[game] + combined_total
                if combined_total == 0:
                    combined_win_percentage = 50
                else:
                    combined_win_percentage = (
                        float(combined_wins) / combined_total
                    ) * 100
                simulation_results = run_simulations(
                    combined_win_percentage, my_race, their_race, simulation_count
                )
                distribution = [
                    int(float(simulation_results[1]) / simulation_count * 100 + 0.5),
                    int(float(simulation_results[3]) / simulation_count * 100 + 0.5),
                    int(float(simulation_results[6]) / simulation_count * 100 + 0.5),
                    int(float(simulation_results[14]) / simulation_count * 100 + 0.5),
                    int(float(simulation_results[20]) / simulation_count * 100 + 0.5),
                ]
                predictions[player][against][game] = (
                    (distribution[1] * 3)
                    + (distribution[2] * 6)
                    + (distribution[3] * 14)
                    + (distribution[4] * 20)
                ) / 100
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
                        game_map[game_index]
                        + "Not enough results".center(100)
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
                        + u"\u001b[0m"
                    )

                game_index += 1
            print "%s --- %s --- seed games %s, %s, %s --- skill %s %s %s" % (
                against,
                ", ".join(races),
                seed_games["8_ball"],
                seed_games["9_ball"],
                seed_games["10_ball"],
                str(players[opponent][against]["skill_level"][0]),
                str(players[opponent][against]["skill_level"][1]),
                str(players[opponent][against]["skill_level"][2]),
            )
            if graphs == "bucket_per_line":
                for bucket in ["c_loss", "loss", "h_loss", "win", "c_win"]:
                    for line in results[bucket]:
                        print "%s:\t%s" % (bucket, line)
            elif graphs == "one_line":
                for line in results["one_line"]:
                    print line
            print "-" * 103
        except:
            pass
for against in players[opponent]:
    print "===== %s =====" % against
    for player in predictions:
        for game in predictions[player][against]:
            print (
                "%s vs %s at %s = %s"
                % (player, against, game, predictions[player][against][game])
            )
        print "-----------------------------------"

browser.close()
