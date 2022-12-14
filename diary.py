
from datetime import date
from participants import load_participants, update_participants
from rooms import load_rooms, update_room
from UI import ask_date, ask_option, print_status, print_diary, chose_appointment, search_by
from meeting import process_appointment, create_meeting, edit_meeting


def create_diary():
    diary_date = "-".join(str(date.today()).split("-")[::-1])
    participants = load_participants()
    rooms = load_rooms()
    diary = {"meetings": [],
             "date": diary_date,
             "participants": participants,
             "rooms": rooms}
    return diary


def save_diary(_diary):
    meeting_n = len(_diary["meetings"])
    if meeting_n:
        file_name_f = "{0}.Diary"
        meeting_f = "{0}\n{1}\n{2}\n"
        file = open(file_name_f.format(_diary["date"]), "w")
        file.write('\n')
        for idx, meeting in enumerate(_diary["meetings"]):
            file.write(str(meeting_f.format(meeting[0], meeting[1], meeting[2])))
            print(*meeting[3], file=file, sep=', ')
            if idx != meeting_n - 1:
                file.write("\n")
        file.close()
        return True
    return False


def read_meeting(_file_o):
    try:
        return False, float(_file_o.readline()[:-1]), float(_file_o.readline()[:-1]), \
                int(_file_o.readline()[:-1]), tuple(_file_o.readline()[:-1].split(", "))
    except ValueError:
        return True, 0.0, 0.0, 0, ()


def load_diary(_old_diary):
    file_name = ask_date()
    try:
        file = open(file_name + ".Diary", "r")
        diary = create_diary()
        while f := file.read(1):
            val_err, start_t, end_t, room_n, guests = read_meeting(file)
            if not val_err:
                result, meeting = process_appointment(diary["rooms"], diary["participants"], start_t, end_t, room_n, guests)
                if result:
                    add_meeting(diary, meeting)
                    continue
            raise ValueError
        else:
            _old_diary["date"], _old_diary["rooms"], _old_diary["participants"], _old_diary["meetings"] = \
                file_name, diary["rooms"], diary["participants"], diary["meetings"]
            return True
    except FileNotFoundError:
        print_status("File Not Found.", False)
    except ValueError:
        print_status("File Corrupted.", False)
    return False


def add_meeting(_diary, _meeting):
    for idx, meet in enumerate(_diary["meetings"]):
        if _meeting[0] < meet[0]:
            _diary["meetings"].insert(idx, _meeting)
            break
    else:
        _diary["meetings"].append(_meeting)
    update_room(_meeting[2], _diary["rooms"], _meeting[0], _meeting[1], True)
    update_participants(_meeting[3], _diary["participants"], _meeting[0], _meeting[1], True)


def create_appointment(_diary):
    result, meeting = create_meeting(_diary["rooms"], _diary["participants"])
    if result:
        add_meeting(_diary, meeting)
    print_status("Creating Appointment", result)


def search_appointment(_diary):
    status, result = "", False
    if _diary["meetings"]:
        param, key = search_by()
        meetings = []
        if param != 3:
            for meet in _diary["meetings"]:
                if meet[param] == key:
                    meetings.append(meet)
        else:
            for meet in _diary["meetings"]:
                if key in meet[param]:
                    meetings.append(meet)
        if meetings:
            print_diary("'" + str(key) + "'" + " Search Results", meetings)
            status, result = "Searching Appointment", True
        else:
            status = "No Results Found For " + "'" + str(key) + "'."
    else:
        status = "Diary is Empty."
    print_status(status, result)


def delete_appointment(_diary):
    print_diary(_diary["date"], _diary["meetings"])
    result = False
    if _diary["meetings"]:
        meeting = _diary["meetings"].pop(chose_appointment(len(_diary["meetings"])))
        update_room(meeting[2], _diary["rooms"], meeting[0], meeting[1], False)
        update_participants(meeting[3], _diary["participants"], meeting[0], meeting[1], False)
        result = True
    print_status("Deleting Appointment", result)


def save_diary_m(_diary):
    print_status("Saving Diary", save_diary(_diary))


def load_diary_m(_diary):
    print_status("Loading Diary", load_diary(_diary))


def print_diary_m(_diary):
    print_diary(_diary["date"], _diary["meetings"])


def edit_appointment(_diary):
    print_diary(_diary["date"], _diary["meetings"])
    if _diary["meetings"]:
        edit = chose_appointment(len(_diary["meetings"]))
        start_t, end_t, room, guests = _diary["meetings"][edit]
        status, new_meeting = edit_meeting(_diary["rooms"], _diary["participants"], start_t, end_t, room, guests)
        if status:
            if room != new_meeting[2] or start_t != new_meeting[0] or end_t != new_meeting[1]:
                update_room(room, _diary["rooms"], start_t, end_t, False)
                update_room(new_meeting[2], _diary["rooms"], new_meeting[0], new_meeting[1], True)
            if start_t != new_meeting[0] or end_t != new_meeting[1] or guests != new_meeting[3]:
                update_participants(guests, _diary["participants"], start_t, end_t, False)
                update_participants(new_meeting[3], _diary["participants"], new_meeting[0], new_meeting[1], True)
            _diary["meetings"][edit] = new_meeting
            _diary["meetings"].sort(key=lambda meeting: meeting[0])
    else:
        status = False
    print_status("Editing Appointment", status)


MENU = (("Create Appointment", 1, create_appointment),
        ("Search Appointment", 2, search_appointment),
        ("Delete Appointment", 3, delete_appointment),
        ("Edit Appointment", 4, edit_appointment),
        ("Save Diary", 5, save_diary_m),
        ("Load Diary", 6, load_diary_m),
        ("Print Diary", 7, print_diary_m),
        ("Exit", 0))


def manage_diary():
    diary = create_diary()
    option = ask_option(MENU)
    while option:
        MENU[option - 1][2](diary)
        option = ask_option(MENU)
