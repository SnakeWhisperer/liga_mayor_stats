import csv
import re
import requests
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape(teams=[], pt=False):

    if not teams:
        print('No se seleccionó ningún equipo.')
        return

    teams_dict = {
        'CQS': 0,
        'CTS': 1,
        'DEL': 2,
        'GUE': 3,
        'LDR': 4,
        'MAR': 5,
        'SAM': 6,
        'SEN': 7
    }

    team_keys = [teams_dict.get(team, None) for team in teams]

    stats = {
        0: {'name': 'Caciques', 'hitting': [], 'pitching': []},
        1: {'name': 'Centauros', 'hitting': [], 'pitching': []},
        2: {'name': 'Delfines', 'hitting': [], 'pitching': []},
        3: {'name': 'Guerreros', 'hitting': [], 'pitching': []},
        4: {'name': 'Líderes', 'hitting': [], 'pitching': []},
        5: {'name': 'Marineros', 'hitting': [], 'pitching': []},
        6: {'name': 'Samanes', 'hitting': [], 'pitching': []},
        7: {'name': 'Senadores', 'hitting': [], 'pitching': []},
    }

    DRIVER_PATH = 'C:/chromedriver.exe'
    options = Options()
    # options.headless = True
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    for i, team in enumerate(teams):
        driver.get(f'https://www.lmbp.net')
        time.sleep(3)

        nav_teams = driver.find_element(
            By.XPATH,
            '/html/body/header/nav/div/div/ul/li[10]/a'
        )

        nav_teams.click()

        time.sleep(3)

        if team == 'CQS':
            xpath = '/html/body/main/div/div/div[2]/div/div[1]/div/a'
        elif team == 'CTS':
            xpath = '/html/body/main/div/div/div[2]/div/div[2]/div/a'
        elif team == 'DEL':
            xpath = '/html/body/main/div/div/div[2]/div/div[3]/div/a'
        elif team == 'GUE':
            xpath = '/html/body/main/div/div/div[2]/div/div[4]/div/a'
        elif team == 'LDR':
            xpath = '/html/body/main/div/div/div[2]/div/div[5]/div/a'
        elif team == 'MAR':
            xpath = '/html/body/main/div/div/div[2]/div/div[6]/div/a'
        elif team == 'SAM':
            xpath = '/html/body/main/div/div/div[2]/div/div[7]/div/a'
        elif team == 'SEN':
            xpath = '/html/body/main/div/div/div[2]/div/div[8]/div/a'


        team_link = driver.find_element(
            By.XPATH,
            xpath
        )

        team_link.click()


        print(f'Working on {team}')

        time.sleep(3)


        hitting_stats = get_stats('bat', driver)
        pitching_stats = get_stats('pit', driver)

        team_key = teams_dict[team]

        stats[team_key]['hitting'] = hitting_stats
        stats[team_key]['pitching'] = pitching_stats

    return stats



def get_stats(stats_type, driver, pt=False):
    if stats_type == 'bat':
        bat_stats_button = driver.find_element(
            By.XPATH,
            '//*[@id="e-bateo-boton"]'
        )

        bat_stats_button.click()

    elif stats_type == 'pit':
        pit_stats_button = driver.find_element(
            By.XPATH,
            '//*[@id="e-pitcheo-boton"]'
        )

        pit_stats_button.click()


    time.sleep(5)

    player_rows = driver.find_elements(
        By.XPATH,
        f'/html/body/main/div/div/div[5]/div/div/div/table/tbody/tr'
    )

    stats_cols = driver.find_elements(
        By.XPATH,
        "/html/body/main/div/div/div[5]/div/div/div/table/thead/tr/th"
    )

    headers = [el.get_attribute('innerHTML') for el in stats_cols]

    print(headers)

    headers[0] = 'id'

    all_player_stats = []
    all_player_stats.append(headers)

    for i in range(len(player_rows)):

        current_stats = []

        try:
            player_link = player_rows[i].find_element(
                By.XPATH,
                f'./td[2]/a'
                # /html/body/main/div/div/div[5]/div/div/div/table/tbody/tr[1]/td[2]/a
            )
        except NoSuchElementException:
            break

        player_name = player_link.get_attribute('innerHTML')
        player_name = re.sub('[\*#]', '', player_name).strip()
        player_link = player_link.get_attribute('href')
        player_id = re.search('\d+', player_link).group()

        current_stats.append(player_id)
        current_stats.append(player_name)

        print('Name: ', current_stats[1])
        print('ID: ', current_stats[0])
        print('\n')

        current_player_stats_els = player_rows[i].find_elements(
            By.XPATH,
            f'./td'
        )

        for j, stat_el in enumerate(current_player_stats_els):
            if j < 2:
                continue

            current_val = stat_el.get_attribute('innerHTML')

            # current_val = re.sub(
            #     '[^\w]',
            #     '',
            #     stat_el.get_attribute('innerHTML')
            # )

            current_stats.append(current_val)

        all_player_stats.append(current_stats)

    return all_player_stats


def dump_stats(stats):
    url = 'http://192.168.4.100/pizarra/scrapping/estadisticas.php'

    responses = ''

    for key in stats.keys():
        for i in range(1, len(stats[key]['hitting'])):
            responses += '\n' + stats[key]['hitting'][i][1]
            cleansed_hit_stats = {
                'proceso': 2,
                'posicion': '2B',
                'ci': stats[key]['hitting'][i][10],
                'hr': stats[key]['hitting'][i][9],
                'peb': stats[key]['hitting'][i][17].replace('.', ''),
                'h': stats[key]['hitting'][i][6],
                'bb': stats[key]['hitting'][i][13],
                'vb': stats[key]['hitting'][i][4],
                'gp': stats[key]['hitting'][i][3],
                'dosb': stats[key]['hitting'][i][7],
                'tresb': stats[key]['hitting'][i][8],
                'sf': stats[key]['hitting'][i][18],
                'ave': stats[key]['hitting'][i][2].replace('.', ''),
                'slg': stats[key]['hitting'][i][12].replace('.', ''),
                'id': stats[key]['hitting'][i][0],
            }

            response = requests.post(url, data=cleansed_hit_stats)
            responses += '\n' + str(response) + '\n' + response.text + '\n\n'

            print(response.text)
            print(f'Jugador {stats[key]["hitting"][i][0]}.')
            print('\n')

        for i in range(1, len(stats[key]['pitching'])):
            responses += '\n' + stats[key]['pitching'][i][1]

            ganados = re.sub('\-.*$', '', stats[key]['pitching'][i][3])
            perdidos = re.sub('^.*\-', '', stats[key]['pitching'][i][3])

            cleansed_pit_stats = {
                'proceso': 3,
                'posicion': 'P',
                'ganados': ganados,
                'perdidos': perdidos,
                'salvados': stats[key]['pitching'][i][8],
                'ip': stats[key]['pitching'][i][9],
                'strikes': stats[key]['pitching'][i][14],
                'bb': stats[key]['pitching'][i][13],
                'cl': stats[key]['pitching'][i][12],
                'efe': stats[key]['pitching'][i][2],
                'id': stats[key]['pitching'][i][0],
            }

            response = requests.post(url, data=cleansed_pit_stats)
            responses += '\n' + str(response) + '\n' + response.text + '\n\n'

            print(response.text)
            print(f'Jugador {stats[key]["pitching"][i][0]}.')
            print('\n')

    return responses


def dump_player(stats, id):
    url = 'http://192.168.4.100/pizarra/scrapping/estadisticas.php'
    
    for key in stats.keys():
        for i in range(1, len(stats[key]['hitting'])):
            if id in stats[key]['hitting'][i]:
                cleansed_hit_stats = {
                    'proceso': 2,
                    'posicion': '2B',
                    'ci': stats[key]['hitting'][i][10],
                    'hr': stats[key]['hitting'][i][9],
                    'peb': stats[key]['hitting'][i][17].replace('.', ''),
                    'h': stats[key]['hitting'][i][6],
                    'bb': stats[key]['hitting'][i][13],
                    'vb': stats[key]['hitting'][i][4],
                    'gp': stats[key]['hitting'][i][3],
                    'dosb': stats[key]['hitting'][i][7],
                    'tresb': stats[key]['hitting'][i][8],
                    'sf': stats[key]['hitting'][i][18],
                    'ave': stats[key]['hitting'][i][2].replace('.', ''),
                    'slg': stats[key]['hitting'][i][12].replace('.', ''),
                    'id': stats[key]['hitting'][i][0],
                }

                print(cleansed_hit_stats)
                response = requests.post(url, data=cleansed_hit_stats)
                print(response.text)
                break


        for i in range(1, len(stats[key]['pitching'])):
            if id in stats[key]['pitching'][i]:
                ganados = re.sub('\-.*$', '', stats[key]['pitching'][i][3])
                perdidos = re.sub('^.*\-', '', stats[key]['pitching'][i][3])

                cleansed_pit_stats = {
                    'proceso': 3,
                    'posicion': 'P',
                    'ganados': ganados,
                    'perdidos': perdidos,
                    'salvados': stats[key]['pitching'][i][8],
                    'ip': stats[key]['pitching'][i][9],
                    'strikes': stats[key]['pitching'][i][14],
                    'bb': stats[key]['pitching'][i][13],
                    'cl': stats[key]['pitching'][i][12],
                    'efe': stats[key]['pitching'][i][2],
                    'id': stats[key]['pitching'][i][0],
                }

                print(cleansed_pit_stats)
                response = requests.post(url, data=cleansed_pit_stats)
                print(response.text)
                break