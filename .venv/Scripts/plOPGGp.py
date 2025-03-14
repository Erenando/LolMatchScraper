from bs4 import BeautifulSoup
import urllib.parse

def get_ingame_names(html):
    soup = BeautifulSoup(html, "html.parser")

    ingame_names = []
    for div in soup.find_all("div", class_="txt-info"):
        name = div.text.strip()
        if "#" in name:
            ingame_names.append(name)

    team1 = ingame_names[:5]
    team2 = ingame_names[5:]

    team1_url = "https://www.op.gg/multisearch/euw?summoners=" + ",".join([urllib.parse.quote(name) for name in team1])
    team2_url = "https://www.op.gg/multisearch/euw?summoners=" + ",".join([urllib.parse.quote(name) for name in team2])

    print("\n🔹 Team 1 OP.GG Link:", team1_url)
    print("🔹 Team 2 OP.GG Link:", team2_url)
    print("\n---------------------------------------\n")


def main():
    while True:
        print("🔹 Gib den HTML-Code ein. Drücke ENTER nach jeder Zeile und tippe 'ENDE', wenn du fertig bist.")
        print("🔹 Tippe 'EXIT', um das Programm zu beenden.\n")

        html_lines = []
        while True:
            line = input()
            if line.strip().upper() == "ENDE":
                break
            elif line.strip().upper() == "EXIT":
                print("\n🚀 Programm beendet.")
                return
            html_lines.append(line)

        html = "\n".join(html_lines)

        if html.strip():
            get_ingame_names(html)
        else:
            print("⚠ Kein HTML-Code eingegeben. Bitte versuche es erneut.\n")

if __name__ == "__main__":
    main()