"""Imports processing functions"""

import dataproject.utils as utils


def main():
    """main function of program"""
    first_file = input("""Welcome to the data handler
    Formats accepted 'csv', 'dat' and 'json\n
    Enter the name or path of your first file (To quit type 'q'): """)
    if 'q' == first_file.lower():
        exit()
    else:
        pass
    second_file = input("Enter the name or path of your second file: ")
    user_input = first_file, second_file
    documents = utils.files(user_input[0], user_input[1])
    if documents[2] == "csv":
        data = utils.datacsv(documents[0], documents[1])
    elif documents[2] == "dat":
        data = utils.datadat(documents[0], documents[1])
    elif documents[2] == "json":
        data = utils.datajson(documents[0], documents[1])

    elif documents[2] is False:
        chosen = True
        while chosen:
            choice = input("Want to start over? 'y'/'n': ")
            if choice.lower() == "y":
                main()
            elif choice.lower() == "n":
                exit()
            else:
                while True:
                    print("Option not recognized")
                    choice2 = input("Please select 'y' or 'n': ")
                    if choice2.lower() == "y":
                        main()
                    elif choice2.lower() == "n":
                        exit()
                    else:
                        continue
    dataset1, dataset2 = (set(data[0]), set(data[1]))
    print("Datasets acquired, please select what would you like to do with them...")
    while True:
        instruction = input("""Join datasets (Enter 'J'), Find intersecting values (Enter 'I')
        Find excluded values (Enter 'E'), Find unique values (Enter 'U'): """)
        if instruction.lower() == "j":
            newset = dataset1 | dataset2
            operation = "joining"
            break
        elif instruction.lower() == "i":
            newset = dataset1 & dataset2
            operation = "intersecting"
            break
        elif instruction.lower() == "e":
            while True:
                print("Select the order from which you want to exclude the data")
                order = input("""Exclude first file's data from second file (f).
                Exclude second file's data from first file (s): """)
                if order.lower() == 'f':
                    newset = dataset2 - dataset1
                elif order.lower() == 's':
                    newset = dataset1 - dataset2
                else:
                    print("Invalid option.")
                    continue
                break
            operation = "excluding"
            break
        elif instruction.lower() == 'u':
            newset = dataset1 ^ dataset2
            operation = "unique"
            break
        else:
            print("Invalid operation.")
            continue

    if operation == "intersecting" or operation == "unique":
        print("The " + operation + " values are: ")
        print(newset)
    else:
        print("After " + operation + " the data. The new set is: ")
        print(newset)
    print("Number of values on the first file: " + str(len(dataset1)))
    print("Number of values on the second file: " + str(len(dataset2)))
    print("Total values on the output: " + str(len(newset)))

    export_output = input("Want to export the output to a csv file? y/n: ")
    while True:
        if export_output.lower() == "y":
            filename = input("Enter the name of the new file: ")
            out_path = input(
                "Please enter the path (default is current folder): ")
            utils.exporter(dataset1, dataset2, newset, filename, out_path)
            break

        elif export_output.lower() == "n":
            break
        else:
            export_output = input("Please enter 'y' or 'n': ")
            continue


while True:
    main()
