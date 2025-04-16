from GoogleAPIConnector import parse_game

def main():
    parsing_option = input("Wählen Sie eine Parsing Option aus (lcu / replay): ")
    if parsing_option == "lcu":
        parse_game()
    elif parsing_option == "replay":
        ## TODO create option for replay parsing
        pass
    else:
        print("Ungültige Option. Bitte wählen Sie 'lcu' oder 'replay'.")
        return



if __name__ == "__main__":
    main()