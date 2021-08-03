def clear_all_table():
    clear_table(table_info)
    clear_table(table_propertys)
    clear_table(table_processes)
    clear_table(table_services)
    clear_table(table_programs)
    clear_table(table_computers)
    clear_table(table_hardwares)


def clear_all_wigets():
    global selected_pc
    selected_pc = ""
    clear_listbox(computer_list)
    clear_all_table()
    entryes_clear()
    enryes_state(DISABLED)
    btn_save["state"] = DISABLED
    btn_delete["state"] = DISABLED


def online_click(event):
    global online
    if online == False or online == None:
        online = True
        clear_all_wigets()

        for pc in names_list:
            name = pc[0]
            computer_list.insert(END, name)


def offline_click(event):
    global online

    if online == True or online == None:
        online = False
        clear_all_wigets()

        sqlite_connect = sqlite3.connect("netspc.db")
        cursor = sqlite_connect.cursor()
        pcs_names_query = '''
                        SELECT pc_name
                        FROM computers;
                        '''
        cursor.execute(pcs_names_query)
        db_names = cursor.fetchall()
        names = list()
        for name in db_names:
            names.append(replace_dash_with_minus(name[0]))
        del db_names, name
        counter = len(names) - 1
        while counter != - 1:
            db_name = names[counter]
            for pc_name in names_list:
                if db_name == pc_name[0]:
                    names.pop(counter)
            counter = counter - 1

        offline = names
        del names
        for name in offline:
            computer_list.insert(END, name)


def get_entryes_list():
    entryes = [
        first_db_entry,
        second_db_entry,
        third_db_entry,
        fourth_db_entry,
        fifth_db_entry
    ]
    return entryes


def enryes_state(state):
    # принимает значение DISABLE или NORMAL
    # меняет статус эдитов на DISABLE или NORMAL
    entryes = get_entryes_list()
    for entry in entryes:
        entry["state"] = state


def entryes_clear():
    entryes = get_entryes_list()
    for entry in entryes:
        entry.delete(0, "end")


def all_tables():
    tables = [
        table_info,
        table_propertys,
        table_processes,
        table_services,
        table_programs,
        table_computers,
        table_hardwares
    ]
    return tables


def delete_selections_in_others_tables(table):
    # Снимает выделение со всех таблиц,
    # кроме той, что передана в функцию
    tables = all_tables()
    for counter, item in enumerate(tables):
        if item == table:
            tables.pop(counter)
    for item in tables:
        if len(item.selection()) > 0:
            item.selection_remove(item.selection()[0])


def table_computers_select(table):
    if len(table.selection()) != 0:
        global table_selected, old_id
        table_selected = 1
        enryes_state(NORMAL)
        entryes_clear()
        fourth_db_lable["text"] = ""
        fourth_db_entry["state"] = DISABLED
        btn_delete["state"] = DISABLED
        btn_save["state"] = NORMAL
        delete_selections_in_others_tables(table)
        for selection in table.selection():
            item = table.item(selection)
            inventory_number, date_buy, room = item["values"][0: 3]
            first_db_lable["text"] = "Id"
            first_db_entry.insert(0, inventory_number)
            old_id = inventory_number
            second_db_lable["text"] = "Дата покупки"
            second_db_entry.insert(0, date_buy)
            third_db_lable["text"] = "Кабинет"
            third_db_entry.insert(0, room)


def table_hardwares_select(table):
    if len(table.selection()) != 0:
        global table_selected
        table_selected = 2
        enryes_state(NORMAL)
        btn_save["state"] = NORMAL
        delete_selections_in_others_tables(table)
        entryes_clear()
        for selection in table.selection():
            item = table.item(selection)
            hardware, data_setting, repair, comment, id = item["values"][0: 5]
            first_db_lable["text"] = "Устройство"
            first_db_entry.insert(0, hardware)
            second_db_lable["text"] = "Дата установки"
            second_db_entry.insert(0, data_setting)
            third_db_lable["text"] = "Ремонт"
            third_db_entry.insert(0, repair)
            fourth_db_lable["text"] = "Коментарий"
            fourth_db_entry.insert(0, comment)
            fifth_db_entry.insert(0, id)

            if id == "None":
                btn_delete["state"] = DISABLED
            else:
                btn_delete["state"] = NORMAL


def sqlite_erorr(error):
    messagebox.showwarning("Ошибка при подключении к sqlite ", error)


def save(event):
    if event.widget.cget("state") == "normal":
        try:
            sqlite_connection = sqlite3.connect("netspc.db")
            cursor = sqlite_connection.cursor()
            pc_name = replace_minus_with_dash(selected_pc)
            if table_selected == 1:
                inventory_number = first_db_entry.get()
                date_buy = second_db_entry.get()
                room = third_db_entry.get()
                query = f'''
                    UPDATE computers
                    SET inventory_number={inventory_number},
                    date_buy='{date_buy}',
                    room='{room}',
                    pc_name='{pc_name}'
                    WHERE inventory_number={old_id};
                    '''
            elif table_selected == 2:
                hardware = first_db_entry.get()
                data_setting = second_db_entry.get()
                repair = third_db_entry.get()
                comment = fourth_db_entry.get()
                id = fifth_db_entry.get()
                if id == "None" or id == "":
                    query = f'''
                        INSERT INTO hardwares
                        (hardware,
                        data_setting,
                        repair,
                        comment,
                        pc_name)
                        VALUES (
                        '{hardware}',
                        '{data_setting}',
                        '{repair}',
                        '{comment}',
                        '{pc_name}');
                        '''
                else:
                    query = f'''
                        UPDATE hardwares
                        SET hardware='{hardware}',
                        data_setting='{data_setting}',
                        repair='{repair}',
                        comment='{comment}',
                        pc_name='{pc_name}'
                        WHERE id={id};
                        '''
            cursor.execute(query)
            sqlite_connection.commit()
            cursor.close()
        except sqlite3.Error as error:
            sqlite_erorr(error)
        finally:
            if (sqlite_connection):
                sqlite_connection.close()
                print("Соединение с SQLite закрыто")
        database_get_pc()


def delete(event):
    if event.widget.cget("state") == "normal":
        try:
            sqlite_connection = sqlite3.connect("netspc.db")
            cursor = sqlite_connection.cursor()
            if table_selected == 2:
                id = fifth_db_entry.get()
                if id != "None" or id != "":
                    query = f'''
                        DELETE FROM hardwares
                        WHERE id={id};
                        '''
            cursor.execute(query)
            sqlite_connection.commit()
            cursor.close()
        except sqlite3.Error as error:
            sqlite_erorr(error)
        finally:
            if (sqlite_connection):
                sqlite_connection.close()
                print("Соединение с SQLite закрыто")
        database_get_pc()


def name_select(event):
    global updated, selected_pc
    pc_name = chosen_name(computer_list)
    if select_pс(pc_name) or is_update(updated, pc_name):
        clear_all_table()

    if (select_pс(pc_name) or is_update(updated, pc_name)) and pc_name != "":
        client_pc = get_pc(pc_name)
        selected_pc = pc_name

        # информация о ПК
        for key, item in client_pc.items():
            table_info.insert("", END, values=(key, item))
            if key == "available_ram":
                del key, item
                break

        # свойства ПК
        table_propertys.insert("", END, values=(
            "Загрузка процессора", client_pc["cpu_usage"]))
        table_propertys.insert("", END, values=(
            "Загрузка памяти", client_pc["ram_usage"]))
        table_propertys.insert("", END, values=(
            "Загрузка диска", client_pc["disk_usage"]))

        # процессы
        for process in client_pc["processes"]:
            table_processes.insert("", END, values=(process))

        # службы
        for servise in client_pc["services"]:
            table_services.insert("", END, values=(servise))

        # программы
        for program in client_pc["programs"]:
            table_programs.insert("", END, values=(program))

        updated.update({pc_name: False})
        database_get_pc()


def thread_name_select(event):
    thread_name_select = Thread(
        target=name_select, args=[event], daemon=True)
    thread_name_select.start()


def thread_get_names_list():
    global names_list
    lock = Lock()
    lock.acquire()
    try:
        names_list = get_names_list(ip_addresses)
        if len(names_list) != 0:
            clear_listbox(computer_list)
            fill_listbox(computer_list, names_list)
            fill_tables()

    finally:
        lock.release()
    print(f"Names PC in my network {len(names_list)}: {str(names_list)}")


def thread_send_command(command, table):
    lock = Lock()
    lock.acquire
    thread_send = Thread(target=send_command(command, table), daemon=True)
    thread_send.start()
    lock.release()
