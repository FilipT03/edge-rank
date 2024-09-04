from data import generator
from trie.trie import Trie
import time
import os
import re

affinity_graph = {}
popularity_map = {}
statuses = {}
username = ""
added_test = False
trie = Trie()

terminal_width = os.get_terminal_size().columns

def start():
    global affinity_graph, popularity_map, statuses
    try:
        affinity_graph, popularity_map, statuses = generator.load_premade()
    except FileNotFoundError:
        print("There is no premade graph. Creating one now... (this will take 10s-40s)")
        startTime = time.time()
        affinity_graph, popularity_map, statuses = generator.load_and_create_data()
        print(f"Loaded data and created graph in \033[92m{(time.time() - startTime):.3f}\033[0ms")
        generator.save_data(affinity_graph, popularity_map, statuses)
    choice = input("Do you want to add test data? [\033[92mY\033[0m/\033[91mN\033[0m]: ")
    if choice.lower() == "y" or choice.lower() == "yes":
        startTime = time.time()
        affinity_graph, popularity_map, statuses = generator.add_test_data(affinity_graph, popularity_map, statuses)
        print(f"Added test data in \033[92m{(time.time() - startTime):.3f}\033[0ms")
        global added_test
        added_test = True

    #startTime = time.time()
    create_trie()
    #print(f"Created trie in {(time.time() - startTime):.3f}s")

    global username
    username = input("Enter your full name to login (empty to exit): ")
    if not username:
        exit()
    main()

def create_trie():
    global trie, statuses
    for id in statuses.keys():
        #words = statuses[id][0].split("[\\s]+")
        words = re.split(r"[\.\s\,\!\'\"\`\(\)\\\/\?\-\_\=\[\]\:\;\@\*\+\–\&\’\>\<\…\”]+", statuses[id][0].strip())
        for word in words:
            if word:
                trie.add_word(word, id)

def error(err):
    print(f"\033[91m{err}\033[0m")

if os.name == "nt":
    def clear(): os.system('cls')
else:
    def clear(): os.system('clear')

def print_banner(username, clear_text:bool = True):
    if clear_text: clear()
    global terminal_width
    lenght = terminal_width - len('"EdgeRank" app') - len(username)
    print("="*terminal_width) #================================================
    print('"\033[31mEdge\033[0m\033[33mRank\033[0m" app' + (" "*lenght) + "\033[92m" + username + "\033[0m")
    print("="*terminal_width) #================================================

def print_start_options():
    global added_test, terminal_width
    print("="*terminal_width) #================================================
    print("\033[33m", end="")
    print("1. Search")       
    print("2. Exit", end="")
    if not added_test:
        print("\n3. Add test data", end="")
    print("\033[0m")
    print("―"*terminal_width) #――――――――――――――――――――――――――――――――――――――――――――――――
    while True:
        choice = input(">> ")
        if choice == "1":
            return 1
        elif choice == "2" or choice == "exit":
            exit()
        elif choice == "3" and not added_test:
            global affinity_graph, popularity_map, statuses
            startTime = time.time()
            affinity_graph, popularity_map, statuses = generator.add_test_data(affinity_graph, popularity_map, statuses)
            print(f"Added test data in {(time.time() - startTime):.3f}s")
            added_test = True
            return 2

def print_feed(search_values: dict = None, filter_words: list = None):
    if search_values == {}:
        return
    global affinity_graph, username, popularity_map, statuses, terminal_width
    top_ten = []
    for item in popularity_map.items():
        id = item[0]
        if search_values:
            if id not in search_values:
                continue
        author = item[1][0]
        popularity_score = item[1][1] # popularity is already multiplied by the time factor
        if username not in affinity_graph or author not in affinity_graph[username]:
            affinity_score = 0
        else:
            affinity_score = affinity_graph[username][author]
        score = (affinity_score + 1) * popularity_score
        if search_values:
            score *= search_values[id] ** 2
        if len(top_ten) < 10:
            top_ten.append((score, id))
        else:
            top_ten.sort() # since the list is so short, it doesn't hurt to sort it for simplicity
            if score > top_ten[0][0]:
                top_ten[0] = (score, id)
    top_ten.sort(reverse = True)
    i = 0
    for entry in top_ten:
        i += 1
        id = entry[1]
        status = statuses[id]
        print(f"\033[33m{i}\033[0m. {status[2]} said on {status[1]}:")
        print("-"*terminal_width*0) #------------------------------------------------
        to_print = status[0].replace("(y)", '👍').replace(":)",'🙂')
        if filter_words:
            for word in filter_words:
                #to_print = to_print.replace(word, f"\033[44m{word}\033[0m")
                lastIndex = 0
                try:
                    found = to_print.lower().index(word.lower(), lastIndex)
                except:
                    continue
                word_lenght = len(word)
                while True:
                    to_print = to_print[0:found] + "\033[44m" + \
                                to_print[found : found+word_lenght] + \
                                "\033[0m" + to_print[found + word_lenght :]
                    lastIndex = found + word_lenght + len("\033[44m\033[0m")
                    try:
                        found = to_print.lower().index(word.lower(), lastIndex)
                    except:
                        break
        print(to_print)
        print("-"*terminal_width*0) #------------------------------------------------
        print(f"Comments: {status[3]}   Shares: {status[4]}")
        print(f"👍: {status[5]}  💙:{status[6]}  😮: {status[7]}  😂: {status[8]}  🙁: {status[9]}  😠: {status[10]}")
        if i != len(top_ten):
            print("―"*terminal_width) #――――――――――――――――――――――――――――――――――――――――――――――――


def print_fraze(fraza):
    global affinity_graph, username, popularity_map, statuses, terminal_width
    top_ten = []
    for item in popularity_map.items():
        id = item[0]
        if fraza not in statuses[id][0]:
            continue
        author = item[1][0]
        popularity_score = item[1][1] # popularity is already multiplied by the time factor
        if username not in affinity_graph or author not in affinity_graph[username]:
            affinity_score = 0
        else:
            affinity_score = affinity_graph[username][author]
        score = (affinity_score + 1) * popularity_score
        if len(top_ten) < 10:
            top_ten.append((score, id))
        else:
            top_ten.sort() # since the list is so short, it doesn't hurt to sort it for simplicity
            if score > top_ten[0][0]:
                top_ten[0] = (score, id)
    top_ten.sort(reverse = True)
    i = 0
    for entry in top_ten:
        i += 1
        id = entry[1]
        status = statuses[id]
        print(f"\033[33m{i}\033[0m. {status[2]} said on {status[1]}:")
        print("-"*terminal_width*0) #------------------------------------------------
        to_print = status[0].replace("(y)", '👍').replace(":)",'🙂')
        lastIndex = 0
        try:
            found = to_print.lower().index(fraza.lower(), lastIndex)
        except:
            continue
        word_lenght = len(fraza)
        while True:
            to_print = to_print[0:found] + "\033[44m" + \
                        to_print[found : found+word_lenght] + \
                        "\033[0m" + to_print[found + word_lenght :]
            lastIndex = found + word_lenght + len("\033[44m\033[0m")
            try:
                found = to_print.lower().index(fraza.lower(), lastIndex)
            except:
                break
        print(to_print)
        print("-"*terminal_width*0) #------------------------------------------------
        print(f"Comments: {status[3]}   Shares: {status[4]}")
        print(f"👍: {status[5]}  💙:{status[6]}  😮: {status[7]}  😂: {status[8]}  🙁: {status[9]}  😠: {status[10]}")
        if i != len(top_ten):
            print("―"*terminal_width) #――――――――――――――――――――――――――――――――――――――――――――――――


def wait_for_continue(new_line = True):
    if new_line: print()
    input("Press ENTER to continue...")

def main():
    global username
    search_values = None
    words = None
    while True:
        print_banner(username, True)
        print_feed(search_values, words)
        choice = print_start_options()
        if choice == 1:
            global trie
            search_values = None
            while(True):
                query = input("Search: ")
                if query == "":
                    break        
                words = re.split(r"[\.\s\,\!\'\"\`\(\)\\\/\?\-\_\=\[\]\:\;\@\*\+\–\&\’\>\<\…\”]+", query.strip())
                if len(words) == 2:
                    if query[-1] == '*':
                        autocomplete = trie.autocomplete_word(words[0])
                        if autocomplete is None:
                            print("No matches")
                            continue
                        for_print = [(x,y) for y,x in autocomplete.items() if y!='']
                        for_print.sort(reverse=True)
                        for_print = [str(x[1]) for x in for_print]
                        for_print = for_print[0:9]
                        print(', '.join(for_print))
                        continue
                if query.count('"') == 2:
                    print_fraze(query[1:-1])
                    break
                for word in words:
                    if word == '':
                        continue
                    new_values = trie.find_all_word_occurences(word)
                    if not search_values:
                        search_values = new_values
                    elif new_values:
                        search_values = {k: search_values.get(k, 0) + new_values.get(k, 0) for k in set(search_values) | set(new_values)} # merging new values to old dict
                break
        else:
            search_values = None
            words = None


